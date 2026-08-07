"""
Orders Page
Table of orders, searchable by user ID.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from gui.widgets.search_bar import SearchBar
from gui.widgets.table import DataTable
from gui.widgets.notification import show_notification

from crud.read import get_all_orders
from search.search_products import search_orders_by_user

DISPLAY_LIMIT = 300

COLUMNS = [
    ("user_id", "User ID"),
    ("product_id", "Product ID"),
    ("purchase_date", "Purchase Date"),
    ("payment_method", "Payment"),
    ("delivery_status", "Status"),
    ("is_returned", "Returned"),
]


class OrdersPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        title = QLabel("Orders")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Browse and search customer orders.")
        subtitle.setObjectName("PageSubtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        self.search_bar = SearchBar(placeholder="Search orders by User ID...")
        self.search_bar.search_triggered.connect(self._search)
        layout.addWidget(self.search_bar)

        table_card = QFrame()
        table_card.setObjectName("Card")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(12, 12, 12, 12)

        self.table = DataTable(COLUMNS)
        table_layout.addWidget(self.table)

        layout.addWidget(table_card, stretch=1)

        self.load_orders()

    def load_orders(self):
        try:
            orders = get_all_orders()
            self.table.load_data(orders[:DISPLAY_LIMIT])
        except Exception as e:
            show_notification(self, f"Could not load orders: {e}", "error")

    def _search(self, user_id):
        if not user_id:
            self.load_orders()
            return

        try:
            results = search_orders_by_user(user_id)
            self.table.load_data(results[:DISPLAY_LIMIT])
            if not results:
                show_notification(self, "No orders found for that user.", "warning")
        except Exception as e:
            show_notification(self, f"Search failed: {e}", "error")

    def showEvent(self, event):
        super().showEvent(event)
        self.load_orders()
