"""
Local catalog assistant.

A rule-based engine on top of the SAME database tools the AI uses. It is
smarter than plain keyword search: it understands sorting words, counts,
averages, delivery analytics, product ids, "the first one" follow-ups and
simple comparisons without contacting an external service.
"""

import re

from ai import tools
from ai.retrieval import parse_constraints

ALIASES = {
    "phone": "mobile", "phones": "mobile", "smartphone": "mobile", "smartphones": "mobile",
    "earphone": "headphones", "earphones": "headphones", "headset": "headphones",
    "headphone": "headphones", "laptops": "laptop", "notebook": "laptop",
}

SORT_RULES = [
    (r"\b(cheap|cheapest|lowest price|low price|budget|affordable|least expensive)\b", "price_asc"),
    (r"\b(expensive|costly|costliest|premium|highest price|most expensive)\b", "price_desc"),
    (r"\b(most reviewed|most reviews|popular|trending)\b", "reviews"),
    (r"\b(discount|discounts|offer|offers|deal|deals|sale)\b", "discount"),
    (r"\b(best|top|highest rated|top rated|best rated|good)\b", "rating"),
]

ORDINALS = {
    "first": 0, "1st": 0, "second": 1, "2nd": 1, "third": 2, "3rd": 2,
    "fourth": 3, "4th": 3, "fifth": 4, "5th": 4,
}


def _rupees(value):
    try:
        return f"₹{float(value):,.0f}"
    except (TypeError, ValueError):
        return "₹—"


def _line(index, p):
    return (
        f"{index}. **{p.get('brand', '')} {p.get('subcategory', '')}** ({p.get('product_id')}) — "
        f"**{_rupees(p.get('final_price'))}**, ★ {p.get('rating', '—')}, "
        f"{p.get('review_count', 0)} reviews, stock {p.get('stock', 0)}"
    )


def _entities(text, overview):
    """Find category / subcategory / brand names mentioned in the text."""
    lowered = text.lower()
    for alias, real in ALIASES.items():
        lowered = re.sub(rf"\b{alias}\b", real, lowered)

    found = {}
    for category, subs in overview.get("categories", {}).items():
        if re.search(rf"\b{re.escape(category.lower())}\b", lowered):
            found["category"] = category
        for sub in subs:
            if re.search(rf"\b{re.escape(sub.lower())}s?\b", lowered):
                found["subcategory"] = sub
    for brand in overview.get("brands", []):
        if re.search(rf"\b{re.escape(brand.lower())}\b", lowered):
            found.setdefault("brands", []).append(brand)
    return found


def answer(message, last_products=None):
    """Return {"message": markdown, "products": [..]} using only database tools."""
    last_products = last_products or []
    text = message.strip()
    lowered = text.lower()
    overview = tools.catalog_overview()
    entities = _entities(text, overview)

    # ---- greeting / help
    if re.fullmatch(r"(hi|hii+|hello|hey|vanakkam|hola|yo)[\s!.?]*", lowered) or "what can you do" in lowered:
        return {
            "message": (
                "Hi! I'm the **Cartify Database Assistant**. I can:\n"
                "- **Find products** — e.g. *cheapest headphones*, *top rated Electronics under ₹5000*\n"
                "- **Look up a product** by ID, e.g. *P12345*\n"
                "- **Count & average** — *how many Sony products*, *average price by brand*\n"
                "- **Delivery & returns summary**\n\n"
                "Every result is calculated from your local MongoDB database."
            ),
            "products": [],
        }

    # ---- "the first one" follow-ups
    for word, position in ORDINALS.items():
        if re.search(rf"\b{word}\b", lowered) and last_products and position < len(last_products):
            return _details(last_products[position]["product_id"])

    # ---- explicit product id
    match = re.search(r"\bP\d{3,}\b", text, re.IGNORECASE)
    ids = re.findall(r"\bP\d{3,}\b", text, re.IGNORECASE)
    if re.search(r"\b(compare|vs|versus|difference)\b", lowered) and len(ids) >= 2:
        return _compare(ids)
    if match:
        return _details(match.group(0))

    # ---- delivery / returns / payment analytics
    if re.search(r"\b(deliver\w*|return\w*|payment\w*|shipping time|shipment\w*)\b", lowered) and not entities.get("subcategory"):
        metric = "delivery_status"
        if "return" in lowered:
            metric = "returns"
        elif "payment" in lowered:
            metric = "payment_method"
        elif "location" in lowered or "shipping time" in lowered:
            metric = "shipping_by_location"
        return _analytics(metric)

    # ---- which brand/category has the most ...
    group = re.search(r"\b(brand|category|subcategory)\b", lowered)
    if group and re.search(r"\b(most|highest|top|largest|biggest|which)\b", lowered) and re.search(r"\b(products?|items?|count|many)\b", lowered):
        return _group_stats(group.group(1), "count", entities)
    if re.search(r"\b(average|avg|mean)\b", lowered):
        field = group.group(1) if group else None
        return _group_stats(field, "avg_price", entities, overall=not group)

    # ---- how many
    if re.search(r"\b(how many|count|number of|total)\b", lowered):
        args = _filters(entities)
        result = tools.run_tool("catalog_stats", args)
        n = result.get("summary", {}).get("products", 0)
        brand = (entities.get("brands") or [""])[0]
        place = entities.get("subcategory") or entities.get("category")
        label = f"{brand} products".strip()
        if place:
            label += f" in {place}"
        return {"message": f"There are **{n:,}** {label} in the catalog.", "products": []}

    # ---- product search
    return _search(text, lowered, entities)


# --------------------------------------------------------------------------


def _filters(entities):
    args = {}
    if entities.get("category"):
        args["category"] = entities["category"]
    if entities.get("subcategory"):
        args["subcategory"] = entities["subcategory"]
    if entities.get("brands"):
        args["brand"] = entities["brands"][0]
    return args


def _search(text, lowered, entities):
    args = _filters(entities)
    sort = "rating"
    for pattern, key in SORT_RULES:
        if re.search(pattern, lowered):
            sort = key
            break
    args["sort_by"] = sort
    args["limit"] = 6

    constraints = parse_constraints(text)
    if constraints.get("max_price") is not None:
        args["max_price"] = constraints["max_price"]
    if constraints.get("min_price") is not None:
        args["min_price"] = constraints["min_price"]
    if constraints.get("min_rating") is not None:
        args["min_rating"] = constraints["min_rating"]
    if re.search(r"\bin stock\b|\bavailable\b", lowered):
        args["in_stock_only"] = True

    if not any(k in args for k in ("category", "subcategory", "brand")):
        words = [w for w in re.findall(r"[A-Za-z0-9]+", text) if len(w) > 2][:3]
        args["query"] = " ".join(words)

    result = tools.run_tool("search_products", args)
    products = result.get("products", [])
    if result.get("error"):
        return {
            "message": "**Catalog temporarily unavailable**\n\nI could not retrieve the requested catalog records just now. Please try again in a moment.",
            "products": [],
        }
    if not products:
        return {
            "message": (
                "**No matching catalog records found**\n\n"
                "I could not locate products that match this request. Please check the product ID or spelling, "
                "or refine the search with a valid brand, category, subcategory, price, or rating."
            ),
            "products": [],
        }

    titles = {
        "price_asc": "Cheapest matches", "price_desc": "Most expensive matches",
        "reviews": "Most reviewed matches", "discount": "Biggest discounts",
        "rating": "Top rated matches",
    }
    lines = [f"**{titles[sort]}** — {result['total_matching_products']:,} products match:"]
    lines += [_line(i, p) for i, p in enumerate(products, 1)]
    return {"message": "\n".join(lines), "products": products}


def _details(product_id):
    result = tools.run_tool("get_product_details", {"product_id": product_id})
    if result.get("error"):
        return {
            "message": (
                f"**Product record not available**\n\n"
                f"I could not locate a product with ID **{product_id.upper()}**. Please verify the ID and try again."
            ),
            "products": [],
        }
    p = result["products"][0]
    lines = [
        f"**{p.get('brand', '')} {p.get('subcategory', '')}** ({p.get('product_id')})",
        f"- Price: **{_rupees(p.get('final_price'))}** (MRP {_rupees(p.get('price'))}, {p.get('discount', 0)}% off)",
        f"- Rating: **{p.get('rating', '—')}** from {p.get('review_count', 0)} reviews",
        f"- Stock: **{p.get('stock', 0)}**",
    ]
    if result.get("orders") is not None:
        lines.append(f"- Orders: **{result['orders']}** · Returned: **{result.get('returned_orders', 0)}**")
    return {"message": "\n".join(lines), "products": [p]}


def _compare(ids):
    result = tools.run_tool("compare_products", {"product_ids": ids})
    if result.get("error"):
        return {
            "message": "**Comparison could not be completed**\n\nPlease provide two or more valid product IDs, such as `P12345` and `P67890`.",
            "products": [],
        }
    rows = result["products"]
    lines = ["| Product | Price | Rating | Reviews | Stock |", "|---|---|---|---|---|"]
    for p in rows:
        lines.append(
            f"| {p['product_id']} ({p.get('brand', '')}) | {_rupees(p.get('final_price'))} | "
            f"{p.get('rating', '—')} | {p.get('review_count', 0)} | {p.get('stock', 0)} |"
        )
    w = result.get("winners", {})
    if w:
        lines.append(f"\n**Cheapest:** {w['lowest_price']} · **Best rated:** {w['highest_rating']}")
    return {"message": "\n".join(lines), "products": rows}


def _group_stats(field, metric, entities, overall=False):
    args = _filters(entities)
    if not overall:
        args.update(group_by=field, metric=metric, top_n=8)
    result = tools.run_tool("catalog_stats", args)
    if result.get("summary") is not None:
        s = result["summary"]
        return {
            "message": f"Across **{s.get('products', 0):,}** products the average price is **{_rupees(s.get('avg_price'))}** "
                       f"(range {_rupees(s.get('min_price'))} – {_rupees(s.get('max_price'))}).",
            "products": [],
        }
    rows = result.get("rows", [])
    if not rows:
        return {
            "message": "**No matching data available**\n\nThere are no records available for the selected criteria.",
            "products": [],
        }
    title = "Products per" if metric == "count" else "Average price per"
    lines = [f"**{title} {field}:**"]
    for r in rows:
        value = f"{r[metric]:,}" if metric == "count" else _rupees(r[metric])
        lines.append(f"- {r[field]}: **{value}**")
    return {"message": "\n".join(lines), "products": []}


def _analytics(metric):
    result = tools.run_tool("order_analytics", {"metric": metric})
    rows = result.get("rows", [])
    if result.get("error") or not rows:
        return {
            "message": "**No matching operational data available**\n\nI could not find records that match this request. Please review the wording or try a different filter.",
            "products": [],
        }
    lines = [f"**{metric.replace('_', ' ').title()}** (from {result['total_records']:,} {result['source'].lower()} records):"]
    for r in rows[:10]:
        extra = f", avg {r['avg_shipping_days']} days" if "avg_shipping_days" in r else ""
        lines.append(f"- {r['value']}: **{r['records']:,}** ({r['share_percent']}%){extra}")
    return {"message": "\n".join(lines), "products": []}
