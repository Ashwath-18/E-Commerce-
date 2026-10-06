"""Deterministic English-to-MongoDB query engine used by the Cartify chat.

This is intentionally *not* a language model.  It recognises supported
English query patterns, normalises harmless spacing/grammar variation, and
maps them to fixed MongoDB filters and aggregation pipelines.  It never
executes user-provided MongoDB, Python, or shell code.

Write operations are staged first and require a separate ``CONFIRM`` reply.
"""

from __future__ import annotations

import html
import re
from datetime import datetime

from config.mongodb import db


MAX_RESULTS = 20
ALLOWED_INPUT = re.compile(r"^[A-Za-z0-9\s.,:;?()<>+=_\-/%&*!]+$")
PRODUCT_ID = re.compile(r"\bP\s*(\d{3,})\b", re.IGNORECASE)
USER_ID = re.compile(r"\bU\s*(\d{3,})\b", re.IGNORECASE)
SELLER_ID = re.compile(r"\bS\s*(\d{3,})\b", re.IGNORECASE)

COLLECTION_NAMES = {
    "product": "Products",
    "user": "Users",
    "seller": "Sellers",
    "order": "Orders",
    "payment": "Payments",
    "shipping": "Shipping",
    "review": "Reviews",
    "inventory": "Inventory",
    "return": "Returns",
    "order item": "OrderItems",
}

COMPARISON_WORDS = {
    "<": "$lt",
    "<=": "$lte",
    ">": "$gt",
    ">=": "$gte",
    "=": "$eq",
    "less than": "$lt",
    "below": "$lt",
    "under": "$lt",
    "at most": "$lte",
    "no more than": "$lte",
    "greater than": "$gt",
    "more than": "$gt",
    "above": "$gt",
    "over": "$gt",
    "at least": "$gte",
    "no less than": "$gte",
    "equal to": "$eq",
    "equals": "$eq",
    "is": "$eq",
}

PRODUCT_ASSIGNMENTS = {
    "product id": "product_id",
    "product_id": "product_id",
    "category": "category",
    "subcategory": "subcategory",
    "sub category": "subcategory",
    "brand": "brand",
    "price": "price",
    "discount": "discount",
    "final price": "final_price",
    "final_price": "final_price",
    "stock": "stock",
    "rating": "rating",
    "review count": "review_count",
    "review_count": "review_count",
}

# Explicit, whitelisted fields used by the reusable local query grammar.
# User text is mapped through these names; it is never used as a MongoDB key.
ENTITY_FIELDS = {
    "product": {
        "price": "final_price", "final price": "final_price", "rating": "rating",
        "stock": "stock", "discount": "discount", "review count": "review_count",
    },
    "seller": {"rating": "seller_rating", "seller rating": "seller_rating"},
    "order": {
        "shipping days": "shipping_time_days", "shipping time": "shipping_time_days",
        "delivery status": "delivery_status", "payment method": "payment_method",
    },
    "shipping": {
        "shipping days": "shipping_time_days", "shipping time": "shipping_time_days",
        "delivery status": "delivery_status",
    },
    "review": {"rating": "rating", "review count": "review_count"},
}

GROUPS = {
    "brand": "brand", "category": "category", "subcategory": "subcategory",
    "payment method": "payment_method", "delivery status": "delivery_status",
    "location": "location", "user": "user_id", "user id": "user_id",
    "product": "product_id", "product id": "product_id", "purchase date": "purchase_date",
}


def _number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _money(value):
    value = _number(value)
    return f"₹{value:,.2f}" if value is not None else "₹—"


def _safe_id(pattern, text, prefix):
    match = pattern.search(text)
    return f"{prefix}{match.group(1)}" if match else None


def _plural(word):
    return f"{word}s?"


class LocalQueryEngine:
    """A small, deliberately transparent query language for Cartify data."""

    def __init__(self):
        self.pending_action = None

    def reset(self):
        self.pending_action = None

    # ------------------------------------------------------------------
    # public entrypoint
    # ------------------------------------------------------------------

    def answer(self, raw_message, last_products=None):
        valid, message = self._normalise(raw_message)
        if not valid:
            return {"message": message, "products": []}

        lowered = message.lower()
        try:
            if lowered in {"confirm", "confirm action", "yes confirm"}:
                return self._confirm_action()
            if lowered in {"cancel", "cancel action", "no cancel"}:
                self.pending_action = None
                return {"message": "Pending create/delete action cancelled.", "products": []}

            if self._is_help_request(lowered):
                return self._help()

            mutation = self._stage_mutation(message, lowered)
            if mutation is not None:
                return mutation

            product_id = _safe_id(PRODUCT_ID, message, "P")
            if product_id and self._asks_product_order_count(lowered):
                return self._product_order_count(product_id)

            comparison = self._comparison_query(message, lowered)
            if comparison is not None:
                return comparison

            pattern = self._pattern_query(message, lowered)
            if pattern is not None:
                return pattern

            if self._is_summary_request(lowered):
                return self._collection_summary(lowered)

            if self._is_most_ordered_query(lowered):
                return self._most_ordered(lowered)

            if self._is_shipping_average_query(lowered):
                return self._shipping_average()

            date_query = self._orders_on_date(lowered)
            if date_query is not None:
                return date_query

            status_query = self._order_status_count(lowered)
            if status_query is not None:
                return status_query

            grouped = self._generic_group_query(message, lowered)
            if grouped is not None:
                return grouped

            top_products = self._top_products(message, lowered)
            if top_products is not None:
                return top_products

            generic = self._generic_collection_query(message, lowered)
            if generic is not None:
                return generic

            collection_count = self._collection_count(lowered)
            if collection_count is not None:
                return collection_count

            aggregate = self._product_aggregate(message, lowered)
            if aggregate is not None:
                return aggregate

            if product_id:
                return self._product_details(product_id)

            # The existing offline search is also local and covers ordinary
            # catalog phrases such as "cheap Nike phones under 5000".
            from ai import offline

            return offline.answer(message, last_products or [])
        except Exception as exc:
            return {
                "message": (
                    "**Request could not be completed**\n\n"
                    "The requested database operation is unavailable at the moment. Please review the request and try again."
                ),
                "products": [],
            }

    # ------------------------------------------------------------------
    # input and help
    # ------------------------------------------------------------------

    @staticmethod
    def _normalise(raw_message):
        text = html.unescape(str(raw_message or "")).strip()
        text = text.replace("–", "-").replace("—", "-")
        if not text:
            return False, "Enter an English database request."
        if len(text) > 500:
            return False, "Keep a request to 500 characters or fewer."
        if not ALLOWED_INPUT.fullmatch(text):
            return False, (
                "Use English letters, numbers, spaces, and simple symbols only "
                "(`- ( ) < > ? + _ = . , : / % & * !`)."
            )

        text = re.sub(r"\s+", " ", text)
        compact_terms = {
            "seller rating": "seller rating", "product id": "product id", "user id": "user id",
            "seller id": "seller id", "final price": "final price", "review count": "review count",
            "how many": "how many", "most ordered": "most ordered",
            "average shipping": "average shipping", "shipping days": "shipping days",
            "delivery status": "delivery status", "returned orders": "returned orders",
        }
        for spaced, replacement in compact_terms.items():
            compact = re.escape(spaced.replace(" ", ""))
            flexible = r"\s*".join(re.escape(word) for word in spaced.split())
            text = re.sub(compact, replacement, text, flags=re.IGNORECASE)
            text = re.sub(flexible, replacement, text, flags=re.IGNORECASE)
        text = re.sub(r"\b([PUSpus])\s+(\d{3,})\b", r"\1\2", text)
        text = re.sub(r"\s*(<=|>=|<|>|=)\s*", r"\1", text)
        return True, text

    @staticmethod
    def _is_help_request(text):
        return text in {"help", "examples", "what can you do", "what do you do"} or "supported queries" in text

    @staticmethod
    def _help():
        return {
            "message": (
                "**Cartify Local Database Assistant**\n\n"
                "I use only Python and MongoDB—no online AI or API. I understand these request types:\n"
                "- `top 5 products by price`, `lowest 3 products by stock`\n"
                "- `seller rating <2`, `products with rating greater than 4`\n"
                "- `how many returned orders`, `number of delayed orders`\n"
                "- `how many times was P13100 ordered`, `orders on 2025-01-15`\n"
                "- `most ordered brand`, `top 3 ordered categories`\n"
                "- `average shipping days`, `seller summary`, `product summary`\n"
                "- `brand like Nike`, `category contains Sport`\n"
                "- `create user U999999` or `delete product P999999`\n\n"
                "These are query patterns, not fixed sentences: you can combine a count, average, "
                "minimum, maximum, total, top, or lowest operation with a collection, field, filter, "
                "or grouping—for example `average price by category` or `count returned orders by payment method`.\n\n"
                "For a new product use named values, for example:\n"
                "`create product P999999 category=Sports subcategory=Cycling brand=Nike price=1000 discount=10 stock=5 rating=4 review_count=0`\n\n"
                "Create and delete operations are previewed first. Reply **CONFIRM** to execute or **CANCEL** to stop."
            ),
            "products": [],
        }

    # ------------------------------------------------------------------
    # safe create and delete commands
    # ------------------------------------------------------------------

    def _stage_mutation(self, message, lowered):
        action_match = re.match(r"^(create|add|delete|remove)\b", lowered)
        if not action_match:
            return None
        action = action_match.group(1)
        entity = self._mutation_entity(lowered)
        if not entity:
            return {
                "message": "For a write action, specify `product`, `user`, or `seller`.",
                "products": [],
            }

        if action in {"delete", "remove"}:
            record_id = self._id_for_entity(entity, message)
            if not record_id:
                return {
                    "message": f"Include the {entity} ID to delete, for example `delete {entity} {entity[0].upper()}123456`.",
                    "products": [],
                }
            self.pending_action = {"kind": "delete", "entity": entity, "id": record_id}
            return {
                "message": (
                    f"**Delete preview**\n\nI am ready to delete {entity} **{record_id}**. "
                    "This may be blocked if related records exist. Reply **CONFIRM** to delete it, or **CANCEL** to keep it."
                ),
                "products": [],
            }

        if entity == "user":
            user_id = self._id_for_entity("user", message)
            if not user_id:
                return {"message": "Include a user ID, for example `create user U999999`.", "products": []}
            self.pending_action = {"kind": "create", "entity": "user", "values": {"user_id": user_id}}
            return self._preview_create("user", f"User ID: **{user_id}**")

        if entity == "seller":
            seller_id = self._id_for_entity("seller", message)
            fields = self._parse_assignments(message, {"seller rating": "seller_rating", "seller_rating": "seller_rating"})
            rating = _number(fields.get("seller_rating"))
            if not seller_id or rating is None:
                return {
                    "message": "Use `create seller S999999 seller_rating=4.5`.",
                    "products": [],
                }
            if not 0 <= rating <= 5:
                return {"message": "Seller rating must be from 0 to 5.", "products": []}
            self.pending_action = {
                "kind": "create", "entity": "seller",
                "values": {"seller_id": seller_id, "seller_rating": rating},
            }
            return self._preview_create("seller", f"Seller ID: **{seller_id}** · Rating: **{rating:g}**")

        values = self._product_values(message)
        if isinstance(values, str):
            return {"message": values, "products": []}
        self.pending_action = {"kind": "create", "entity": "product", "values": values}
        return self._preview_create(
            "product",
            " · ".join([
                f"ID: **{values['product_id']}**",
                f"Category: **{values['category']}**",
                f"Brand: **{values['brand']}**",
                f"Final price: **{_money(values['final_price'])}**",
                f"Stock: **{values['stock']}**",
            ]),
        )

    @staticmethod
    def _mutation_entity(text):
        for entity in ("product", "user", "seller"):
            if re.search(rf"\b{_plural(entity)}\b", text):
                return entity
        return None

    @staticmethod
    def _id_for_entity(entity, text):
        patterns = {"product": (PRODUCT_ID, "P"), "user": (USER_ID, "U"), "seller": (SELLER_ID, "S")}
        if entity not in patterns:
            return None
        pattern, prefix = patterns[entity]
        return _safe_id(pattern, text, prefix)

    @staticmethod
    def _preview_create(entity, details):
        return {
            "message": (
                f"**Create preview**\n\n{details}\n\n"
                f"Reply **CONFIRM** to create this {entity}, or **CANCEL** to stop."
            ),
            "products": [],
        }

    @staticmethod
    def _parse_assignments(message, aliases):
        alternatives = "|".join(re.escape(item) for item in sorted(aliases, key=len, reverse=True))
        pattern = re.compile(rf"\b({alternatives})\s*=\s*", re.IGNORECASE)
        matches = list(pattern.finditer(message))
        values = {}
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(message)
            raw_value = message[match.end():end].strip(" ,")
            values[aliases[match.group(1).lower()]] = " ".join(raw_value.split())
        return values

    def _product_values(self, message):
        values = self._parse_assignments(message, PRODUCT_ASSIGNMENTS)
        values.setdefault("product_id", self._id_for_entity("product", message))
        required = ("product_id", "category", "subcategory", "brand", "price", "stock", "rating")
        missing = [field.replace("_", " ") for field in required if not values.get(field)]
        if missing:
            return "Missing product values: **" + ", ".join(missing) + ". Use `help` to see the create-product format."

        numeric = {"price": float, "discount": float, "final_price": float, "stock": int, "rating": float, "review_count": int}
        for field, converter in numeric.items():
            if field not in values or values[field] == "":
                continue
            number = _number(values[field])
            if number is None or (converter is int and not number.is_integer()):
                return f"`{field.replace('_', ' ')}` must be a valid number."
            values[field] = converter(number)

        values.setdefault("discount", 0.0)
        values.setdefault("review_count", 0)
        values.setdefault("final_price", round(values["price"] * (1 - values["discount"] / 100), 2))
        if values["price"] < 0 or values["final_price"] < 0 or values["stock"] < 0:
            return "Price, final price, and stock cannot be negative."
        if not 0 <= values["discount"] <= 100:
            return "Discount must be from 0 to 100."
        if not 0 <= values["rating"] <= 5:
            return "Rating must be from 0 to 5."
        return values

    def _confirm_action(self):
        if not self.pending_action:
            return {"message": "There is no pending create/delete action to confirm.", "products": []}

        action = self.pending_action
        self.pending_action = None
        try:
            if action["kind"] == "delete":
                from crud import delete

                deleted = getattr(delete, f"delete_{action['entity']}")(action["id"])
                if not deleted:
                    return {"message": f"No {action['entity']} with ID **{action['id']}** was found.", "products": []}
                return {"message": f"Deleted {action['entity']} **{action['id']}** successfully.", "products": []}

            from crud import create

            getattr(create, f"create_{action['entity']}")(**action["values"])
            record_id = action["values"].get(f"{action['entity']}_id")
            return {"message": f"Created {action['entity']} **{record_id}** successfully.", "products": []}
        except Exception as exc:
            return {"message": f"The action was not completed: {exc}", "products": []}

    # ------------------------------------------------------------------
    # read queries: summaries, counts and comparisons
    # ------------------------------------------------------------------

    @staticmethod
    def _asks_product_order_count(text):
        return bool(re.search(r"\b(how many|number of|count|times|ordered|orders?)\b", text))

    @staticmethod
    def _product_order_count(product_id):
        query = {"product_id": {"$regex": f"^{re.escape(product_id)}$", "$options": "i"}}
        total = db["Orders"].count_documents(query)
        returned = db["Orders"].count_documents({**query, "is_returned": True})
        return {
            "message": f"Product **{product_id}** has been ordered **{total:,}** time(s), including **{returned:,}** returned order(s).",
            "products": [],
        }

    def _comparison_query(self, message, text):
        field_info = self._comparison_field(text)
        comparison = self._extract_comparison(text, field_info[0] if field_info else None)
        if not field_info or comparison is None:
            return None

        field, display = field_info
        mongo_operator, amount, symbol = comparison
        entity = "seller" if "seller" in text else "product"
        if entity == "seller":
            if field != "seller_rating":
                return None
            rows = list(db["Sellers"].find({field: {mongo_operator: amount}}, {"_id": 0}).sort(field, 1).limit(MAX_RESULTS))
            total = db["Sellers"].count_documents({field: {mongo_operator: amount}})
            lines = [f"**Sellers with {display} {symbol} {amount:g}** — {total:,} match(es):"]
            lines += [f"- {row.get('seller_id', 'N/A')}: **{row.get('seller_rating', '—')}**" for row in rows]
            return {"message": "\n".join(lines), "products": []}

        if field == "seller_rating":
            return None
        query = {field: {mongo_operator: amount}}
        rows = self._find_products(query, [(field, 1)], MAX_RESULTS)
        total = self._product_count(query)
        lines = [f"**Products with {display} {symbol} {amount:g}** — {total:,} match(es):"]
        lines += [self._product_line(index, row) for index, row in enumerate(rows, 1)]
        return {"message": "\n".join(lines), "products": rows}

    @staticmethod
    def _comparison_field(text):
        fields = (
            ("seller rating", "seller_rating", "seller rating"),
            ("final price", "final_price", "final price"),
            ("price", "final_price", "price"),
            ("product rating", "rating", "rating"),
            ("rating", "seller_rating" if "seller" in text else "rating", "rating"),
            ("stock", "stock", "stock"),
            ("review count", "review_count", "review count"),
        )
        for phrase, field, display in fields:
            if re.search(rf"\b{re.escape(phrase)}\b", text):
                return field, display
        return None

    @staticmethod
    def _extract_comparison(text, field=None):
        if not field:
            return None
        field_name = re.escape(field.replace("_", " "))
        generic = r"(?:seller\s+)?(?:final\s+)?(?:product\s+)?(?:rating|price|stock|review\s+count)"
        match = re.search(rf"{generic}\s*(<=|>=|<|>|=)\s*(\d+(?:\.\d+)?)", text)
        if not match:
            words = "|".join(re.escape(word) for word in sorted(COMPARISON_WORDS, key=len, reverse=True) if word not in {"<", "<=", ">", ">=", "="})
            match = re.search(rf"{generic}\s+(?:is\s+)?({words})\s+(\d+(?:\.\d+)?)", text)
        if not match:
            return None
        operator = match.group(1).lower()
        amount = float(match.group(2))
        return COMPARISON_WORDS[operator], amount, {"$lt": "<", "$lte": "<=", "$gt": ">", "$gte": ">=", "$eq": "="}[COMPARISON_WORDS[operator]]

    def _pattern_query(self, message, text):
        pattern = re.search(
            r"\b(product id|brand|category|subcategory|user id|seller id)\s+(?:is\s+)?(?:like|contains|matches)\s+([A-Za-z0-9_%-]+)",
            text,
        )
        if not pattern:
            return None
        label, value = pattern.groups()
        fields = {
            "product id": ("Products", "product_id"), "brand": ("Products", "brand"),
            "category": ("Products", "category"), "subcategory": ("Products", "subcategory"),
            "user id": ("Users", "user_id"), "seller id": ("Sellers", "seller_id"),
        }
        collection, field = fields[label]
        mongo_pattern = ".*".join(re.escape(part) for part in value.split("%"))
        query = {field: {"$regex": mongo_pattern, "$options": "i"}}
        if collection == "Products":
            rows = self._find_products(query, [("rating", -1)], MAX_RESULTS)
            total = self._product_count(query)
            lines = [f"**Products where {label} matches `{value}`** — {total:,} match(es):"]
            lines += [self._product_line(index, row) for index, row in enumerate(rows, 1)]
            return {"message": "\n".join(lines), "products": rows}

        rows = list(db[collection].find(query, {"_id": 0}).limit(MAX_RESULTS))
        total = db[collection].count_documents(query)
        lines = [f"**{collection} where {label} matches `{value}`** — {total:,} match(es):"]
        lines += [f"- **{row.get(field, 'N/A')}**" for row in rows]
        return {"message": "\n".join(lines), "products": []}

    @staticmethod
    def _is_summary_request(text):
        return bool(re.search(r"\b(summary|overview|report)\b", text))

    def _collection_summary(self, text):
        if "sales" in text:
            entity = "order"
        else:
            entity = self._entity_in_text(text)
        if not entity:
            return {
                "message": "Name a collection for the summary, for example `seller summary` or `orders report`.",
                "products": [],
            }

        handlers = {
            "product": self._products_summary, "seller": self._sellers_summary,
            "user": self._users_summary, "order": self._orders_summary,
            "shipping": self._shipping_summary, "review": self._reviews_summary,
            "payment": self._payments_summary, "inventory": self._inventory_summary,
            "return": self._returns_summary,
        }
        handler = handlers.get(entity)
        if not handler:
            return {"message": f"A summary is not configured for {entity} records yet.", "products": []}
        return {"message": handler(), "products": []}

    @staticmethod
    def _entity_in_text(text):
        for entity in ("order item", "product", "user", "seller", "order", "payment", "shipping", "review", "inventory", "return"):
            if re.search(rf"\b{_plural(entity)}\b", text):
                return entity
        # Product is often implied rather than named: "average price by
        # category" still has an unambiguous product collection target.
        if re.search(r"\b(brand|category|subcategory|price|stock|discount)\b", text):
            return "product"
        return None

    @staticmethod
    def _products_summary():
        rows = list(db["Products"].aggregate([{"$group": {
            "_id": None, "products": {"$sum": 1}, "avg_price": {"$avg": "$final_price"},
            "avg_rating": {"$avg": "$rating"}, "total_stock": {"$sum": "$stock"},
            "out_of_stock": {"$sum": {"$cond": [{"$lte": ["$stock", 0]}, 1, 0]}},
        }}]))
        data = rows[0] if rows else {}
        return (
            "**Product Summary**\n"
            f"- Products: **{data.get('products', 0):,}**\n"
            f"- Average final price: **{_money(data.get('avg_price'))}**\n"
            f"- Average rating: **{data.get('avg_rating', 0):.2f} / 5**\n"
            f"- Total stock: **{data.get('total_stock', 0):,}**\n"
            f"- Out of stock: **{data.get('out_of_stock', 0):,}**"
        )

    @staticmethod
    def _sellers_summary():
        rows = list(db["Sellers"].aggregate([{"$group": {
            "_id": None, "sellers": {"$sum": 1}, "average": {"$avg": "$seller_rating"},
            "minimum": {"$min": "$seller_rating"}, "maximum": {"$max": "$seller_rating"},
        }}]))
        data = rows[0] if rows else {}
        best = list(db["Sellers"].find({}, {"_id": 0, "seller_id": 1, "seller_rating": 1}).sort("seller_rating", -1).limit(1))
        best_text = f"{best[0]['seller_id']} ({best[0]['seller_rating']})" if best else "N/A"
        return (
            "**Seller Summary**\n"
            f"- Sellers: **{data.get('sellers', 0):,}**\n"
            f"- Average seller rating: **{data.get('average', 0):.2f} / 5**\n"
            f"- Rating range: **{data.get('minimum', 0):g} – {data.get('maximum', 0):g}**\n"
            f"- Highest-rated seller: **{best_text}**"
        )

    @staticmethod
    def _users_summary():
        count = db["Users"].count_documents({})
        top = list(db["Orders"].aggregate([
            {"$group": {"_id": "$user_id", "orders": {"$sum": 1}}}, {"$sort": {"orders": -1}}, {"$limit": 1},
        ]))
        top_text = f"{top[0]['_id']} ({top[0]['orders']:,} orders)" if top else "N/A"
        return f"**User Summary**\n- Total users: **{count:,}**\n- Most active user: **{top_text}**"

    @staticmethod
    def _orders_summary():
        rows = list(db["Orders"].aggregate([{"$group": {
            "_id": None, "orders": {"$sum": 1}, "returned": {"$sum": {"$cond": ["$is_returned", 1, 0]}},
            "average_shipping_days": {"$avg": "$shipping_time_days"}, "users": {"$addToSet": "$user_id"},
        }}]))
        data = rows[0] if rows else {}
        return (
            "**Order Summary**\n"
            f"- Total orders: **{data.get('orders', 0):,}**\n"
            f"- Returned orders: **{data.get('returned', 0):,}**\n"
            f"- Unique ordering users: **{len(data.get('users', [])):,}**\n"
            f"- Average shipping time: **{data.get('average_shipping_days', 0):.2f} days**"
        )

    @staticmethod
    def _shipping_summary():
        rows = list(db["Shipping"].aggregate([{"$group": {
            "_id": None, "records": {"$sum": 1}, "average_days": {"$avg": "$shipping_time_days"},
            "minimum_days": {"$min": "$shipping_time_days"}, "maximum_days": {"$max": "$shipping_time_days"},
        }}]))
        data = rows[0] if rows else {}
        return (
            "**Shipping Summary**\n"
            f"- Shipping records: **{data.get('records', 0):,}**\n"
            f"- Average shipping time: **{data.get('average_days', 0):.2f} days**\n"
            f"- Shipping-day range: **{data.get('minimum_days', 0):g} – {data.get('maximum_days', 0):g}**"
        )

    @staticmethod
    def _reviews_summary():
        rows = list(db["Reviews"].aggregate([{"$group": {
            "_id": None, "records": {"$sum": 1}, "average": {"$avg": "$rating"},
            "minimum": {"$min": "$rating"}, "maximum": {"$max": "$rating"},
        }}]))
        data = rows[0] if rows else {}
        return (
            "**Review Summary**\n"
            f"- Review records: **{data.get('records', 0):,}**\n"
            f"- Average rating: **{data.get('average', 0):.2f} / 5**\n"
            f"- Rating range: **{data.get('minimum', 0):g} – {data.get('maximum', 0):g}**"
        )

    @staticmethod
    def _payments_summary():
        rows = list(db["Payments"].aggregate([{"$group": {"_id": "$payment_method", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}]))
        lines = ["**Payment Summary**", f"- Payment records: **{sum(row['count'] for row in rows):,}**"]
        lines.extend(f"- {row['_id'] or 'Unknown'}: **{row['count']:,}**" for row in rows)
        return "\n".join(lines)

    @staticmethod
    def _inventory_summary():
        rows = list(db["Inventory"].aggregate([{"$group": {
            "_id": None, "records": {"$sum": 1}, "total_stock": {"$sum": "$stock"}, "average_stock": {"$avg": "$stock"},
        }}]))
        data = rows[0] if rows else {}
        return (
            "**Inventory Summary**\n"
            f"- Inventory records: **{data.get('records', 0):,}**\n"
            f"- Total stock: **{data.get('total_stock', 0):,}**\n"
            f"- Average stock: **{data.get('average_stock', 0):.2f}**"
        )

    @staticmethod
    def _returns_summary():
        total = db["Returns"].count_documents({})
        returned = db["Returns"].count_documents({"is_returned": True})
        return f"**Return Summary**\n- Return records: **{total:,}**\n- Marked returned: **{returned:,}**"

    # ------------------------------------------------------------------
    # aggregate and order queries
    # ------------------------------------------------------------------

    @staticmethod
    def _is_most_ordered_query(text):
        return bool(re.search(r"\b(most|top|highest)\s+ordered\s+(brand|category|subcategory)\b", text))

    def _most_ordered(self, text):
        match = re.search(r"\b(most|top|highest)\s+ordered\s+(brand|category|subcategory)\b", text)
        field = match.group(2)
        limit = self._top_n(text, default=5)
        rows = list(db["Orders"].aggregate([
            {"$lookup": {"from": "Products", "localField": "product_id", "foreignField": "product_id", "as": "product"}},
            {"$unwind": "$product"},
            {"$group": {"_id": f"$product.{field}", "orders": {"$sum": 1}}},
            {"$sort": {"orders": -1, "_id": 1}}, {"$limit": limit},
        ]))
        label = "Most ordered" if limit == 1 else f"Top {limit} ordered"
        lines = [f"**{label} {field}s:**"]
        lines.extend(f"- {row['_id'] or 'Unknown'}: **{row['orders']:,} orders**" for row in rows)
        return {"message": "\n".join(lines) if rows else "No order data is available.", "products": []}

    @staticmethod
    def _is_shipping_average_query(text):
        if re.search(r"\bby\s+(delivery status|location|user|product)\b", text):
            return False
        return bool(re.search(r"\b(avg|average|mean)\s+(?:shipping|delivery)\s+(?:time|days?)\b", text))

    @staticmethod
    def _shipping_average():
        rows = list(db["Shipping"].aggregate([{"$group": {"_id": None, "average": {"$avg": "$shipping_time_days"}, "records": {"$sum": 1}}}]))
        data = rows[0] if rows else {}
        return {
            "message": f"Average shipping time is **{data.get('average', 0):.2f} days** across **{data.get('records', 0):,}** shipping records.",
            "products": [],
        }

    @staticmethod
    def _orders_on_date(text):
        date_match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", text)
        if not date_match or not re.search(r"\b(orders?|purchases?)\b", text):
            return None
        date = date_match.group(1)
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return {"message": "Use a valid date in `YYYY-MM-DD` format.", "products": []}
        total = db["Orders"].count_documents({"purchase_date": date})
        return {"message": f"There are **{total:,}** order(s) on **{date}**.", "products": []}

    @staticmethod
    def _order_status_count(text):
        if not re.search(r"\b(how many|number of|count|total)\b", text):
            return None
        if re.search(r"\bby\s+(brand|category|subcategory|payment method|delivery status|location|user|product|purchase date)\b", text):
            return None
        if "return" in text:
            total = db["Orders"].count_documents({"is_returned": True})
            return {"message": f"There are **{total:,}** returned order(s).", "products": []}

        statuses = ("delayed", "delivered", "pending", "shipped", "cancelled", "returned")
        status = next((item for item in statuses if re.search(rf"\b{item}\b", text)), None)
        if not status:
            return None
        query = {"delivery_status": {"$regex": f"^{re.escape(status)}$", "$options": "i"}}
        total = db["Orders"].count_documents(query)
        return {"message": f"There are **{total:,}** order(s) with delivery status **{status.title()}**.", "products": []}

    def _collection_count(self, text):
        if not re.search(r"\b(how many|number of|count|total)\b", text):
            return None
        entity = self._entity_in_text(text)
        if not entity or entity not in COLLECTION_NAMES:
            return None
        collection = COLLECTION_NAMES[entity]
        count = db[collection].count_documents({})
        return {"message": f"There are **{count:,}** {collection.lower()} record(s).", "products": []}

    # ------------------------------------------------------------------
    # reusable entity + field + operation grammar
    # ------------------------------------------------------------------

    def _generic_group_query(self, message, text):
        """Handle requests such as ``average price by category``.

        Supported groups are deliberately named in :data:`GROUPS`, allowing
        natural variations while keeping every generated pipeline safe.
        """
        entity = self._entity_in_text(text)
        group = self._group_from_text(text)
        if not entity or not group:
            return None

        # "top five products by price" is a ranking, not a group operation.
        if entity == "product" and group == "final_price":
            return None

        operation, metric_field, metric_label = self._operation_and_metric(entity, text)
        if operation is None:
            return None
        pipeline = self._group_pipeline(entity, group, operation, metric_field, message, text)
        if pipeline is None:
            return None

        rows = list(db[COLLECTION_NAMES[entity]].aggregate(pipeline))
        if not rows:
            return {"message": "No records match that grouped request.", "products": []}

        title_operation = {
            "$sum": "Total", "$avg": "Average", "$min": "Minimum", "$max": "Maximum",
        }.get(operation, "Count")
        if operation == "count":
            title_operation = "Count"
        label = metric_label if operation != "count" else "records"
        lines = [f"**{title_operation} {label} by {group.replace('_', ' ')}:**"]
        for row in rows:
            value = row["value"]
            if metric_field == "final_price":
                shown = _money(value)
            elif isinstance(value, float):
                shown = f"{value:,.2f}"
            else:
                shown = f"{value:,}"
            lines.append(f"- {row['_id'] or 'Unknown'}: **{shown}**")
        return {"message": "\n".join(lines), "products": []}

    @staticmethod
    def _group_from_text(text):
        # Restrict this to expressions following "by" so a filter such as
        # "products by Nike" does not accidentally become a group request.
        by_match = re.search(r"\bby\s+([a-z ]+)", text)
        if not by_match:
            return None
        tail = by_match.group(1)
        for phrase, field in sorted(GROUPS.items(), key=lambda item: len(item[0]), reverse=True):
            if re.match(rf"{re.escape(phrase)}\b", tail):
                return field
        return None

    def _group_pipeline(self, entity, group, operation, metric_field, message, text):
        filters = self._filters_for(entity, message, text)
        source_group = group
        stages = [{"$match": filters}] if filters else []

        # Product attributes are reached from Orders/Reviews through a safe,
        # fixed lookup.  This is what makes "orders by category" work.
        product_group = group in {"brand", "category", "subcategory"}
        if product_group and entity in {"order", "review"}:
            stages.extend([
                {"$lookup": {"from": "Products", "localField": "product_id", "foreignField": "product_id", "as": "product"}},
                {"$unwind": "$product"},
            ])
            source_group = f"product.{group}"
        elif product_group and entity != "product":
            return None

        allowed_groups = {
            "product": {"brand", "category", "subcategory"},
            "order": {"brand", "category", "subcategory", "payment_method", "delivery_status", "location", "user_id", "product_id", "purchase_date"},
            "shipping": {"delivery_status", "location", "user_id", "product_id"},
            "review": {"brand", "category", "subcategory", "product_id"},
            "payment": {"payment_method", "user_id", "product_id"},
            "return": {"user_id", "product_id"},
        }
        if group not in allowed_groups.get(entity, set()):
            return None

        if operation == "count":
            accumulator = {"$sum": 1}
        else:
            if not metric_field:
                return None
            accumulator = {operation: f"${metric_field}"}

        ascending = bool(re.search(r"\b(lowest|least|minimum|min|smallest)\b", text))
        limit = self._top_n(text, default=10)
        stages.extend([
            {"$group": {"_id": f"${source_group}", "value": accumulator}},
            {"$sort": {"value": 1 if ascending else -1, "_id": 1}},
            {"$limit": limit},
        ])
        return stages

    def _generic_collection_query(self, message, text):
        """Interpret filtered counts, ranks, aggregates and lists by entity."""
        entity = self._entity_in_text(text)
        if not entity or entity not in COLLECTION_NAMES:
            return None

        # Product aggregations have a specialised formatter below.  Let it
        # handle those unless this is clearly a generic filtered count/list.
        operation, metric_field, metric_label = self._operation_and_metric(entity, text)
        filters = self._filters_for(entity, message, text)
        asks_count = bool(re.search(r"\b(how many|number of|count|total)\b", text))
        asks_list = bool(re.search(r"\b(show|list|find|display|get)\b", text))
        asks_rank = bool(re.search(r"\b(top|highest|most|lowest|least|best|worst)\b", text))

        if entity == "product" and operation and not asks_count and not asks_list and not asks_rank:
            return None

        if asks_count:
            count = db[COLLECTION_NAMES[entity]].count_documents(filters)
            qualifier = self._filter_description(entity, text)
            return {
                "message": f"There are **{count:,}** {entity} record(s){qualifier}.",
                "products": [],
            }

        if asks_rank and metric_field and self._is_rankable_field(metric_field):
            ascending = bool(re.search(r"\b(lowest|least|worst|minimum|min)\b", text))
            limit = self._top_n(text, default=5)
            rows = list(
                db[COLLECTION_NAMES[entity]].find(filters, {"_id": 0})
                .sort([(metric_field, 1 if ascending else -1)])
                .limit(limit)
            )
            if entity == "product":
                lines = [f"**{'Lowest' if ascending else 'Top'} {len(rows)} products by {metric_label}:**"]
                lines.extend(self._product_line(index, row) for index, row in enumerate(rows, 1))
                return {"message": "\n".join(lines), "products": rows}
            lines = [f"**{'Lowest' if ascending else 'Top'} {len(rows)} {entity}s by {metric_label}:**"]
            lines.extend(self._record_line(entity, row) for row in rows)
            return {"message": "\n".join(lines) if rows else "No matching records were found.", "products": []}

        if operation and metric_field:
            row = list(db[COLLECTION_NAMES[entity]].aggregate([
                {"$match": filters}, {"$group": {"_id": None, "value": {operation: f"${metric_field}"}, "records": {"$sum": 1}}},
            ]))
            if not row:
                return {"message": "No matching records were found.", "products": []}
            value = row[0].get("value")
            shown = _money(value) if metric_field == "final_price" else f"{value:,.2f}" if isinstance(value, float) else f"{value:,}"
            labels = {"$avg": "Average", "$min": "Minimum", "$max": "Maximum", "$sum": "Total"}
            return {
                "message": f"**{labels[operation]} {metric_label}** is **{shown}** across **{row[0]['records']:,}** matching {entity} record(s).",
                "products": [],
            }

        if asks_list and filters:
            rows = list(db[COLLECTION_NAMES[entity]].find(filters, {"_id": 0}).limit(MAX_RESULTS))
            if entity == "product":
                lines = [f"**Matching products** — showing {len(rows)} result(s):"]
                lines.extend(self._product_line(index, row) for index, row in enumerate(rows, 1))
                return {"message": "\n".join(lines), "products": rows}
            lines = [f"**Matching {entity} records** — showing {len(rows)} result(s):"]
            lines.extend(self._record_line(entity, row) for row in rows)
            return {"message": "\n".join(lines), "products": []}
        return None

    @staticmethod
    def _operation_and_metric(entity, text):
        metric_text = re.split(r"\bby\b", text, maxsplit=1)[0]
        if re.search(r"\b(avg|average|mean)\b", metric_text):
            operation = "$avg"
        elif re.search(r"\b(min|minimum|lowest|least)\b", metric_text) and "orders" not in metric_text:
            operation = "$min"
        elif re.search(r"\b(max|maximum|highest|most)\b", metric_text) and "orders" not in metric_text:
            operation = "$max"
        elif re.search(r"\b(sum|total value|total stock)\b", metric_text):
            operation = "$sum"
        elif re.search(r"\b(top|best|worst)\b", metric_text):
            # A ranking needs a metric but is sorted separately by the caller.
            operation = "$max"
        elif re.search(r"\b(count|how many|number of|total|ordered|orders?)\b", metric_text):
            return "count", None, "records"
        else:
            return None, None, None

        fields = ENTITY_FIELDS.get(entity, {})
        for phrase, field in sorted(fields.items(), key=lambda item: len(item[0]), reverse=True):
            if re.search(rf"\b{re.escape(phrase)}\b", metric_text):
                return operation, field, phrase
        # In a ranking, the metric naturally comes after "by":
        # "top sellers by rating".  Only use this fallback when no metric
        # appeared before "by", so grouped aggregates stay unambiguous.
        if " by " in text:
            trailing_text = text.split(" by ", 1)[1]
            for phrase, field in sorted(fields.items(), key=lambda item: len(item[0]), reverse=True):
                if re.match(rf"{re.escape(phrase)}\b", trailing_text):
                    return operation, field, phrase
        return operation, None, None

    def _filters_for(self, entity, message, text):
        clauses = []
        product_id = _safe_id(PRODUCT_ID, message, "P")
        user_id = _safe_id(USER_ID, message, "U")
        seller_id = _safe_id(SELLER_ID, message, "S")
        if product_id and entity in {"product", "order", "shipping", "review", "payment", "return", "inventory"}:
            clauses.append({"product_id": {"$regex": f"^{re.escape(product_id)}$", "$options": "i"}})
        if user_id and entity in {"user", "order", "shipping", "payment", "return"}:
            clauses.append({"user_id": {"$regex": f"^{re.escape(user_id)}$", "$options": "i"}})
        if seller_id and entity in {"seller", "product"}:
            clauses.append({"seller_id": {"$regex": f"^{re.escape(seller_id)}$", "$options": "i"}})

        date = re.search(r"\b\d{4}-\d{2}-\d{2}\b", text)
        if date and entity == "order":
            clauses.append({"purchase_date": date.group(0)})
        if "return" in text and entity in {"order", "return"}:
            clauses.append({"is_returned": True})

        payment = next((item for item in ("cash on delivery", "credit card", "debit card", "upi", "cash") if item in text), None)
        if payment and entity in {"order", "payment"}:
            clauses.append({"payment_method": {"$regex": re.escape(payment), "$options": "i"}})
        status = next((item for item in ("delayed", "delivered", "pending", "shipped", "cancelled", "returned") if re.search(rf"\b{item}\b", text)), None)
        if status and entity in {"order", "shipping"}:
            clauses.append({"delivery_status": {"$regex": f"^{re.escape(status)}$", "$options": "i"}})

        if entity == "product":
            product_filters = self._product_filters(message)
            if product_filters:
                clauses.append(product_filters)
            if re.search(r"\bin stock\b|\bavailable\b", text):
                clauses.append({"stock": {"$gt": 0}})

        comparison = self._entity_comparison(entity, text)
        if comparison:
            field, operator, value = comparison
            clauses.append({field: {operator: value}})

        return clauses[0] if len(clauses) == 1 else {"$and": clauses} if clauses else {}

    @staticmethod
    def _entity_comparison(entity, text):
        fields = ENTITY_FIELDS.get(entity, {})
        for phrase, field in sorted(fields.items(), key=lambda item: len(item[0]), reverse=True):
            expression = re.escape(phrase)
            symbol_match = re.search(rf"\b{expression}\s*(<=|>=|<|>|=)\s*(\d+(?:\.\d+)?)", text)
            if symbol_match:
                return field, COMPARISON_WORDS[symbol_match.group(1)], float(symbol_match.group(2))
            word_options = "|".join(re.escape(word) for word in sorted(COMPARISON_WORDS, key=len, reverse=True) if word not in {"<", "<=", ">", ">=", "="})
            word_match = re.search(rf"\b{expression}\s+(?:is\s+)?({word_options})\s+(\d+(?:\.\d+)?)", text)
            if word_match:
                return field, COMPARISON_WORDS[word_match.group(1)], float(word_match.group(2))
        return None

    @staticmethod
    def _is_rankable_field(field):
        return field in {"final_price", "rating", "stock", "discount", "review_count", "seller_rating", "shipping_time_days"}

    @staticmethod
    def _filter_description(entity, text):
        descriptions = []
        if "return" in text:
            descriptions.append(" marked returned")
        status = next((item for item in ("delayed", "delivered", "pending", "shipped", "cancelled") if item in text), None)
        if status:
            descriptions.append(f" with status {status.title()}")
        if "upi" in text:
            descriptions.append(" paid by UPI")
        return "".join(descriptions)

    @staticmethod
    def _record_line(entity, row):
        if entity == "seller":
            return f"- **{row.get('seller_id', 'N/A')}** — rating {row.get('seller_rating', '—')}"
        if entity == "order":
            return (
                f"- **{row.get('order_id', 'N/A')}** — user {row.get('user_id', '—')}, "
                f"product {row.get('product_id', '—')}, {row.get('delivery_status', '—')}"
            )
        if entity == "shipping":
            return f"- Product **{row.get('product_id', '—')}** — {row.get('shipping_time_days', '—')} day(s), {row.get('delivery_status', '—')}"
        if entity == "review":
            return f"- Product **{row.get('product_id', '—')}** — rating {row.get('rating', '—')}"
        if entity == "user":
            return f"- **{row.get('user_id', 'N/A')}**"
        if entity == "payment":
            return f"- User **{row.get('user_id', '—')}** · product {row.get('product_id', '—')} · {row.get('payment_method', '—')}"
        return f"- {row}"

    # ------------------------------------------------------------------
    # product ranking and aggregate queries
    # ------------------------------------------------------------------

    def _top_products(self, message, text):
        if not re.search(r"\b(top|highest|most|lowest|least|cheapest|expensive)\b", text):
            return None
        if not re.search(r"\b(products?|prices?|ratings?|stock|reviews?|discount)\b", text):
            return None
        if "ordered" in text or "seller" in text or "category" in text and "product" not in text:
            return None

        field, label = self._product_metric(text)
        if not field:
            return None
        ascending = bool(re.search(r"\b(lowest|least|cheapest|minimum|min)\b", text))
        limit = self._top_n(text, default=5)
        filters = self._product_filters(message)
        rows = self._find_products(filters, [(field, 1 if ascending else -1), ("rating", -1)], limit)
        direction = "Lowest" if ascending else "Top"
        lines = [f"**{direction} {len(rows)} products by {label}:**"]
        lines.extend(self._product_line(index, row) for index, row in enumerate(rows, 1))
        return {"message": "\n".join(lines) if rows else "No products match that request.", "products": rows}

    def _product_aggregate(self, message, text):
        aggregate_match = re.search(r"\b(avg|average|mean|min|minimum|max|maximum)\b", text)
        if not aggregate_match or "shipping" in text:
            return None
        field, label = self._product_metric(text)
        if not field:
            return None
        operation = aggregate_match.group(1)
        mongo_operation = "$avg" if operation in {"avg", "average", "mean"} else "$min" if operation in {"min", "minimum"} else "$max"
        rows = list(db["Products"].aggregate([
            {"$match": self._product_filters(message)},
            {"$group": {"_id": None, "value": {mongo_operation: f"${field}"}, "products": {"$sum": 1}}},
        ]))
        if not rows:
            return {"message": "No products match that request.", "products": []}
        value = rows[0].get("value")
        display_value = _money(value) if field == "final_price" else f"{value:,.2f}" if isinstance(value, float) else f"{value:,}"
        operation_label = {"$avg": "Average", "$min": "Minimum", "$max": "Maximum"}[mongo_operation]
        return {
            "message": f"**{operation_label} {label}** is **{display_value}** across **{rows[0]['products']:,}** matching product(s).",
            "products": [],
        }

    @staticmethod
    def _product_metric(text):
        if re.search(r"\b(final\s+)?price|prices?\b", text):
            return "final_price", "final price"
        if re.search(r"\breview\s+count|reviews?\b", text):
            return "review_count", "review count"
        if re.search(r"\brating|rated\b", text):
            return "rating", "rating"
        if re.search(r"\bdiscount\b", text):
            return "discount", "discount"
        if re.search(r"\bstock\b", text):
            return "stock", "stock"
        return None, None

    @staticmethod
    def _top_n(text, default=5):
        match = re.search(r"\b(?:top|lowest|highest|most|least)\s+(\d{1,2})\b", text)
        if not match:
            return default
        return max(1, min(int(match.group(1)), MAX_RESULTS))

    def _product_filters(self, message):
        """Resolve real category, subcategory and brand names from the catalog."""
        overview = self._catalog_options()
        lowered = message.lower()
        filters = []
        for field, values in overview.items():
            found = next((value for value in values if re.search(rf"\b{re.escape(value.lower())}\b", lowered)), None)
            if found:
                filters.append({field: {"$regex": f"^{re.escape(found)}$", "$options": "i"}})
        return filters[0] if len(filters) == 1 else {"$and": filters} if filters else {}

    @staticmethod
    def _catalog_options():
        values = {"category": set(), "subcategory": set(), "brand": set()}
        for row in db["Products"].aggregate([{"$group": {"_id": {"category": "$category", "subcategory": "$subcategory", "brand": "$brand"}}}, {"$limit": 1000}]):
            data = row.get("_id", {})
            for field in values:
                if data.get(field):
                    values[field].add(str(data[field]))
        return {field: sorted(items, key=len, reverse=True) for field, items in values.items()}

    @staticmethod
    def _find_products(query, sort, limit):
        rows = list(db["Products"].find(query, {"_id": 0}).sort(sort).limit(limit))
        return rows

    @staticmethod
    def _product_count(query):
        return db["Products"].count_documents(query)

    @staticmethod
    def _product_line(index, product):
        return (
            f"{index}. **{product.get('brand', '')} {product.get('subcategory', '')}** "
            f"({product.get('product_id', 'N/A')}) — {_money(product.get('final_price'))}, "
            f"rating {product.get('rating', '—')}, stock {product.get('stock', 0)}"
        )

    @staticmethod
    def _product_details(product_id):
        row = db["Products"].find_one(
            {"product_id": {"$regex": f"^{re.escape(product_id)}$", "$options": "i"}}, {"_id": 0}
        )
        if not row:
            return {
                "message": (
                    "**Product record not available**\n\n"
                    f"I could not locate a product with ID **{product_id}**. Please verify the ID and try again."
                ),
                "products": [],
            }
        orders = db["Orders"].count_documents({"product_id": {"$regex": f"^{re.escape(product_id)}$", "$options": "i"}})
        return {
            "message": (
                f"**{row.get('brand', '')} {row.get('subcategory', '')}** ({row.get('product_id')})\n"
                f"- Category: **{row.get('category', '—')}**\n"
                f"- Final price: **{_money(row.get('final_price'))}**\n"
                f"- Rating: **{row.get('rating', '—')} / 5**\n"
                f"- Stock: **{row.get('stock', 0)}**\n"
                f"- Orders: **{orders:,}**"
            ),
            "products": [row],
        }
