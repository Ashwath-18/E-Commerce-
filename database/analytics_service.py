"""MongoDB aggregation queries used by Cartify analytics reports."""

from config.mongodb import db


class AnalyticsService:
    def __init__(self):
        self.db = db

    @staticmethod
    def _ranked(collection, field, limit=5, ascending=False):
        direction = 1 if ascending else -1
        return list(
            collection.find({}, {"_id": 0})
            .sort(field, direction)
            .limit(limit)
        )

    def get_sales_report(self):
        order_values = [
            {"$lookup": {"from": "Products", "localField": "product_id", "foreignField": "product_id", "as": "product"}},
            {"$unwind": "$product"},
        ]
        summary = list(self.db.Orders.aggregate(order_values + [{"$group": {
            "_id": None,
            "total_orders": {"$sum": 1},
            "total_revenue": {"$sum": "$product.final_price"},
            "average_order_value": {"$avg": "$product.final_price"},
            "returned_orders": {"$sum": {"$cond": ["$is_returned", 1, 0]}},
            "delivered_orders": {"$sum": {"$cond": [{"$eq": ["$delivery_status", "Delivered"]}, 1, 0]}},
        }}]))
        totals = summary[0] if summary else {}

        categories = list(self.db.Orders.aggregate(order_values + [
            {"$group": {"_id": "$product.category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5},
        ]))
        return {
            "total_orders": totals.get("total_orders", 0),
            "total_revenue": totals.get("total_revenue", 0),
            "average_order_value": totals.get("average_order_value", 0),
            "top_category": categories[0]["_id"] if categories else "N/A",
            "categories": [(item["_id"] or "Uncategorized", item["count"]) for item in categories],
            "status": [("Delivered", totals.get("delivered_orders", 0)), ("Returned", totals.get("returned_orders", 0))],
        }

    def get_inventory_report(self):
        summary = list(self.db.Products.aggregate([{"$group": {
            "_id": None,
            "products": {"$sum": 1},
            "out_of_stock": {"$sum": {"$cond": [{"$lte": ["$stock", 0]}, 1, 0]}},
            "low_stock": {"$sum": {"$cond": [{"$and": [{"$gt": ["$stock", 0]}, {"$lte": ["$stock", 10]}]}, 1, 0]}},
            "average_stock": {"$avg": "$stock"},
        }}]))
        totals = summary[0] if summary else {}
        products = totals.get("products", 0)
        out = totals.get("out_of_stock", 0)
        low = totals.get("low_stock", 0)
        return {
            "products": products,
            "out_of_stock": out,
            "low_stock": low,
            "average_stock": totals.get("average_stock", 0),
            "status": [("Out of Stock", out), ("Low Stock", low), ("Healthy Stock", max(0, products - out - low))],
        }

    def get_customer_report(self):
        activity = list(self.db.Orders.aggregate([
            {"$group": {"_id": "$user_id", "orders": {"$sum": 1}}},
            {"$sort": {"orders": -1}}, {"$limit": 5},
        ]))
        spend = list(self.db.Orders.aggregate([
            {"$lookup": {"from": "Products", "localField": "product_id", "foreignField": "product_id", "as": "product"}},
            {"$unwind": "$product"},
            {"$group": {"_id": "$user_id", "spent": {"$sum": "$product.final_price"}}},
            {"$sort": {"spent": -1}}, {"$limit": 5},
        ]))
        return {
            "total_users": self.db.Users.count_documents({}),
            "most_active_user": activity[0]["_id"] if activity else "N/A",
            "top_buyer": spend[0]["_id"] if spend else "N/A",
            "activity": [(item["_id"], item["orders"]) for item in activity],
            "buyers": [(item["_id"], item["spent"]) for item in spend],
        }

    def get_seller_report(self):
        summary = list(self.db.Sellers.aggregate([{"$group": {"_id": None, "average_rating": {"$avg": "$seller_rating"}}}]))
        sellers = list(self.db.Sellers.aggregate([
            {"$sample": {"size": 5}},
            {"$project": {"_id": 0, "seller_id": 1, "seller_rating": 1}},
        ]))
        return {
            "average_rating": (summary[0].get("average_rating", 0) if summary else 0),
            "sellers": [(item.get("seller_id", "N/A"), item.get("seller_rating", 0)) for item in sellers],
        }

    def get_review_report(self):
        summary = list(self.db.Reviews.aggregate([{"$group": {"_id": None, "average_rating": {"$avg": "$rating"}}}]))
        category_ratings = list(self.db.Reviews.aggregate([
            {"$lookup": {
                "from": "Products",
                "localField": "product_id",
                "foreignField": "product_id",
                "as": "product",
            }},
            {"$unwind": "$product"},
            {"$group": {
                "_id": "$product.category",
                "average_rating": {"$avg": "$rating"},
            }},
        ]))
        high = sorted(category_ratings, key=lambda item: item["average_rating"], reverse=True)[:5]
        low = sorted(category_ratings, key=lambda item: item["average_rating"])[:5]
        return {
            "average_rating": (summary[0].get("average_rating", 0) if summary else 0),
            "highest": [(item.get("_id") or "Uncategorized", item["average_rating"]) for item in high],
            "lowest": [(item.get("_id") or "Uncategorized", item["average_rating"]) for item in low],
        }

    def get_payment_report(self):
        results = list(self.db.Payments.aggregate([{"$group": {"_id": "$payment_method", "count": {"$sum": 1}}}]))
        raw = {item["_id"]: item["count"] for item in results}
        return [
            ("Cash", raw.get("Cash", 0)),
            ("UPI", raw.get("UPI", 0)),
            ("Credit Card", raw.get("Credit Card", 0)),
            ("Debit Card", raw.get("Debit Card", 0)),
        ]
