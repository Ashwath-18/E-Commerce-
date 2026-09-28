"""Robust conversation orchestration for Cartify AI.

This version keeps the assistant useful even when MongoDB or the external
AI provider is temporarily unavailable. It never lets a backend exception
escape to the UI as a generic "Something went wrong" message.
"""

import re
from dataclasses import dataclass, field

from ai.prompts import SYSTEM_PROMPT
from ai.provider import AIProviderError, create_provider
from ai.retrieval import find_by_context, format_products, get_product, retrieve_products


@dataclass
class ChatState:
    messages: list = field(default_factory=list)
    last_products: list = field(default_factory=list)


class ShoppingAssistant:
    def __init__(self):
        self.provider = create_provider()
        self.state = ChatState()

    def reset(self):
        self.state = ChatState()

    def ask(self, message):
        message = (message or "").strip()

        if not message:
            return {
                "message": "Please type a question or shopping request.",
                "products": [],
                "ai": False,
            }

        # Handle normal conversation before touching MongoDB. This means
        # "hello", "hi", "what can you do?" etc. still work if MongoDB is down.
        if self._is_greeting(message):
            reply, ai_used = self._generate_safely(
                message,
                products=[],
                extra_instruction=(
                    "This is a casual greeting. Reply naturally and briefly, "
                    "then mention that you can help search the Cartify catalog."
                ),
            )
            return self._finish(message, reply, [], ai_used)

        if self._is_capability_request(message):
            reply, ai_used = self._generate_safely(
                message,
                products=[],
                extra_instruction=(
                    "Explain briefly what this shopping assistant can do. "
                    "Mention catalog search, price/rating/brand/category filters, "
                    "comparisons and follow-up references."
                ),
            )
            return self._finish(message, reply, [], ai_used)

        # Resolve conversational references. If MongoDB is temporarily
        # unavailable, this block is protected and the assistant can still
        # attempt a normal LLM response.
        context_product = None
        try:
            context_product, _ = find_by_context(message, self.state.last_products)
        except Exception:
            context_product = None

        if self._is_order_request(message):
            reply = (
                "I can see that this project has order-related data, but the "
                "current login is an admin-only login rather than a customer "
                "account session. So I won't expose or guess a customer's "
                "personal order information."
            )
            return self._finish(message, reply, [], False)

        if self._is_cart_request(message):
            reply = (
                "The current Cartify project does not have a cart collection "
                "or cart service. I won't pretend that an item was added or "
                "removed. I can still help you find and compare the products."
            )
            return self._finish(message, reply, [], False)

        # Retrieve real catalog records when the request looks shopping-related.
        products = []
        retrieval_error = None
        try:
            products = self._retrieve_for_message(message, context_product)
        except Exception as exc:
            retrieval_error = exc
            products = []

        if not products and context_product and self._looks_like_detail_request(message):
            products = [context_product]

        context = self._build_context(products)

        # Give the real LLM the user's question plus only the relevant
        # catalog records. If the provider is unavailable, use a useful
        # deterministic fallback instead of exposing an exception.
        reply, ai_used = self._generate_safely(
            message,
            products,
            extra_instruction=(
                "Answer the user's request directly. Use the supplied catalog "
                "records when the request is about Cartify products. Never "
                "invent product facts. If the user asks for something that is "
                "not present in the catalog, say so clearly."
            ),
            context=context,
        )

        # If both MongoDB and the LLM failed, make the failure understandable
        # and actionable instead of showing a generic UI error.
        if retrieval_error is not None and not ai_used and not products:
            reply = (
                "I couldn't access the Cartify product catalog right now. "
                "Please make sure MongoDB is running at "
                "mongodb://localhost:27017/ and try again. "
                "Your question was received correctly."
            )

        return self._finish(message, reply, products, ai_used)

    def _generate_safely(self, message, products, extra_instruction="", context=None):
        if context is None:
            context = self._build_context(products)

        try:
            reply = self.provider.generate(
                SYSTEM_PROMPT + "\n\n" + extra_instruction,
                self.state.messages,
                message,
                context,
            )
            return reply.strip(), True
        except AIProviderError as exc:
            return self._fallback_reply(message, products, str(exc)), False
        except Exception as exc:
            # Never let provider/parser/network implementation details reach
            # the PySide UI as an unhandled exception.
            return self._fallback_reply(message, products, str(exc)), False

    def _retrieve_for_message(self, message, context_product):
        text = message.casefold()

        if context_product and any(
            k in text
            for k in (
                "details",
                "detail",
                "available",
                "stock",
                "price",
                "how much",
                "rating",
            )
        ):
            product_id = context_product.get("product_id")
            return [get_product(product_id) or context_product]

        if self.state.last_products and "cheaper" in text:
            prices = [
                float(p.get("final_price", 0) or 0)
                for p in self.state.last_products
                if p.get("final_price") is not None
            ]
            if prices:
                return self._price_relative(min(prices), cheaper=True)

        if self.state.last_products and re.search(
            r"\b(more expensive|costlier)\b", text
        ):
            prices = [
                float(p.get("final_price", 0) or 0)
                for p in self.state.last_products
                if p.get("final_price") is not None
            ]
            if prices:
                return self._price_relative(max(prices), cheaper=False)

        if self.state.last_products and re.search(
            r"\b(show|give) me more\b|\bmore options\b", text
        ):
            previous = self.state.last_products
            seed = previous[0] if previous else {}
            query = (
                f"{seed.get('category', '')} "
                f"{seed.get('subcategory', '')} "
                f"{seed.get('brand', '')}"
            )
            return retrieve_products(
                query,
                limit=8,
                exclude_ids=[p.get("product_id") for p in previous],
            )

        ids = re.findall(r"\bP\d{3,}\b", message, re.I)
        if ids:
            product = get_product(ids[0])
            return [product] if product else []

        if context_product and re.search(
            r"\b(this|that|it|same|similar)\b", text
        ):
            return [context_product]

        return retrieve_products(message, limit=8)

    @staticmethod
    def _price_relative(reference, cheaper=True):
        from config.mongodb import db

        operator = {"$lt": reference} if cheaper else {"$gt": reference}
        return list(
            db["Products"]
            .find({"final_price": operator}, {"_id": 0})
            .sort([("rating", -1), ("review_count", -1)])
            .limit(8)
        )

    @staticmethod
    def _looks_like_detail_request(message):
        return bool(
            re.search(
                r"\b(details?|specs?|information|available|stock|price|rating)\b",
                message.casefold(),
            )
        )

    @staticmethod
    def _is_order_request(message):
        return bool(
            re.search(
                r"\b(order|orders|shipment|shipped|delivery|delivered)\b",
                message.casefold(),
            )
        )

    @staticmethod
    def _is_cart_request(message):
        return bool(
            re.search(
                r"\bcart\b|\badd .*\bto cart\b|\bremove .*\bfrom cart\b",
                message.casefold(),
            )
        )

    @staticmethod
    def _is_greeting(message):
        text = message.casefold().strip()
        return bool(
            re.fullmatch(
                r"(hi|hello|hey|hii|hiii|good morning|good afternoon|good evening|"
                r"vanakkam|வணக்கம்)[!. ]*",
                text,
            )
        )

    @staticmethod
    def _is_capability_request(message):
        text = message.casefold()
        return bool(
            re.search(
                r"\b(what can you do|what do you do|help me|how can you help|"
                r"what are you capable of|capabilities)\b",
                text,
            )
        )

    @staticmethod
    def _build_context(products):
        if not products:
            return "No matching catalog records were retrieved."

        rows = format_products(products)
        lines = []

        for index, p in enumerate(rows, start=1):
            lines.append(
                f"{index}. {p['product_id']} | "
                f"brand={p['brand']} | "
                f"category={p['category']} | "
                f"subcategory={p['subcategory']} | "
                f"final_price=₹{p['final_price']} | "
                f"discount={p['discount']}% | "
                f"stock={p['stock']} | "
                f"rating={p['rating']} | "
                f"review_count={p['review_count']} | "
                f"seller_rating={p['seller_rating']}"
            )

        return "\n".join(lines)

    @staticmethod
    def _fallback_reply(message, products, error=""):
        text = message.casefold().strip()

        if re.search(r"\b(hello|hi|hey|hii|hiii)\b", text):
            return (
                "Hi! 👋 I'm Cartify AI. I can help you search the real Cartify "
                "catalog, filter products by price/rating/brand/category, "
                "compare products, and answer follow-up questions."
            )

        if "what can you help" in text or "what do you do" in text:
            return (
                "I can search the Cartify catalog, filter by price, rating, "
                "brand or category, compare the products we found, and keep "
                "track of products during this conversation."
            )

        if text in {"food", "foods"}:
            return (
                "I can help with products available in Cartify. The current "
                "catalog categories I can search are Sports, Electronics, "
                "Beauty, Home and Clothing. I don't see a Food category in "
                "the current catalog."
            )

        if not products:
            if "api" in error.lower() or "key" in error.lower():
                return (
                    "I understood your question, but the AI service is not "
                    "configured correctly yet. Check AI_API_KEY and AI_MODEL "
                    "in the project's .env file."
                )

            return (
                "I understood your request, but I couldn't find a matching "
                "product in the current Cartify catalog. Try a product name, "
                "brand, category, subcategory, product ID, or a price such as "
                "\"headphones under ₹5000\"."
            )

        lines = [
            "I found these real matches in the Cartify catalog:"
        ]

        for i, product in enumerate(products[:6], 1):
            lines.append(
                f"{i}. {product.get('product_id')} — "
                f"{product.get('brand')} / {product.get('subcategory')} — "
                f"₹{product.get('final_price')} — "
                f"rating {product.get('rating')} — "
                f"stock {product.get('stock')}"
            )

        return "\n".join(lines)

    def _finish(self, user_message, reply, products, ai_used):
        self.state.messages.append(
            {"role": "user", "content": user_message}
        )
        self.state.messages.append(
            {"role": "assistant", "content": reply}
        )

        # Keep only a bounded local conversation history.
        self.state.messages = self.state.messages[-24:]

        if products:
            self.state.last_products = products

        return {
            "message": reply,
            "products": format_products(products),
            "ai": ai_used,
        }
