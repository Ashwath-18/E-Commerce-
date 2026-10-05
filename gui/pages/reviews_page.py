"""
Reviews Page
Table of product reviews, searched through search/search_products.py.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout
from gui.widgets.search_bar import SearchBar
from gui.widgets.sort_button import SortButton
from gui.widgets.table import DataTable
from gui.widgets.notification import show_notification
from gui.widgets.pagination import PaginationControls
from gui.widgets.page_header import PageHeader, FilterBar, make_table_card

from search.search_products import get_reviews_page

PAGE_SIZE = 100

SORT_OPTIONS = [("rating", "Rating", "number")]

COLUMNS = [
    ("product_id", "Product ID"),
    ("rating", "Rating"),
    ("review_count", "Review Count"),
]


class ReviewsPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_query = ""
        self.current_page = 1

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 8, 8)
        layout.setSpacing(16)

        layout.addWidget(
            PageHeader("Reviews", "Browse product reviews and ratings.", "reviews")
        )

        self.search_bar = SearchBar(
            placeholder="Search by Product ID..."
        )
        self.search_bar.search_triggered.connect(self._search)

        self.sort_button = SortButton(SORT_OPTIONS)
        self.sort_button.sort_requested.connect(self._sort)

        filters = FilterBar()
        filters.row.addWidget(self.search_bar, stretch=1)
        filters.row.addWidget(self.sort_button)
        layout.addWidget(filters)

        self.table = DataTable(COLUMNS)
        self.table.set_empty_message("No reviews found", "Try searching by a different Product ID.")
        layout.addWidget(make_table_card(self.table), stretch=1)

        self.pagination = PaginationControls(PAGE_SIZE)
        self.pagination.page_changed.connect(self.load_reviews)
        layout.addWidget(self.pagination)

        self.load_reviews()

    def load_reviews(self, page=1):
        try:
            records, total = get_reviews_page(
                page, PAGE_SIZE, self.current_query
            )
            self.current_page = page
            self.table.load_data(records)
            self.pagination.set_pagination(total, page)
        except Exception as e:
            show_notification(self, f"Could not load reviews: {e}", "error")

    def _search(self, query):
        if not query:
            self.current_query = ""
            self.load_reviews(1)
            return

        try:
            self.current_query = query
            self.load_reviews(1)
        except Exception as e:
            show_notification(self, f"Search failed: {e}", "error")

    def _sort(self, field, descending):
        self.table.sort_data(field, descending, numeric=True)

    def showEvent(self, event):
        super().showEvent(event)
        self.load_reviews(self.current_page)
