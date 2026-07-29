"""
Category Model
Represents a Category document in MongoDB
"""


class Category:
    def __init__(self, category):
        self.category = category

    def to_dict(self):
        return {
            "category": self.category
        }

    def __str__(self):
        return f"Category({self.category})"