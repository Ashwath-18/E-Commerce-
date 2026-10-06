"""
Cartify AI service.

ask() runs the "think -> look something up -> answer" loop:

  1. send the conversation + tool definitions to the language model
  2. if the model asks for tools, run them against MongoDB and loop
  3. stream the final answer back to the UI as it is written

Without an AI key (or if the AI service fails) it falls back to the offline
engine in ai/offline.py, which uses the same database tools.
"""

import json

from ai import offline, tools
from ai.prompts import build_system_prompt
from ai.provider import AIProviderError, create_provider

MAX_TOOL_ROUNDS = 5
HISTORY_LIMIT = 20
TOOL_RESULT_LIMIT = 7000


def _noop(*_args, **_kwargs):
    return None


class ShoppingAssistant:

    def __init__(self):
        self.provider = create_provider()
        self.history = []          # [{"role": "user"|"assistant", "content": str}]
        self.last_products = []    # products shown in the previous reply
        self._cancel = False
        self._hinted = False

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    @property
    def ai_enabled(self):
        return self.provider.configured

    def reset(self):
        self.history = []
        self.last_products = []
        self._hinted = False

    def cancel(self):
        """Ask a running ask() call to stop as soon as possible."""
        self._cancel = True

    def ask(self, message, on_text=None, on_reset=None, on_status=None):
        """
        Answer one user message. Returns {"message", "products", "mode"}.

        on_text(delta)  - called with each streamed piece of text
        on_reset()      - called when streamed text so far should be discarded
        on_status(text) - called with a short progress message ("Searching ...")
        """
        message = (message or "").strip()
        if not message:
            return {"message": "Ask me about products, prices, ratings or stock.", "products": [], "mode": "none"}

        self._cancel = False
        on_text = on_text or _noop
        on_reset = on_reset or _noop
        on_status = on_status or _noop

        notice = ""
        if self.provider.configured:
            try:
                result = self._ask_llm(message, on_text, on_reset, on_status)
                self._remember(message, result)
                return result
            except AIProviderError as exc:
                notice = f"> ⚠️ {exc} Showing a basic answer instead.\n\n"
        elif not self._hinted:
            self._hinted = True
            notice = (
                "> 💡 Basic mode: add `AI_API_KEY` to your `.env` file to turn on the full AI.\n\n"
            )

        on_reset()
        result = offline.answer(message, self.last_products)
        result["message"] = notice + result["message"]
        result["mode"] = "offline"
        self._remember(message, result)
        return result

    # ------------------------------------------------------------------
    # LLM loop
    # ------------------------------------------------------------------

    def _ask_llm(self, message, on_text, on_reset, on_status):
        messages = (
            [{"role": "system", "content": self._system_prompt()}]
            + self.history[-HISTORY_LIMIT:]
            + [{"role": "user", "content": message}]
        )

        use_tools = True
        tool_failures = 0
        shown = []
        final_text = ""

        for round_number in range(MAX_TOOL_ROUNDS + 1):
            if self._cancel:
                break

            offer_tools = tools.TOOLS if use_tools and round_number < MAX_TOOL_ROUNDS else None
            on_status("Thinking…")

            try:
                content, calls = self._one_round(messages, offer_tools, on_text)
            except AIProviderError as exc:
                if exc.tool_failure and tool_failures < 2:
                    tool_failures += 1
                    on_reset()
                    if tool_failures == 2:
                        # The model can't do tool calls: ground it with offline data instead.
                        use_tools = False
                        context = offline.answer(message, self.last_products)
                        messages.append(
                            {
                                "role": "system",
                                "content": "Tools are unavailable. Use ONLY this retrieved catalog data "
                                           "to answer, and don't invent anything else:\n" + context["message"],
                            }
                        )
                        if context["products"]:
                            shown = list(context["products"])
                    continue
                raise

            if not calls:
                final_text = content
                break

            # The model wants data: discard any preamble text and run the tools.
            on_reset()
            messages.append(
                {
                    "role": "assistant",
                    "content": content or None,
                    "tool_calls": [
                        {
                            "id": c["id"],
                            "type": "function",
                            "function": {"name": c["name"], "arguments": c["arguments"]},
                        }
                        for c in calls
                    ],
                }
            )
            for call in calls:
                if self._cancel:
                    break
                on_status(tools.STATUS_TEXT.get(call["name"], "Looking that up…"))
                try:
                    arguments = json.loads(call["arguments"] or "{}")
                except ValueError:
                    arguments = {}
                result = tools.run_tool(call["name"], arguments)

                if isinstance(result, dict) and result.get("products"):
                    shown = list(result["products"])

                payload = json.dumps(result, ensure_ascii=False, default=str)
                if len(payload) > TOOL_RESULT_LIMIT:
                    payload = payload[:TOOL_RESULT_LIMIT] + '…(truncated)"}'
                messages.append(
                    {"role": "tool", "tool_call_id": call["id"], "content": payload}
                )

        if self._cancel and not final_text:
            final_text = "Stopped."
        if not final_text:
            final_text = "I couldn't put an answer together. Please try rephrasing your question."

        unique, seen = [], set()
        for product in shown:
            if product.get("product_id") not in seen:
                seen.add(product.get("product_id"))
                unique.append(product)

        return {"message": final_text, "products": unique[:8], "mode": "ai"}

    def _one_round(self, messages, offer_tools, on_text):
        content, calls = "", []
        for kind, payload in self.provider.stream_chat(
            messages, offer_tools, cancel=lambda: self._cancel
        ):
            if kind == "text":
                on_text(payload)
            else:
                content, calls = payload["content"], payload["tool_calls"]
        return content, calls

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _system_prompt(self):
        overview = tools.catalog_overview()
        lines = []
        for category, subs in sorted(overview.get("categories", {}).items()):
            lines.append(f"- {category}: {', '.join(subs) if subs else '(no subcategories)'}")
        text = "Categories and subcategories:\n" + "\n".join(lines) if lines else ""
        if overview.get("brands"):
            text += "\nBrands: " + ", ".join(overview["brands"])

        previous = "\n".join(
            f"{i}. {p.get('product_id')} — {p.get('brand')} {p.get('subcategory')}, "
            f"₹{p.get('final_price')}, rating {p.get('rating')}"
            for i, p in enumerate(self.last_products, 1)
        )
        return build_system_prompt(text, previous)

    def _remember(self, message, result):
        self.history.append({"role": "user", "content": message})
        self.history.append({"role": "assistant", "content": result["message"]})
        self.history = self.history[-HISTORY_LIMIT:]
        if result.get("products"):
            self.last_products = list(result["products"])
