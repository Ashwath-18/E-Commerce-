"""
User Model
Represents a User document in MongoDB
"""


class User:
    def __init__(self, user_id):
        self.user_id = user_id

    def to_dict(self):
        return {
            "user_id": self.user_id
        }

    def __str__(self):
        return f"User({self.user_id})"