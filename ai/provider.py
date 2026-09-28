"""LLM provider abstraction for Cartify."""

import json
import os
import urllib.error
import urllib.request

from dotenv import load_dotenv

load_dotenv()


class AIProviderError(RuntimeError):
    pass


class OpenAIProvider:
    """Small dependency-free OpenAI Responses API client."""

    endpoint = "https://api.openai.com/v1/responses"

    def __init__(self):
        self.api_key = os.getenv("AI_API_KEY", "").strip()
        self.model = os.getenv("AI_MODEL", "gpt-5.6-luna").strip()
        self.timeout = int(os.getenv("AI_TIMEOUT_SECONDS", "45"))

    @property
    def configured(self):
        return bool(self.api_key)

    def generate(self, system_prompt, history, user_message, product_context=""):
        if not self.configured:
            raise AIProviderError(
                "AI_API_KEY is not configured. Add it to the Cartify .env file."
            )

        context_block = product_context or "No matching catalog records were retrieved."
        input_items = [
            {
                "role": "system",
                "content": [{"type": "input_text", "text": system_prompt}],
            }
        ]

        # Keep the request bounded. The service already maintains a larger local history.
        for item in history[-12:]:
            role = item.get("role")
            text = str(item.get("content", "")).strip()
            if role in {"user", "assistant"} and text:
                input_items.append(
                    {"role": role, "content": [{"type": "input_text", "text": text}]}
                )

        input_items.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            f"Current catalog context:\n{context_block}\n\n"
                            f"User request:\n{user_message}"
                        ),
                    }
                ],
            }
        )

        payload = json.dumps(
            {
                "model": self.model,
                "input": input_items,
                "store": False,
            }
        ).encode("utf-8")

        request = urllib.request.Request(
            self.endpoint,
            data=payload,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            try:
                detail = exc.read().decode("utf-8")
            except Exception:
                detail = ""
            raise AIProviderError(self._friendly_http_error(exc.code, detail)) from exc
        except urllib.error.URLError as exc:
            raise AIProviderError("I couldn't reach the AI service. Please check your network connection.") from exc
        except TimeoutError as exc:
            raise AIProviderError("The AI service took too long to respond. Please try again.") from exc
        except Exception as exc:
            raise AIProviderError("The AI service returned an unexpected response.") from exc

        text = self._extract_text(data)
        if not text:
            raise AIProviderError("The AI service returned an empty response.")
        return text.strip()

    @staticmethod
    def _extract_text(data):
        direct = data.get("output_text")
        if isinstance(direct, str) and direct.strip():
            return direct

        chunks = []
        for item in data.get("output", []) or []:
            for content in item.get("content", []) or []:
                text = content.get("text")
                if isinstance(text, str) and text.strip():
                    chunks.append(text)
        return "\n".join(chunks)

    @staticmethod
    def _friendly_http_error(status, detail):
        if status == 401:
            return "The AI API key was rejected. Check AI_API_KEY in your .env file."
        if status == 429:
            return "The AI service is rate-limited right now. Please try again shortly."
        if status in {500, 502, 503, 504}:
            return "The AI service is temporarily unavailable. Please try again shortly."
        return f"The AI service returned an error (HTTP {status})."


def create_provider():
    return OpenAIProvider()
