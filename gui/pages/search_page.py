"""
Search Page
Unified UI over search/search_products.py and search/filter_products.py.

NOTE: This file didn't exist in the uploaded gui/pages/ folder —
the sidebar has a "Search" nav item pointing to it, so it's added
here to keep the app from crashing on that page.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QComboBox,
    QLineEdit, QPushButton, QFrame, QScrollArea
)
from PySide6.QtCore import Qt

from gui.widgets import icons
from gui.widgets.table import DataTable
from gui.widgets.detail_panel import DetailPanel
from gui.widgets.page_header import PageHeader, FilterBar, make_table_card
from gui.widgets.notification import show_notification
from gui.widgets.sort_button import SortButton
from gui.widgets.pagination import PaginationControls

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
    get_search_results_page,
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

NUMERIC_FIELDS = {
    "final_price", "stock", "rating", "review_count", "seller_rating",
}

DATE_FIELDS = {"purchase_date"}
PAGE_SIZE = 100

MODES = {
    "Product by ID": ("input", PRODUCT_COLUMNS),
    "Products by Brand": ("input", PRODUCT_COLUMNS),
    "Products by Category": ("input", PRODUCT_COLUMNS),
    "Products by Subcategory": ("input", PRODUCT_COLUMNS),
    "Products by Min Rating": ("input", PRODUCT_COLUMNS),
    "User by ID": ("input", ORDER_COLUMNS),
    "Orders by User ID": ("input", ORDER_COLUMNS),
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
        self.scroll_area.viewport().setAutoFillBackground(False)

        content = QWidget()
        self.scroll_area.setWidget(content)
        outer_layout.addWidget(self.scroll_area)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(4, 4, 8, 16)
        layout.setSpacing(16)

        layout.addWidget(
            PageHeader(
                "Search & Filter", "Look up products, orders, and sellers.", "search"
            )
        )

        # ---------------- Controls ----------------

        self.mode_dropdown = QComboBox()
        self.mode_dropdown.setMinimumHeight(46)
        self.mode_dropdown.setMinimumWidth(230)
        self.mode_dropdown.addItems(list(MODES.keys()))
        self.mode_dropdown.currentTextChanged.connect(self._on_mode_changed)
        self.current_mode = self.mode_dropdown.currentText()
        self.current_query = ""
        self.current_page = 1

        self.query_input = QLineEdit()
        self.query_input.setObjectName("SearchBar")
        self.query_input.setPlaceholderText("Enter search value...")
        self.query_input.setFixedHeight(46)
        self.query_input.returnPressed.connect(self._run_search)
        search_action = self.query_input.addAction(
            icons.icon("search", 18, "muted"), QLineEdit.LeadingPosition
        )
        icons.bind(search_action, "search", 18, "muted")

        search_btn = QPushButton("Search")
        search_btn.setObjectName("PrimaryButton")
        search_btn.setCursor(Qt.PointingHandCursor)
        search_btn.setFixedHeight(46)
        search_btn.clicked.connect(self._run_search)

        self.sort_button = SortButton()
        self.sort_button.sort_requested.connect(self._sort)

        controls = FilterBar()
        controls.row.addWidget(self.mode_dropdown)
        controls.row.addWidget(self.query_input, stretch=1)
        controls.row.addWidget(search_btn)
        controls.row.addWidget(self.sort_button)
        layout.addWidget(controls)

        # ---------------- Detail Panels ----------------

        self.product_detail_card = DetailPanel(columns=4)
        self.product_detail_card.hide()
        layout.addWidget(self.product_detail_card)

        self.user_detail_card = DetailPanel(columns=4)
        self.user_detail_card.hide()
        layout.addWidget(self.user_detail_card)

        # ---------------- Results Table ----------------

        self.table = DataTable(PRODUCT_COLUMNS)
        table_card = make_table_card(self.table)
        table_card.setMinimumHeight(340)
        layout.addWidget(table_card, stretch=1)

        self.pagination = PaginationControls(PAGE_SIZE)
        self.pagination.page_changed.connect(self._load_results)
        layout.addWidget(self.pagination)

        self._on_mode_changed(self.mode_dropdown.currentText())

    def _on_mode_changed(self, mode):
        input_type, columns = MODES[mode]
        self.query_input.setEnabled(input_type == "input")
        self.query_input.clear()
        self.current_mode = mode
        self.current_query = ""
        self.current_page = 1
        self.product_detail_card.hide()
        self.user_detail_card.hide()
        self.table.columns = columns
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels([label for _, label in columns])
        self.table.set_empty_message(
            "Search the catalog",
            "Pick a lookup type, enter a value and press Search.",
        )
        self.table.load_data([])
        self._set_sort_options(columns)
        self.pagination.set_pagination(0, 1)

    def _run_search(self):
        mode = self.mode_dropdown.currentText()
        query = self.query_input.text().strip()
        input_type, columns = MODES[mode]

        if input_type == "input" and not query:
            show_notification(self, "Enter a search value first.", "warning")
            return

        self.current_mode = mode
        self.current_query = query
        self._load_results(1)

    def _load_results(self, page=1):
        """Load one results page while preserving the active search mode."""
        try:
            self.product_detail_card.hide()
            self.user_detail_card.hide()

            if self.current_mode == "Product by ID":
                overview = get_product_overview(self.current_query)
                results = [overview["product"]] if overview else []
                total = len(results)
                if overview:
                    self._show_product_overview(overview)
            elif self.current_mode == "User by ID":
                overview = get_user_overview(self.current_query)
                if overview:
                    self._show_user_overview(overview)
                results, total = get_search_results_page(
                    self.current_mode, self.current_query, page, PAGE_SIZE
                )
            else:
                results, total = get_search_results_page(
                    self.current_mode, self.current_query, page, PAGE_SIZE
                )

            self.current_page = page
            self.table.load_data(results)
            self.pagination.set_pagination(total, page)

            if not results and page == 1:
                self.table.set_empty_message(
                    "No results found",
                    "Nothing matched that value. Check it and try again.",
                )
                self.table.load_data([])
                show_notification(self, "No results found.", "warning")
        except Exception as e:
            show_notification(self, f"Search failed: {e}", "error")

    def _show_product_overview(self, overview):
        """Display all stored product fields and linked-record summaries."""
        product = overview["product"]

        def value(field):
            return str(product.get(field, "—"))

        statuses = ", ".join(overview["delivery_statuses"]) or "—"
        payment_methods = ", ".join(overview["payment_methods"]) or "—"
        average_rating = overview["average_review_rating"]
        average_rating = average_rating if average_rating is not None else "—"

        self.product_detail_card.set_sections([
            ("Product Details", [
                ("Product ID", value("product_id")),
                ("Brand", value("brand")),
                ("Category", value("category")),
                ("Subcategory", value("subcategory")),
                ("Original Price", value("price")),
                ("Discount", f"{value('discount')}%"),
                ("Final Price", value("final_price")),
                ("Product Stock", value("stock")),
                ("Product Rating", value("rating")),
                ("Listed Review Count", value("review_count")),
            ]),
            ("Related Records", [
                ("Inventory Stock", overview["inventory_stock"]),
                ("Orders", overview["order_count"]),
                ("Review Records", overview["review_records"]),
                ("Average Review Rating", average_rating),
                ("Shipping Records", overview["shipping_count"]),
                ("Delivery Statuses", statuses),
                ("Payment Records", overview["payment_count"]),
                ("Payment Methods", payment_methods),
                ("Returned Orders", overview["return_count"]),
                ("Order Items", overview["order_item_count"]),
            ]),
        ])
        self.product_detail_card.show()

    def _show_user_overview(self, overview):
        """Display a user and summary data for their linked records."""
        user_id = str(overview["user"].get("user_id", "—"))
        statuses = ", ".join(overview["delivery_statuses"]) or "—"
        payment_methods = ", ".join(overview["payment_methods"]) or "—"

        self.user_detail_card.set_sections([
            ("User Details", [
                ("User ID", user_id),
                ("Total Orders", len(overview["orders"])),
                ("Unique Products Purchased", overview["unique_products"]),
                ("Order Items", overview["order_item_count"]),
            ]),
            ("Related Records", [
                ("Shipping Records", overview["shipping_count"]),
                ("Delivery Statuses", statuses),
                ("Payment Records", overview["payment_count"]),
                ("Payment Methods", payment_methods),
                ("Returned Orders", overview["return_count"]),
                ("Order List", "Shown below"),
            ]),
        ])
        self.user_detail_card.show()

    def _set_sort_options(self, columns):
        options = []
        for field, label in columns:
            if field in NUMERIC_FIELDS:
                field_kind = "number"
            elif field in DATE_FIELDS:
                field_kind = "date"
            else:
                field_kind = "text"
            options.append((field, label, field_kind))
        self.sort_button.set_sort_options(options)

    def _sort(self, field, descending):
        self.table.sort_data(field, descending, field in NUMERIC_FIELDS)
