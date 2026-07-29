"""
SubCategory Model
Represents a SubCategory document in MongoDB
"""


class SubCategory:
    def __init__(self, category, subcategory):
        self.category = category
        self.subcategory = subcategory

    def to_dict(self):
        return {
            "category": self.category,
            "subcategory": self.subcategory
        }

    def __str__(self):
        return f"SubCategory({self.subcategory})"