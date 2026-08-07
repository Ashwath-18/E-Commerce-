"""
Reviews Page
Table of product reviews. Queries the Reviews collection directly
via config.mongodb, since no crud module exists for it yet.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from gui.widgets.table import DataTable
from gui.widgets.notification import show_notification

from config.mongodb import db

DISPLAY_LIMIT = 300

COLUMNS = [
    ("product_id", "Product ID"),
    ("rating", "Rating"),
    ("review_count", "Review Count"),
]


class ReviewsPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        title = QLabel("Reviews")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Browse product reviews and ratings.")
        subtitle.setObjectName("PageSubtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        table_card = QFrame()
        table_card.setObjectName("Card")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(12, 12, 12, 12)

        self.table = DataTable(COLUMNS)
        table_layout.addWidget(self.table)

        layout.addWidget(table_card, stretch=1)

        self.load_reviews()

    def load_reviews(self):
        try:
            records = list(
                db["Reviews"].find({}, {"_id": 0}).limit(DISPLAY_LIMIT)
            )
            self.table.load_data(records)
        except Exception as e:
            show_notification(self, f"Could not load reviews: {e}", "error")

    def showEvent(self, event):
        super().showEvent(event)
        self.load_reviews()
