"""
Search Page
Unified UI over search/search_products.py and search/filter_products.py.

NOTE: This file didn't exist in the uploaded gui/pages/ folder —
the sidebar has a "Search" nav item pointing to it, so it's added
here to keep the app from crashing on that page.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QLineEdit, QPushButton, QFrame
)
from PySide6.QtCore import Qt

from gui.widgets.table import DataTable
from gui.widgets.notification import show_notification

from search.search_products import (
    search_product_by_id,
    search_products_by_brand,
    search_products_by_category,
    search_products_by_subcategory,
    search_products_by_rating,
    search_orders_by_user,
    search_sellers_by_rating,
)
from search.filter_products import (
    filter_products_in_stock,
    filter_returned_orders,
    filter_delivered_orders,
)

PRODUCT_COLUMNS = [
    ("product_id", "Product ID"), ("category", "Category"),
    ("subcategory", "Subcategory"), ("brand", "Brand"),
    ("final_price", "Price"), ("stock", "Stock"), ("rating", "Rating"),
]

ORDER_COLUMNS = [
    ("user_id", "User ID"), ("product_id", "Product ID"),
    ("payment_method", "Payment"), ("delivery_status", "Status"),
]

SELLER_COLUMNS = [
    ("seller_id", "Seller ID"), ("seller_rating", "Rating"),
]

MODES = {
    "Product by ID": ("input", PRODUCT_COLUMNS),
    "Products by Brand": ("input", PRODUCT_COLUMNS),
    "Products by Category": ("input", PRODUCT_COLUMNS),
    "Products by Subcategory": ("input", PRODUCT_COLUMNS),
    "Products by Min Rating": ("input", PRODUCT_COLUMNS),
    "Orders by User ID": ("input", ORDER_COLUMNS),
    "Sellers by Min Rating": ("input", SELLER_COLUMNS),
    "In-Stock Products": ("none", PRODUCT_COLUMNS),
    "Returned Orders": ("none", ORDER_COLUMNS),
    "Delivered Orders": ("none", ORDER_COLUMNS),
}


class SearchPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        title = QLabel("Search & Filter")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Look up products, orders, and sellers.")
        subtitle.setObjectName("PageSubtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        # ---------------- Controls ----------------

        controls_row = QHBoxLayout()

        self.mode_dropdown = QComboBox()
        self.mode_dropdown.addItems(list(MODES.keys()))
        self.mode_dropdown.currentTextChanged.connect(self._on_mode_changed)

        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Enter search value...")
        self.query_input.returnPressed.connect(self._run_search)

        search_btn = QPushButton("Search")
        search_btn.setObjectName("PrimaryButton")
        search_btn.setCursor(Qt.PointingHandCursor)
        search_btn.clicked.connect(self._run_search)

        controls_row.addWidget(self.mode_dropdown)
        controls_row.addWidget(self.query_input, stretch=1)
        controls_row.addWidget(search_btn)

        layout.addLayout(controls_row)

        # ---------------- Results Table ----------------

        table_card = QFrame()
        table_card.setObjectName("Card")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(12, 12, 12, 12)

        self.table = DataTable(PRODUCT_COLUMNS)
        table_layout.addWidget(self.table)

        layout.addWidget(table_card, stretch=1)

        self._on_mode_changed(self.mode_dropdown.currentText())

    def _on_mode_changed(self, mode):
        input_type, columns = MODES[mode]
        self.query_input.setEnabled(input_type == "input")
        self.query_input.clear()
        self.table.columns = columns
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels([label for _, label in columns])
        self.table.load_data([])

    def _run_search(self):
        mode = self.mode_dropdown.currentText()
        query = self.query_input.text().strip()
        input_type, columns = MODES[mode]

        if input_type == "input" and not query:
            show_notification(self, "Enter a search value first.", "warning")
            return

        try:
            results = self._execute(mode, query)

            if mode == "Product by ID":
                results = [results] if results else []

            self.table.load_data(results)

            if not results:
                show_notification(self, "No results found.", "warning")
        except Exception as e:
            show_notification(self, f"Search failed: {e}", "error")

    def _execute(self, mode, query):
        if mode == "Product by ID":
            return search_product_by_id(query)
        if mode == "Products by Brand":
            return search_products_by_brand(query)
        if mode == "Products by Category":
            return search_products_by_category(query)
        if mode == "Products by Subcategory":
            return search_products_by_subcategory(query)
        if mode == "Products by Min Rating":
            return search_products_by_rating(float(query))
        if mode == "Orders by User ID":
            return search_orders_by_user(query)
        if mode == "Sellers by Min Rating":
            return search_sellers_by_rating(float(query))
        if mode == "In-Stock Products":
            return filter_products_in_stock()
        if mode == "Returned Orders":
            return filter_returned_orders()
        if mode == "Delivered Orders":
            return filter_delivered_orders()
        return []
