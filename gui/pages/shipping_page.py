"""
Shipping Page
Table of shipping records, searched through search/search_products.py.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout
from gui.widgets.search_bar import SearchBar
from gui.widgets.sort_button import SortButton
from gui.widgets.table import DataTable
from gui.widgets.notification import show_notification
from gui.widgets.pagination import PaginationControls
from gui.widgets.page_header import PageHeader, FilterBar, make_table_card

from search.search_products import get_shipping_page

PAGE_SIZE = 100

SORT_OPTIONS = [
    ("user_id", "User ID", "text"),
    ("product_id", "Product ID", "text"),
    ("shipping_time_days", "Shipping Days", "number"),
    ("location", "Location", "text"),
    ("delivery_status", "Delivery Status", "text"),
]

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

        self.current_query = ""
        self.current_page = 1

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 8, 8)
        layout.setSpacing(16)

        layout.addWidget(
            PageHeader("Shipping", "Track shipment status and delivery times.", "shipping")
        )

        self.search_bar = SearchBar(
            placeholder="Search user, product, location, or status..."
        )
        self.search_bar.search_triggered.connect(self._search)

        self.sort_button = SortButton(SORT_OPTIONS)
        self.sort_button.sort_requested.connect(self._sort)

        filters = FilterBar()
        filters.row.addWidget(self.search_bar, stretch=1)
        filters.row.addWidget(self.sort_button)
        layout.addWidget(filters)

        self.table = DataTable(COLUMNS)
        self.table.set_empty_message("No shipments found", "Try a different user, product, location or status.")
        layout.addWidget(make_table_card(self.table), stretch=1)

        self.pagination = PaginationControls(PAGE_SIZE)
        self.pagination.page_changed.connect(self.load_shipping)
        layout.addWidget(self.pagination)

        self.load_shipping()

    def load_shipping(self, page=1):
        try:
            records, total = get_shipping_page(
                page, PAGE_SIZE, self.current_query
            )
            self.current_page = page
            self.table.load_data(records)
            self.pagination.set_pagination(total, page)
        except Exception as e:
            show_notification(self, f"Could not load shipping data: {e}", "error")

    def _search(self, query):
        if not query:
            self.current_query = ""
            self.load_shipping(1)
            return

        try:
            self.current_query = query
            self.load_shipping(1)
        except Exception as e:
            show_notification(self, f"Search failed: {e}", "error")

    def _sort(self, field, descending):
        self.table.sort_data(field, descending, field == "shipping_time_days")

    def showEvent(self, event):
        super().showEvent(event)
        self.load_shipping(self.current_page)
