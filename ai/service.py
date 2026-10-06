"""Local-only assistant service for the Cartify database.

This module deliberately does not import an LLM provider or make network
requests.  Every response is produced by :mod:`ai.local_engine`, which
parses supported English request patterns and runs safe MongoDB queries.
"""

from ai.local_engine import LocalQueryEngine


def _noop(*_args, **_kwargs):
    return None


class ShoppingAssistant:
    """Compatibility wrapper used by the chat page."""

    def __init__(self):
        self.engine = LocalQueryEngine()
        self.history = []
        self.last_products = []
        self._cancel = False

    @property
    def ai_enabled(self):
        """Kept for existing UI callers; this assistant is always local."""
        return False

    @property
    def mode_label(self):
        return "Local · MongoDB"

    def reset(self):
        self.history = []
        self.last_products = []
        self.engine.reset()

    def cancel(self):
        self._cancel = True

    def ask(self, message, on_text=None, on_reset=None, on_status=None):
        """Run one local request without contacting an external AI service."""
        message = (message or "").strip()
        if not message:
            return {
                "message": "Enter an English database request, such as `seller rating <2`.",
                "products": [],
                "mode": "local",
            }

        self._cancel = False
        on_text = on_text or _noop
        on_reset = on_reset or _noop
        on_status = on_status or _noop
        on_status("Reading your database request…")

        if self._cancel:
            return {"message": "Stopped.", "products": [], "mode": "local"}

        result = self.engine.answer(message, self.last_products)
        result["mode"] = "local"
        on_reset()
        if not self._cancel:
            on_text(result["message"])
        else:
            result = {"message": "Stopped.", "products": [], "mode": "local"}

        self._remember(message, result)
        return result

    def _remember(self, message, result):
        self.history.extend([
            {"role": "user", "content": message},
            {"role": "assistant", "content": result["message"]},
        ])
        self.history = self.history[-20:]
        if result.get("products"):
            self.last_products = list(result["products"])
