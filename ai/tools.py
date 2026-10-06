"""
Database tools for the Cartify AI.

The language model never sees the database directly. It asks for one of
these tools (search, compare, statistics ...), we run it against MongoDB and
hand the real result back. That is what keeps answers grounded in real data.

All tools return JSON-safe dicts and never raise: problems come back as
{"error": "..."} so the model can explain them.
"""

import re
import time

from config.mongodb import db

MAX_LIMIT = 10

PRODUCT_FIELDS = (
    "product_id", "category", "subcategory", "brand", "price", "discount",
    "final_price", "stock", "rating", "review_count", "seller_id", "seller_rating",
)

SORTS = {
    "rating": [("rating", -1), ("review_count", -1)],
    "reviews": [("review_count", -1), ("rating", -1)],
    "price_asc": [("final_price", 1), ("rating", -1)],
    "price_desc": [("final_price", -1), ("rating", -1)],
    "discount": [("discount", -1), ("rating", -1)],
    "stock": [("stock", -1)],
}

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _contains(value):
    return {"$regex": re.escape(str(value).strip()), "$options": "i"}


def _exact(value):
    return {"$regex": f"^{re.escape(str(value).strip())}$", "$options": "i"}


def _clean(doc):
    row = {key: doc.get(key) for key in PRODUCT_FIELDS if key in doc}
    for key in ("price", "final_price", "discount", "rating", "seller_rating"):
        if isinstance(row.get(key), float):
            row[key] = round(row[key], 2)
    return row


def _dedupe(rows):
    seen, unique = set(), []
    for row in rows:
        key = row.get("product_id")
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    return unique


def _number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _product_match(args):
    """Build a Mongo filter from the shared product filter arguments."""
    clauses = []

    for field in ("category", "subcategory", "brand"):
        if args.get(field):
            clauses.append({field: _contains(args[field])})

    query = str(args.get("query") or "").strip()
    for token in re.findall(r"[A-Za-z0-9]+", query)[:6]:
        clauses.append(
            {
                "$or": [
                    {"product_id": _contains(token)},
                    {"brand": _contains(token)},
                    {"category": _contains(token)},
                    {"subcategory": _contains(token)},
                ]
            }
        )

    price = {}
    if _number(args.get("min_price")) is not None:
        price["$gte"] = _number(args["min_price"])
    if _number(args.get("max_price")) is not None:
        price["$lte"] = _number(args["max_price"])
    if price:
        clauses.append({"final_price": price})

    if _number(args.get("min_rating")) is not None:
        clauses.append({"rating": {"$gte": _number(args["min_rating"])}})

    if args.get("in_stock_only"):
        clauses.append({"stock": {"$gt": 0}})

    if not clauses:
        return {}
    return clauses[0] if len(clauses) == 1 else {"$and": clauses}


def _distinct_products_pipeline(match):
    """Pipeline stages that collapse duplicate product_id rows."""
    return [
        {"$match": match},
        {"$group": {"_id": "$product_id", "doc": {"$first": "$$ROOT"}}},
        {"$replaceRoot": {"newRoot": "$doc"}},
    ]


# ---------------------------------------------------------------------------
# tools
# ---------------------------------------------------------------------------


def search_products(args):
    match = _product_match(args)
    sort_key = args.get("sort_by") if args.get("sort_by") in SORTS else "rating"
    limit = int(min(max(_number(args.get("limit")) or 6, 1), MAX_LIMIT))

    products = db["Products"]
    rows = list(
        products.find(match, {"_id": 0}).sort(SORTS[sort_key]).limit(limit * 4)
    )
    unique = [_clean(r) for r in _dedupe(rows)]

    total = 0
    try:
        counted = list(
            products.aggregate(
                [{"$match": match}, {"$group": {"_id": "$product_id"}}, {"$count": "n"}]
            )
        )
        total = counted[0]["n"] if counted else 0
    except Exception:
        total = len(unique)

    return {
        "total_matching_products": total,
        "returned": min(len(unique), limit),
        "sorted_by": sort_key,
        "products": unique[:limit],
    }


def get_product_details(args):
    product_id = str(args.get("product_id") or "").strip()
    if not product_id:
        return {"error": "product_id is required"}

    try:
        from search.search_products import get_product_overview

        overview = get_product_overview(product_id)
    except Exception:
        overview = None

    if overview:
        return {
            "products": [_clean(overview["product"])],
            "inventory_stock": overview.get("inventory_stock"),
            "orders": overview.get("order_count"),
            "review_records": overview.get("review_records"),
            "average_review_rating": overview.get("average_review_rating"),
            "shipping_records": overview.get("shipping_count"),
            "delivery_statuses": overview.get("delivery_statuses"),
            "payment_methods": overview.get("payment_methods"),
            "returned_orders": overview.get("return_count"),
        }

    doc = db["Products"].find_one({"product_id": _exact(product_id)}, {"_id": 0})
    if not doc:
        return {"error": f"No product found with ID {product_id}"}
    return {"products": [_clean(doc)]}


def compare_products(args):
    ids = [str(i).strip() for i in (args.get("product_ids") or []) if str(i).strip()][:5]
    if len(ids) < 2:
        return {"error": "Provide at least two product IDs to compare."}

    found, missing = [], []
    for product_id in ids:
        doc = db["Products"].find_one({"product_id": _exact(product_id)}, {"_id": 0})
        (found if doc else missing).append(_clean(doc) if doc else product_id)

    result = {"products": found, "not_found": missing}
    if len(found) >= 2:
        def best(key, highest=True):
            rows = [p for p in found if p.get(key) is not None]
            if not rows:
                return None
            pick = max(rows, key=lambda p: p[key]) if highest else min(rows, key=lambda p: p[key])
            return pick["product_id"]

        result["winners"] = {
            "lowest_price": best("final_price", False),
            "highest_rating": best("rating"),
            "most_reviews": best("review_count"),
            "highest_discount": best("discount"),
            "most_stock": best("stock"),
        }
    return result


GROUP_FIELDS = {"category", "subcategory", "brand"}
METRICS = {
    "count": {"$sum": 1},
    "avg_price": {"$avg": "$final_price"},
    "avg_rating": {"$avg": "$rating"},
    "avg_discount": {"$avg": "$discount"},
    "total_stock": {"$sum": "$stock"},
}


def catalog_stats(args):
    group_by = args.get("group_by")
    metric = args.get("metric") if args.get("metric") in METRICS else "count"
    match = _product_match(args)

    base = _distinct_products_pipeline(match)

    if group_by not in GROUP_FIELDS:
        pipeline = base + [
            {
                "$group": {
                    "_id": None,
                    "products": {"$sum": 1},
                    "avg_price": {"$avg": "$final_price"},
                    "avg_rating": {"$avg": "$rating"},
                    "min_price": {"$min": "$final_price"},
                    "max_price": {"$max": "$final_price"},
                    "total_stock": {"$sum": "$stock"},
                }
            }
        ]
        rows = list(db["Products"].aggregate(pipeline))
        if not rows:
            return {"summary": {"products": 0}}
        row = rows[0]
        row.pop("_id", None)
        return {"summary": {k: (round(v, 2) if isinstance(v, float) else v) for k, v in row.items()}}

    top_n = int(min(max(_number(args.get("top_n")) or 10, 1), 30))
    direction = 1 if args.get("order") == "asc" else -1
    pipeline = base + [
        {"$group": {"_id": f"${group_by}", "value": METRICS[metric], "products": {"$sum": 1}}},
        {"$sort": {"value": direction}},
        {"$limit": top_n},
    ]
    rows = list(db["Products"].aggregate(pipeline))
    return {
        "group_by": group_by,
        "metric": metric,
        "rows": [
            {
                group_by: r["_id"],
                metric: round(r["value"], 2) if isinstance(r["value"], float) else r["value"],
                "products": r["products"],
            }
            for r in rows
        ],
    }


def list_options(args):
    field = args.get("field")
    if field not in GROUP_FIELDS:
        return {"error": "field must be one of: category, subcategory, brand"}

    match = _product_match(args)
    pipeline = _distinct_products_pipeline(match) + [
        {"$group": {"_id": f"${field}", "products": {"$sum": 1}}},
        {"$sort": {"products": -1}},
        {"$limit": 60},
    ]
    rows = list(db["Products"].aggregate(pipeline))
    return {"field": field, "options": [{"name": r["_id"], "products": r["products"]} for r in rows]}


ORDER_METRICS = {
    "delivery_status": ("Orders", "$delivery_status"),
    "payment_method": ("Orders", "$payment_method"),
    "returns": ("Orders", "$is_returned"),
    "orders_by_month": ("Orders", {"$substr": ["$purchase_date", 0, 7]}),
    "shipping_by_location": ("Shipping", "$location"),
    "shipping_status": ("Shipping", "$delivery_status"),
}


def order_analytics(args):
    """Aggregate-only business analytics (no individual customer data)."""
    metric = args.get("metric")
    if metric not in ORDER_METRICS:
        return {"error": "metric must be one of: " + ", ".join(ORDER_METRICS)}

    collection, key = ORDER_METRICS[metric]
    match = {}
    if args.get("product_id"):
        match["product_id"] = _exact(args["product_id"])

    group = {"_id": key, "records": {"$sum": 1}}
    if collection == "Shipping":
        group["avg_shipping_days"] = {"$avg": "$shipping_time_days"}

    pipeline = ([{"$match": match}] if match else []) + [
        {"$group": group},
        {"$sort": {"_id": 1} if metric == "orders_by_month" else {"records": -1}},
        {"$limit": 40},
    ]
    rows = list(db[collection].aggregate(pipeline))
    total = sum(r["records"] for r in rows) or 1

    out = []
    for r in rows:
        item = {"value": r["_id"], "records": r["records"], "share_percent": round(r["records"] * 100 / total, 1)}
        if "avg_shipping_days" in r and r["avg_shipping_days"] is not None:
            item["avg_shipping_days"] = round(r["avg_shipping_days"], 2)
        out.append(item)
    return {"metric": metric, "source": collection, "total_records": total if rows else 0, "rows": out}


# ---------------------------------------------------------------------------
# catalog overview (injected into the prompt so the model knows real values)
# ---------------------------------------------------------------------------

_overview_cache = {"time": 0, "value": None}


def catalog_overview(max_age=300):
    now = time.time()
    if _overview_cache["value"] and now - _overview_cache["time"] < max_age:
        return _overview_cache["value"]

    overview = {"categories": {}, "brands": []}
    try:
        pipeline = [
            {"$group": {"_id": {"c": "$category", "s": "$subcategory"}}},
            {"$limit": 500},
        ]
        for row in db["Products"].aggregate(pipeline):
            c, s = row["_id"].get("c"), row["_id"].get("s")
            if c:
                overview["categories"].setdefault(c, [])
                if s and s not in overview["categories"][c]:
                    overview["categories"][c].append(s)
        brand_rows = db["Products"].aggregate(
            [{"$group": {"_id": "$brand", "n": {"$sum": 1}}}, {"$sort": {"n": -1}}, {"$limit": 60}]
        )
        overview["brands"] = [r["_id"] for r in brand_rows if r["_id"]]
        for subs in overview["categories"].values():
            subs.sort()
    except Exception:
        pass

    _overview_cache.update(time=now, value=overview)
    return overview


# ---------------------------------------------------------------------------
# schemas shown to the model + dispatcher
# ---------------------------------------------------------------------------

_FILTERS = {
    "query": {"type": "string", "description": "Free text (brand, category or product id words)."},
    "category": {"type": "string", "description": "Category, e.g. Electronics."},
    "subcategory": {"type": "string", "description": "Subcategory, e.g. Headphones."},
    "brand": {"type": "string", "description": "Brand name."},
    "min_price": {"type": "number", "description": "Minimum final price in rupees."},
    "max_price": {"type": "number", "description": "Maximum final price in rupees."},
    "min_rating": {"type": "number", "description": "Minimum rating (0-5)."},
    "in_stock_only": {"type": "boolean", "description": "Only products with stock > 0."},
}


def _tool(name, description, properties, required=None):
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required or [],
            },
        },
    }


TOOLS = [
    _tool(
        "search_products",
        "Find products in the live catalog with filters and sorting. Use for any "
        "'show / find / cheapest / best / under 5000' style request.",
        {
            **_FILTERS,
            "sort_by": {
                "type": "string",
                "enum": list(SORTS),
                "description": "rating (default), reviews, price_asc (cheapest), price_desc, discount, stock.",
            },
            "limit": {"type": "integer", "description": "How many products (1-10, default 6)."},
        },
    ),
    _tool(
        "get_product_details",
        "Full details of ONE product plus its orders, reviews, shipping and returns summary.",
        {"product_id": {"type": "string", "description": "Exact product id, e.g. P12345."}},
        ["product_id"],
    ),
    _tool(
        "compare_products",
        "Compare 2-5 products side by side by their product ids.",
        {"product_ids": {"type": "array", "items": {"type": "string"}}},
        ["product_ids"],
    ),
    _tool(
        "catalog_stats",
        "Aggregate catalog statistics. Use for 'how many', 'average price', 'which brand has the most'. "
        "Omit group_by for overall totals.",
        {
            **_FILTERS,
            "group_by": {"type": "string", "enum": ["category", "subcategory", "brand"]},
            "metric": {"type": "string", "enum": list(METRICS)},
            "order": {"type": "string", "enum": ["desc", "asc"]},
            "top_n": {"type": "integer", "description": "Rows to return (default 10)."},
        },
    ),
    _tool(
        "list_options",
        "List the real categories, subcategories or brands (with product counts).",
        {"field": {"type": "string", "enum": ["category", "subcategory", "brand"]}, **_FILTERS},
        ["field"],
    ),
    _tool(
        "order_analytics",
        "Aggregate business analytics from orders and shipping: delivery status mix, payment methods, "
        "return rate, orders per month, shipping time by location. Aggregates only.",
        {
            "metric": {"type": "string", "enum": list(ORDER_METRICS)},
            "product_id": {"type": "string", "description": "Optional: limit to one product."},
        },
        ["metric"],
    ),
]

REGISTRY = {
    "search_products": search_products,
    "get_product_details": get_product_details,
    "compare_products": compare_products,
    "catalog_stats": catalog_stats,
    "list_options": list_options,
    "order_analytics": order_analytics,
}

STATUS_TEXT = {
    "search_products": "Searching the catalog…",
    "get_product_details": "Looking up product details…",
    "compare_products": "Comparing products…",
    "catalog_stats": "Crunching catalog numbers…",
    "list_options": "Checking available options…",
    "order_analytics": "Analysing orders and shipping…",
}


def run_tool(name, args):
    """Execute a tool by name. Never raises."""
    function = REGISTRY.get(name)
    if function is None:
        return {"error": f"Unknown tool: {name}"}
    try:
        return function(args if isinstance(args, dict) else {})
    except Exception as exc:  # database offline, bad data, ...
        return {"error": f"Database lookup failed: {exc}"}
