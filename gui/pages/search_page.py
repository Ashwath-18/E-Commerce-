"""
Search Page
Unified UI over search/search_products.py and search/filter_products.py.

NOTE: This file didn't exist in the uploaded gui/pages/ folder —
the sidebar has a "Search" nav item pointing to it, so it's added
here to keep the app from crashing on that page.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QLineEdit, QPushButton, QFrame, QScrollArea
)
from PySide6.QtCore import Qt
from html import escape

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
    get_product_overview,
    get_user_overview,
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
    "User by ID": ("input", ORDER_COLUMNS),
    "Orders by User ID": ("input", ORDER_COLUMNS),
    "Sellers by Min Rating": ("input", SELLER_COLUMNS),
    "In-Stock Products": ("none", PRODUCT_COLUMNS),
    "Returned Orders": ("none", ORDER_COLUMNS),
    "Delivered Orders": ("none", ORDER_COLUMNS),
}


class SearchPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        self.scroll_area.setWidget(content)
        outer_layout.addWidget(self.scroll_area)

        layout = QVBoxLayout(content)
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

        # ---------------- Product Detail Panel ----------------

        self.product_detail_card = QFrame()
        self.product_detail_card.setObjectName("Card")
        detail_layout = QVBoxLayout(self.product_detail_card)
        detail_layout.setContentsMargins(22, 18, 22, 18)

        self.product_detail = QLabel()
        self.product_detail.setWordWrap(True)
        self.product_detail.setTextFormat(Qt.RichText)
        detail_layout.addWidget(self.product_detail)

        self.product_detail_card.hide()
        layout.addWidget(self.product_detail_card)

        self.user_detail_card = QFrame()
        self.user_detail_card.setObjectName("Card")
        user_detail_layout = QVBoxLayout(self.user_detail_card)
        user_detail_layout.setContentsMargins(22, 18, 22, 18)

        self.user_detail = QLabel()
        self.user_detail.setWordWrap(True)
        self.user_detail.setTextFormat(Qt.RichText)
        user_detail_layout.addWidget(self.user_detail)

        self.user_detail_card.hide()
        layout.addWidget(self.user_detail_card)

        # ---------------- Results Table ----------------

        table_card = QFrame()
        table_card.setObjectName("Card")
        table_card.setMinimumHeight(320)
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
        self.product_detail_card.hide()
        self.user_detail_card.hide()
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
            self.product_detail_card.hide()
            self.user_detail_card.hide()

            if mode == "Product by ID":
                overview = get_product_overview(query)
                results = [overview["product"]] if overview else []
                if overview:
                    self._show_product_overview(overview)
            elif mode == "User by ID":
                overview = get_user_overview(query)
                results = overview["orders"] if overview else []
                if overview:
                    self._show_user_overview(overview)
            else:
                results = self._execute(mode, query)

            self.table.load_data(results)

            if not results:
                show_notification(self, "No results found.", "warning")
        except Exception as e:
            show_notification(self, f"Search failed: {e}", "error")

    def _show_product_overview(self, overview):
        """Display all stored product fields and linked-record summaries."""
        product = overview["product"]

        def value(field):
            return escape(str(product.get(field, "—")))

        statuses = ", ".join(overview["delivery_statuses"]) or "—"
        payment_methods = ", ".join(overview["payment_methods"]) or "—"
        average_rating = overview["average_review_rating"]
        average_rating = average_rating if average_rating is not None else "—"

        self.product_detail.setText(
            "<h3 style='margin:0 0 10px 0;'>Product Details</h3>"
            "<table cellspacing='6'>"
            f"<tr><td><b>Product ID</b></td><td>{value('product_id')}</td>"
            f"<td><b>Brand</b></td><td>{value('brand')}</td></tr>"
            f"<tr><td><b>Category</b></td><td>{value('category')}</td>"
            f"<td><b>Subcategory</b></td><td>{value('subcategory')}</td></tr>"
            f"<tr><td><b>Original Price</b></td><td>{value('price')}</td>"
            f"<td><b>Discount</b></td><td>{value('discount')}%</td></tr>"
            f"<tr><td><b>Final Price</b></td><td>{value('final_price')}</td>"
            f"<td><b>Product Stock</b></td><td>{value('stock')}</td></tr>"
            f"<tr><td><b>Product Rating</b></td><td>{value('rating')}</td>"
            f"<td><b>Listed Review Count</b></td><td>{value('review_count')}</td></tr>"
            "</table>"
            "<h3 style='margin:12px 0 10px 0;'>Related Records</h3>"
            "<table cellspacing='6'>"
            f"<tr><td><b>Inventory Stock</b></td><td>{overview['inventory_stock']}</td>"
            f"<td><b>Orders</b></td><td>{overview['order_count']}</td></tr>"
            f"<tr><td><b>Review Records</b></td><td>{overview['review_records']}</td>"
            f"<td><b>Average Review Rating</b></td><td>{average_rating}</td></tr>"
            f"<tr><td><b>Shipping Records</b></td><td>{overview['shipping_count']}</td>"
            f"<td><b>Delivery Statuses</b></td><td>{escape(statuses)}</td></tr>"
            f"<tr><td><b>Payment Records</b></td><td>{overview['payment_count']}</td>"
            f"<td><b>Payment Methods</b></td><td>{escape(payment_methods)}</td></tr>"
            f"<tr><td><b>Returned Orders</b></td><td>{overview['return_count']}</td>"
            f"<td><b>Order Items</b></td><td>{overview['order_item_count']}</td></tr>"
            "</table>"
        )
        self.product_detail_card.show()

    def _show_user_overview(self, overview):
        """Display a user and summary data for their linked records."""
        user_id = escape(str(overview["user"].get("user_id", "—")))
        statuses = ", ".join(overview["delivery_statuses"]) or "—"
        payment_methods = ", ".join(overview["payment_methods"]) or "—"

        self.user_detail.setText(
            "<h3 style='margin:0 0 10px 0;'>User Details</h3>"
            "<table cellspacing='6'>"
            f"<tr><td><b>User ID</b></td><td>{user_id}</td>"
            f"<td><b>Total Orders</b></td><td>{len(overview['orders'])}</td></tr>"
            f"<tr><td><b>Unique Products Purchased</b></td><td>{overview['unique_products']}</td>"
            f"<td><b>Order Items</b></td><td>{overview['order_item_count']}</td></tr>"
            "</table>"
            "<h3 style='margin:12px 0 10px 0;'>Related Records</h3>"
            "<table cellspacing='6'>"
            f"<tr><td><b>Shipping Records</b></td><td>{overview['shipping_count']}</td>"
            f"<td><b>Delivery Statuses</b></td><td>{escape(statuses)}</td></tr>"
            f"<tr><td><b>Payment Records</b></td><td>{overview['payment_count']}</td>"
            f"<td><b>Payment Methods</b></td><td>{escape(payment_methods)}</td></tr>"
            f"<tr><td><b>Returned Orders</b></td><td>{overview['return_count']}</td>"
            "<td><b>Order List</b></td><td>Shown below</td></tr>"
            "</table>"
        )
        self.user_detail_card.show()

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
