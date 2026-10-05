"""
Products Page
Table of products with search-by-brand, add / edit / delete,
wired to crud/ and search/ backend modules.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton
)
from PySide6.QtCore import Qt

from gui.widgets import icons
from gui.widgets.search_bar import SearchBar
from gui.widgets.sort_button import SortButton
from gui.widgets.table import DataTable
from gui.widgets.notification import show_notification
from gui.widgets.pagination import PaginationControls
from gui.widgets.page_header import PageHeader, FilterBar, make_table_card

from gui.dialogs.add_product_dialog import AddProductDialog
from gui.dialogs.edit_product_dialog import EditProductDialog
from gui.dialogs.delete_dialog import confirm_delete

from crud.delete import delete_product
from search.search_products import get_products_page

PAGE_SIZE = 100

SORT_OPTIONS = [
    ("product_id", "Product ID", "text"),
    ("final_price", "Price", "number"),
    ("stock", "Stock", "number"),
    ("rating", "Rating", "number"),
]

COLUMNS = [
    ("product_id", "Product ID"),
    ("category", "Category"),
    ("subcategory", "Subcategory"),
    ("brand", "Brand"),
    ("final_price", "Price"),
    ("stock", "Stock"),
    ("rating", "Rating"),
]


class ProductsPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.selected_product = None
        self.current_query = ""
        self.current_page = 1

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 8, 8)
        layout.setSpacing(16)

        # ---------------- Header ----------------

        header = PageHeader("Products", "Manage your product catalog.", "products")

        self.add_btn = QPushButton("Add Product")
        self.add_btn.setObjectName("PrimaryButton")
        self.add_btn.setCursor(Qt.PointingHandCursor)
        icons.bind(self.add_btn, "plus", 18, "white")
        self.add_btn.clicked.connect(self._add_product)
        header.add_action(self.add_btn)

        layout.addWidget(header)

        # ---------------- Search Bar ----------------

        self.search_bar = SearchBar(
            placeholder="Search by product ID, brand, category, or subcategory..."
        )
        self.search_bar.search_triggered.connect(self._search)

        self.sort_button = SortButton(SORT_OPTIONS)
        self.sort_button.sort_requested.connect(self._sort)

        filters = FilterBar()
        filters.row.addWidget(self.search_bar, stretch=1)
        filters.row.addWidget(self.sort_button)
        layout.addWidget(filters)

        # ---------------- Table Card ----------------

        self.table = DataTable(COLUMNS)
        self.table.set_empty_message(
            "No products found", "Try a different search, or add a new product."
        )
        self.table.row_selected.connect(self._on_row_selected)
        layout.addWidget(make_table_card(self.table), stretch=1)

        self.pagination = PaginationControls(PAGE_SIZE)
        self.pagination.page_changed.connect(self.load_products)
        layout.addWidget(self.pagination)

        # ---------------- Action Row ----------------

        action_row = QHBoxLayout()
        action_row.addStretch()

        self.edit_btn = QPushButton("Edit Selected")
        self.edit_btn.setObjectName("SecondaryButton")
        self.edit_btn.setCursor(Qt.PointingHandCursor)
        icons.bind(self.edit_btn, "edit", 18, "muted", "primary")
        self.edit_btn.clicked.connect(self._edit_product)

        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.setObjectName("DangerButton")
        self.delete_btn.setCursor(Qt.PointingHandCursor)
        icons.bind(self.delete_btn, "trash", 18, "white")
        self.delete_btn.clicked.connect(self._delete_product)

        action_row.addWidget(self.edit_btn)
        action_row.addWidget(self.delete_btn)

        layout.addLayout(action_row)

        self.load_products()

    # ---------------- Data Loading ----------------

    def load_products(self, page=1):
        try:
            products, total = get_products_page(
                page, PAGE_SIZE, self.current_query
            )
            self.current_page = page
            self.table.load_data(products)
            self.pagination.set_pagination(total, page)
        except Exception as e:
            show_notification(self, f"Could not load products: {e}", "error")

    def _search(self, query):
        if not query:
            self.current_query = ""
            self.load_products(1)
            return

        try:
            self.current_query = query
            self.load_products(1)
        except Exception as e:
            show_notification(self, f"Search failed: {e}", "error")

    def _on_row_selected(self, row):
        self.selected_product = row

    def _sort(self, field, descending):
        numeric = field in {"final_price", "stock", "rating"}
        self.table.sort_data(field, descending, numeric)

    # ---------------- Actions ----------------

    def _add_product(self):
        dialog = AddProductDialog(self)
        if dialog.exec():
            show_notification(self, "Product added successfully.", "success")
            self.load_products(self.current_page)

    def _edit_product(self):
        if not self.selected_product:
            show_notification(self, "Select a product first.", "warning")
            return

        dialog = EditProductDialog(self.selected_product, self)
        if dialog.exec():
            show_notification(self, "Product updated.", "success")
            self.load_products(self.current_page)

    def _delete_product(self):
        if not self.selected_product:
            show_notification(self, "Select a product first.", "warning")
            return

        product_id = self.selected_product.get("product_id")

        if confirm_delete(self, f"product '{product_id}'"):
            try:
                if delete_product(product_id):
                    show_notification(self, "Product deleted.", "success")
                else:
                    show_notification(self, "Product not found.", "warning")
                self.selected_product = None
                self.load_products(self.current_page)
            except Exception as e:
                show_notification(self, f"Delete failed: {e}", "error")

    def showEvent(self, event):
        super().showEvent(event)
        self.load_products(self.current_page)
