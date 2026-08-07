"""
Shipping Page
Table of shipping records. There is no crud module for Shipping
yet, so this queries the collection directly via config.mongodb.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from gui.widgets.table import DataTable
from gui.widgets.notification import show_notification

from config.mongodb import db

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

    def showEvent(self, event):
        super().showEvent(event)
        self.load_shipping()
