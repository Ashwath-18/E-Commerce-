"""
Per-collection graph data for the dashboard "Overview" panel.

get_detail("Orders") returns what the dashboard needs to draw that
collection's own graph:

    {
      "title":     "Orders per month",
      "subtitle":  "Last 12 months with orders",
      "caption":   "orders",          # word shown in the value bubble
      "unit_per":  "month",           # used for the "Average per ..." tile
      "scale":     "auto" | "zero",   # how the curve is scaled vertically
      "data":      [(label, value), ...],
      "note":      "message shown when there is nothing to draw",
    }

Read-only aggregations. Never raises: problems come back as an empty "data"
list with an explanatory "note".
"""

from datetime import datetime

from config.mongodb import db

MONTH_LIMIT = 12


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _ladder(field, steps, last_label):
    """Nested $cond expression that puts a numeric field into labelled buckets."""
    expr = last_label
    for upper, label in reversed(steps):
        expr = {"$cond": [{"$lt": [f"${field}", upper]}, label, expr]}
    return expr


def _ordered(rows, order):
    counts = {row["_id"]: row["n"] for row in rows}
    return [(label, counts[label]) for label in order if counts.get(label)]


def _bucket_counts(collection, field, steps, last_label, order, dedupe_on=None):
    pipeline = [{"$match": {field: {"$type": "number"}}}]
    if dedupe_on:
        pipeline += [
            {"$group": {"_id": f"${dedupe_on}", "doc": {"$first": "$$ROOT"}}},
            {"$replaceRoot": {"newRoot": "$doc"}},
        ]
    pipeline.append(
        {"$group": {"_id": _ladder(field, steps, last_label), "n": {"$sum": 1}}}
    )
    return _ordered(db[collection].aggregate(pipeline), order)


def _top_groups(collection, field, limit=8, match=None, dedupe_on=None):
    pipeline = []
    if match:
        pipeline.append({"$match": match})
    pipeline.append({"$match": {field: {"$ne": None}}})
    if dedupe_on:
        pipeline += [
            {"$group": {"_id": f"${dedupe_on}", "doc": {"$first": "$$ROOT"}}},
            {"$replaceRoot": {"newRoot": "$doc"}},
        ]
    pipeline += [
        {"$group": {"_id": f"${field}", "n": {"$sum": 1}}},
        {"$sort": {"n": -1}},
        {"$limit": limit},
    ]
    return [(str(row["_id"]), row["n"]) for row in db[collection].aggregate(pipeline)]


def _month_label(key):
    try:
        return datetime.strptime(key, "%Y-%m").strftime("%b '%y")
    except ValueError:
        return key


# ---------------------------------------------------------------------------
# one function per collection
# ---------------------------------------------------------------------------

def _products():
    data = _top_groups("Products", "category", dedupe_on="product_id")
    field_name = "category"
    if len(data) < 3:
        data = _top_groups("Products", "subcategory", dedupe_on="product_id")
        field_name = "subcategory"
    return {
        "title": f"Products by {field_name}",
        "subtitle": "Distinct products in each group",
        "caption": "products",
        "unit_per": field_name,
        "scale": "zero",
        "data": data,
    }


def _users():
    steps = [(2, "1 order"), (3, "2 orders"), (6, "3-5 orders"), (11, "6-10 orders")]
    order = ["1 order", "2 orders", "3-5 orders", "6-10 orders", "11+ orders"]
    pipeline = [
        {"$group": {"_id": "$user_id", "n": {"$sum": 1}}},
        {"$group": {"_id": _ladder("n", steps, "11+ orders"), "n": {"$sum": 1}}},
    ]
    return {
        "title": "Users by orders placed",
        "subtitle": "How many orders each customer has made",
        "caption": "users",
        "unit_per": "group",
        "scale": "zero",
        "data": _ordered(db["Orders"].aggregate(pipeline), order),
        "note": "No order data to analyse.",
    }


def _orders():
    rows = list(
        db["Orders"].aggregate(
            [
                {"$match": {"purchase_date": {"$type": "string"}}},
                {"$group": {"_id": {"$substr": ["$purchase_date", 0, 7]}, "n": {"$sum": 1}}},
                {"$sort": {"_id": 1}},
            ]
        )
    )
    if not rows:  # dates stored as real date objects instead of text
        rows = list(
            db["Orders"].aggregate(
                [
                    {"$match": {"purchase_date": {"$type": "date"}}},
                    {
                        "$group": {
                            "_id": {"$dateToString": {"format": "%Y-%m", "date": "$purchase_date"}},
                            "n": {"$sum": 1},
                        }
                    },
                    {"$sort": {"_id": 1}},
                ]
            )
        )
    rows = [r for r in rows if r["_id"]][-MONTH_LIMIT:]
    return {
        "title": "Orders per month",
        "subtitle": f"Last {len(rows)} months that have orders" if rows else "",
        "caption": "orders",
        "unit_per": "month",
        "scale": "auto",
        "data": [(_month_label(r["_id"]), r["n"]) for r in rows],
        "note": "No orders with a purchase date were found.",
    }


def _reviews():
    steps = [(1.5, "1 star"), (2.5, "2 stars"), (3.5, "3 stars"), (4.5, "4 stars")]
    order = ["1 star", "2 stars", "3 stars", "4 stars", "5 stars"]
    return {
        "title": "Reviews by rating",
        "subtitle": "Products grouped by their rounded rating",
        "caption": "reviews",
        "unit_per": "rating",
        "scale": "zero",
        "data": _bucket_counts("Reviews", "rating", steps, "5 stars", order),
    }


def _shipping():
    return {
        "title": "Shipments by status",
        "subtitle": "Delivery status of every shipment",
        "caption": "shipments",
        "unit_per": "status",
        "scale": "zero",
        "data": _top_groups("Shipping", "delivery_status"),
    }


def _payments():
    return {
        "title": "Payments by method",
        "subtitle": "How customers pay",
        "caption": "payments",
        "unit_per": "method",
        "scale": "zero",
        "data": _top_groups("Payments", "payment_method"),
    }


def _inventory():
    steps = [(1, "Out of stock"), (51, "1-50"), (201, "51-200"), (501, "201-500")]
    order = ["Out of stock", "1-50", "51-200", "201-500", "500+"]
    return {
        "title": "Inventory by stock level",
        "subtitle": "Number of products at each stock level",
        "caption": "products",
        "unit_per": "level",
        "scale": "zero",
        "data": _bucket_counts("Inventory", "stock", steps, "500+", order),
    }


def _sellers():
    steps = [(3.0, "Below 3.0"), (3.5, "3.0-3.5"), (4.0, "3.5-4.0"), (4.5, "4.0-4.5")]
    order = ["Below 3.0", "3.0-3.5", "3.5-4.0", "4.0-4.5", "4.5+"]
    return {
        "title": "Sellers by rating",
        "subtitle": "Number of sellers in each rating band",
        "caption": "sellers",
        "unit_per": "band",
        "scale": "zero",
        "data": _bucket_counts("Sellers", "seller_rating", steps, "4.5+", order),
    }


BUILDERS = {
    "Products": _products,
    "Users": _users,
    "Orders": _orders,
    "Reviews": _reviews,
    "Shipping": _shipping,
    "Payments": _payments,
    "Inventory": _inventory,
    "Sellers": _sellers,
}


def get_detail(name):
    """Graph data for one dashboard collection. Never raises."""
    builder = BUILDERS.get(name)
    if builder is None:
        return {"title": name, "subtitle": "", "caption": "records", "unit_per": "group",
                "scale": "zero", "data": [], "note": "No graph is defined for this collection."}
    try:
        detail = builder()
    except Exception as exc:
        return {"title": name, "subtitle": "", "caption": "records", "unit_per": "group",
                "scale": "zero", "data": [], "note": f"Could not load this graph: {exc}"}
    detail.setdefault("note", "No data to show for this collection.")
    return detail
