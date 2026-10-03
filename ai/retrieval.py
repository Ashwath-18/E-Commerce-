"""Safe, application-controlled product retrieval for Cartify AI."""

import re
from typing import Iterable

from config.mongodb import db

products = db["Products"]

CATEGORY_ALIASES = {
    "phone": "Mobile",
    "phones": "Mobile",
    "mobile": "Mobile",
    "mobiles": "Mobile",
    "headphone": "Headphones",
    "headphones": "Headphones",
    "laptop": "Laptop",
    "laptops": "Laptop",
    "notebook": "Laptop",
    "camera": "Camera",
}

STOP_WORDS = {
    "show", "me", "some", "good", "best", "find", "need", "want", "looking",
    "for", "a", "an", "the", "under", "below", "less", "than", "with", "and",
    "or", "please", "product", "products", "one", "ones", "which", "is", "are",
    "do", "you", "have", "anything", "something", "similar", "another", "more",
    "cheaper", "expensive", "available", "in", "my", "budget", "around", "rs", "inr",
    "₹", "phone", "phones", "laptop", "laptops", "headphone", "headphones", "smartwatch",
}


def _money_values(text):
    cleaned = text.replace(",", "")
    # Digits glued to letters (e.g. product IDs like P13100) are not prices.
    pattern = r"(?<![A-Za-z0-9])(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)(?![A-Za-z0-9])"
    values = [float(x) for x in re.findall(pattern, cleaned, re.I)]
    return [v for v in values if v >= 100]


def parse_constraints(message):
    text = message.lower()
    values = _money_values(message)
    min_price = None
    max_price = None

    if re.search(r"\b(under|below|less than|upto|up to|max(?:imum)?|within)\b", text) and values:
        max_price = values[0]
    elif re.search(r"\b(over|above|more than|min(?:imum)?|at least)\b", text) and values:
        min_price = values[0]
    elif len(values) >= 2 and re.search(r"\b(between|from).*(to|and)\b", text):
        min_price, max_price = sorted(values[:2])
    elif len(values) >= 2:
        min_price, max_price = sorted(values[:2])

    rating_match = re.search(r"(?:rating|rated|stars?)\s*(?:of|above|over|at least|>=|:)?\s*(\d(?:\.\d)?)", text)
    min_rating = float(rating_match.group(1)) if rating_match else None

    return {"min_price": min_price, "max_price": max_price, "min_rating": min_rating}


def _distinct(field):
    return [str(v) for v in products.distinct(field) if v not in (None, "")]


def _find_named(text, field):
    text_cf = text.casefold()
    for value in sorted(_distinct(field), key=len, reverse=True):
        if value.casefold() in text_cf:
            return value
    if field == "subcategory":
        for alias, value in CATEGORY_ALIASES.items():
            if re.search(rf"\b{re.escape(alias)}\b", text_cf):
                return value
    return None


def _tokens(text):
    return [
        token for token in re.findall(r"[a-zA-Z0-9]+", text.casefold())
        if len(token) >= 3 and token not in STOP_WORDS and not token.isdigit()
    ]


def _base_query(message):
    constraints = parse_constraints(message)
    query = {}
    if constraints["min_price"] is not None or constraints["max_price"] is not None:
        price = {}
        if constraints["min_price"] is not None:
            price["$gte"] = constraints["min_price"]
        if constraints["max_price"] is not None:
            price["$lte"] = constraints["max_price"]
        query["final_price"] = price
    if constraints["min_rating"] is not None:
        query["rating"] = {"$gte": constraints["min_rating"]}

    for field in ("brand", "category", "subcategory"):
        named = _find_named(message, field)
        if named:
            query[field] = {"$regex": f"^{re.escape(named)}$", "$options": "i"}

    tokens = _tokens(message)
    if tokens:
        ors = []
        for token in tokens[:8]:
            regex = {"$regex": re.escape(token), "$options": "i"}
            ors.extend([
                {"product_id": regex},
                {"brand": regex},
                {"category": regex},
                {"subcategory": regex},
            ])
        if ors:
            # If explicit fields exist, token matching acts as an additional narrowing signal only when needed.
            query.setdefault("$or", ors)
    return query


def retrieve_products(message, limit=8, exclude_ids=None, price_mode=None):
    """Retrieve actual products only; returns records with no Mongo _id."""
    exclude_ids = set(exclude_ids or [])
    constraints = parse_constraints(message)
    query = _base_query(message)
    tokens = _tokens(message)

    # Price follow-up modes are applied from the current context by the service.
    if price_mode:
        query.pop("$or", None)
        price = {}
        if price_mode == "cheaper":
            price["$lt"] = price_mode["reference"] if isinstance(price_mode, dict) else 10**18
        elif price_mode == "more_expensive":
            price["$gt"] = price_mode["reference"] if isinstance(price_mode, dict) else 0
        if price:
            query["final_price"] = price

    if exclude_ids:
        query["product_id"] = {"$nin": list(exclude_ids)}

    # First try the semantic-ish field query. If it yields nothing, retry only explicit constraints.
    records = list(products.find(query, {"_id": 0}).sort([("rating", -1), ("review_count", -1)]).limit(limit))
    if not records:
        fallback = {}
        if constraints["min_price"] is not None or constraints["max_price"] is not None:
            price = {}
            if constraints["min_price"] is not None:
                price["$gte"] = constraints["min_price"]
            if constraints["max_price"] is not None:
                price["$lte"] = constraints["max_price"]
            fallback["final_price"] = price
        if constraints["min_rating"] is not None:
            fallback["rating"] = {"$gte": constraints["min_rating"]}
        for field in ("brand", "category", "subcategory"):
            named = _find_named(message, field)
            if named:
                fallback[field] = {"$regex": f"^{re.escape(named)}$", "$options": "i"}
        if fallback:
            records = list(products.find(fallback, {"_id": 0}).sort([("rating", -1), ("review_count", -1)]).limit(limit))
        elif not tokens:
            records = list(products.find({}, {"_id": 0}).sort([("rating", -1), ("review_count", -1)]).limit(limit))

    return [r for r in records if r.get("product_id") not in exclude_ids]


def get_product(product_id):
    if not product_id:
        return None
    return products.find_one(
        {"product_id": {"$regex": f"^{re.escape(str(product_id).strip())}$", "$options": "i"}},
        {"_id": 0},
    )


def find_by_context(message, context_products):
    """Resolve first/second/this/that and price-relative follow-ups to actual records."""
    if not context_products:
        return None, None
    text = message.casefold()
    indexed = list(enumerate(context_products, start=1))
    for n, product in indexed:
        if re.search(rf"\b(?:the\s+)?{n}(?:st|nd|rd|th)?\s+(?:one|product)\b", text):
            return product, "indexed"
    if re.search(r"\b(first|1st)\b", text):
        return indexed[0][1], "indexed"
    if re.search(r"\b(second|2nd)\b", text) and len(indexed) >= 2:
        return indexed[1][1], "indexed"
    if re.search(r"\b(third|3rd)\b", text) and len(indexed) >= 3:
        return indexed[2][1], "indexed"
    if re.search(r"\b(this|that|it)\b", text):
        return indexed[0][1], "implicit"
    return None, None


def format_products(products_list: Iterable[dict]):
    rows = []
    for p in products_list:
        rows.append({
            "product_id": p.get("product_id"),
            "category": p.get("category"),
            "subcategory": p.get("subcategory"),
            "brand": p.get("brand"),
            "price": p.get("price"),
            "discount": p.get("discount"),
            "final_price": p.get("final_price"),
            "stock": p.get("stock"),
            "rating": p.get("rating"),
            "review_count": p.get("review_count"),
            "seller_id": p.get("seller_id"),
            "seller_rating": p.get("seller_rating"),
        })
    return rows