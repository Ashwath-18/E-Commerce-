"""
LLM provider layer for Cartify AI.

Speaks the OpenAI-compatible "Chat Completions" protocol with streaming and
tool calling, so ONE client works with many services. Pick one in .env:

    AI_PROVIDER = groq        (default - free tier, no credit card)
                  openai | gemini | openrouter | ollama | custom
    AI_API_KEY  = <your key>  (not needed for ollama)
    AI_MODEL    = <model>     (optional - sensible default per provider)
    AI_BASE_URL = <url>       (optional - only for "custom")

No third-party packages are needed (standard library only).
"""

import json
import os
import time
import urllib.error
import urllib.request

from dotenv import load_dotenv

load_dotenv()


class AIProviderError(RuntimeError):
    """Raised for any provider problem. Messages are safe to show to users."""

    def __init__(self, message, tool_failure=False):
        super().__init__(message)
        # True when the model produced a broken / unsupported tool call.
        self.tool_failure = tool_failure


PRESETS = {
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "model": "llama-3.3-70b-versatile",
        "key_env": "GROQ_API_KEY",
        "needs_key": True,
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
        "key_env": "OPENAI_API_KEY",
        "needs_key": True,
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "model": "gemini-2.0-flash",
        "key_env": "GEMINI_API_KEY",
        "needs_key": True,
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "model": "meta-llama/llama-3.3-70b-instruct",
        "key_env": "OPENROUTER_API_KEY",
        "needs_key": True,
    },
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "model": "llama3.1",
        "key_env": None,
        "needs_key": False,
    },
    "custom": {
        "base_url": "",
        "model": "",
        "key_env": None,
        "needs_key": False,
    },
}


def _detect_provider(api_key):
    """Guess the provider from the key prefix when AI_PROVIDER isn't set."""
    if api_key.startswith("gsk_"):
        return "groq"
    if api_key.startswith("sk-or-"):
        return "openrouter"
    if api_key.startswith("sk-"):
        return "openai"
    if api_key.startswith("AIza"):
        return "gemini"
    return "groq"


class ChatProvider:

    def __init__(self):
        configured_key = os.getenv("AI_API_KEY", "").strip()
        name = os.getenv("AI_PROVIDER", "").strip().lower()
        if not name:
            name = _detect_provider(configured_key)
        if name not in PRESETS:
            name = "custom"

        preset = PRESETS[name]
        self.name = name
        self.preset = preset
        self.base_url = (os.getenv("AI_BASE_URL") or preset["base_url"]).rstrip("/")
        self.model = (os.getenv("AI_MODEL") or preset["model"]).strip()

        key = configured_key
        if not key and preset.get("key_env"):
            key = os.getenv(preset["key_env"], "").strip()
        self.api_key = key

        self.timeout = int(os.getenv("AI_TIMEOUT_SECONDS", "60"))
        self.temperature = float(os.getenv("AI_TEMPERATURE", "0.3"))

    # ------------------------------------------------------------------

    @property
    def configured(self):
        if not self.base_url or not self.model:
            return False
        return bool(self.api_key) or not self.preset["needs_key"]

    @property
    def label(self):
        return f"{self.name} · {self.model}"

    # ------------------------------------------------------------------

    def stream_chat(self, messages, tools=None, cancel=None):
        """
        Yield ("text", delta) for every piece of generated text, then a final
        ("done", {"content": str, "tool_calls": [{id, name, arguments}]}).
        `cancel` is an optional callable; when it returns True we stop early.
        """
        if not self.configured:
            raise AIProviderError(
                "The AI service is not configured. Add AI_API_KEY to the .env file."
            )

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "temperature": self.temperature,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        response = self._open(payload)

        content_parts = []
        calls = {}

        try:
            for raw in response:
                if cancel and cancel():
                    break
                line = raw.decode("utf-8", errors="replace").strip()
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                except ValueError:
                    continue

                choices = chunk.get("choices") or []
                if not choices:
                    continue
                delta = choices[0].get("delta") or {}

                text = delta.get("content")
                if text:
                    content_parts.append(text)
                    yield ("text", text)

                for call in delta.get("tool_calls") or []:
                    slot = calls.setdefault(
                        call.get("index", 0), {"id": "", "name": "", "arguments": ""}
                    )
                    if call.get("id"):
                        slot["id"] = call["id"]
                    function = call.get("function") or {}
                    if function.get("name"):
                        slot["name"] += function["name"]
                    if function.get("arguments"):
                        slot["arguments"] += function["arguments"]
        except (TimeoutError, OSError) as exc:
            if not content_parts and not calls:
                raise AIProviderError(
                    "The AI service took too long to respond. Please try again."
                ) from exc
        finally:
            try:
                response.close()
            except Exception:
                pass

        tool_calls = []
        for position, key in enumerate(sorted(calls)):
            slot = calls[key]
            if not slot["name"]:
                continue
            tool_calls.append(
                {
                    "id": slot["id"] or f"call_{position}",
                    "name": slot["name"],
                    "arguments": slot["arguments"] or "{}",
                }
            )

        yield ("done", {"content": "".join(content_parts), "tool_calls": tool_calls})

    # ------------------------------------------------------------------

    def _open(self, payload):
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        for attempt in range(2):
            request = urllib.request.Request(
                f"{self.base_url}/chat/completions",
                data=body,
                method="POST",
                headers=headers,
            )
            try:
                return urllib.request.urlopen(request, timeout=self.timeout)
            except urllib.error.HTTPError as exc:
                try:
                    detail = exc.read().decode("utf-8", errors="replace")
                except Exception:
                    detail = ""

                # One polite retry on rate limits.
                if exc.code == 429 and attempt == 0:
                    wait = 2.0
                    try:
                        wait = min(float(exc.headers.get("retry-after", "2")), 6.0)
                    except (TypeError, ValueError):
                        pass
                    time.sleep(wait)
                    continue

                raise self._http_error(exc.code, detail) from exc
            except urllib.error.URLError as exc:
                raise AIProviderError(
                    "I couldn't reach the AI service. Please check your internet connection."
                ) from exc
            except TimeoutError as exc:
                raise AIProviderError(
                    "The AI service took too long to respond. Please try again."
                ) from exc

        raise AIProviderError("The AI service is rate-limited right now. Please try again shortly.")

    def _http_error(self, status, detail):
        lowered = detail.lower()

        if status in (401, 403):
            return AIProviderError(
                "The AI key was rejected. Check AI_API_KEY in your .env file."
            )
        if status == 404:
            return AIProviderError(
                f"The AI service doesn't know the model '{self.model}'. "
                "Check AI_MODEL in your .env file."
            )
        if status == 429:
            return AIProviderError(
                "The AI service is rate-limited right now. Please try again shortly."
            )
        if status == 400 and (
            "tool_use_failed" in lowered
            or "failed_generation" in lowered
            or "tool" in lowered and "support" in lowered
        ):
            return AIProviderError("The AI produced an invalid tool call.", tool_failure=True)
        if status >= 500:
            return AIProviderError(
                "The AI service is temporarily unavailable. Please try again shortly."
            )
        return AIProviderError(f"The AI service returned an error (HTTP {status}).")


def create_provider():
    return ChatProvider()
