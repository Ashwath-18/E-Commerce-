"""
Shipping Page
Table of shipping records. There is no crud module for Shipping
yet, so this queries the collection directly via config.mongodb.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from gui.widgets.search_bar import SearchBar
from gui.widgets.table import DataTable
from gui.widgets.notification import show_notification

from config.mongodb import db
from search.search_products import search_shipping

DISPLAY_LIMIT = 300

COLUMNS = [
    ("user_id", "User ID"),
    ("product_id", "Product ID"),
    ("shipping_time_days", "Shipping Days"),
    ("location", "Location"),
    ("delivery_status", "Status"),
]


class ShippingPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        title = QLabel("Shipping")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Track shipment status and delivery times.")
        subtitle.setObjectName("PageSubtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        self.search_bar = SearchBar(
            placeholder="Search user, product, location, or status..."
        )
        self.search_bar.search_triggered.connect(self._search)
        layout.addWidget(self.search_bar)

        table_card = QFrame()
        table_card.setObjectName("Card")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(12, 12, 12, 12)

        self.table = DataTable(COLUMNS)
        table_layout.addWidget(self.table)

        layout.addWidget(table_card, stretch=1)

        self.load_shipping()

    def load_shipping(self):
        try:
            records = list(
                db["Shipping"].find({}, {"_id": 0}).limit(DISPLAY_LIMIT)
            )
            self.table.load_data(records)
        except Exception as e:
            show_notification(self, f"Could not load shipping data: {e}", "error")

    def _search(self, query):
        if not query:
            self.load_shipping()
            return

        try:
            records = search_shipping(query)
            self.table.load_data(records[:DISPLAY_LIMIT])
            if not records:
                show_notification(self, "No shipping records found.", "warning")
        except Exception as e:
            show_notification(self, f"Search failed: {e}", "error")

    def showEvent(self, event):
        super().showEvent(event)
        self.load_shipping()
