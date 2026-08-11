"""Orders page with text search, date-range filtering, and sorting."""

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QDateEdit, QPushButton
)
from gui.widgets.search_bar import SearchBar
from gui.widgets.sort_button import SortButton
from gui.widgets.table import DataTable
from gui.widgets.notification import show_notification
from gui.widgets.pagination import PaginationControls

from search.search_products import get_orders_page

PAGE_SIZE = 100

SORT_OPTIONS = [
    ("user_id", "User ID", "text"),
    ("purchase_date", "Purchase Date", "date"),
]

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

        self.current_query = ""
        self.current_from_date = None
        self.current_to_date = None
        self.current_page = 1

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        title = QLabel("Orders")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Search orders and filter them by a date range.")
        subtitle.setObjectName("PageSubtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        self.search_bar = SearchBar(
            placeholder="Search user, product, payment, status, or returned..."
        )
        self.search_bar.search_triggered.connect(self._apply_filters)
        self.search_bar.setMaximumWidth(640)

        self.sort_button = SortButton(SORT_OPTIONS)
        self.sort_button.sort_requested.connect(self._sort)

        search_row = QHBoxLayout()
        search_row.addWidget(self.search_bar)
        search_row.addWidget(self.sort_button)
        search_row.addStretch()
        layout.addLayout(search_row)

        # ---------------- Date Range ----------------

        date_row = QHBoxLayout()
        date_row.setSpacing(10)

        earliest_date = QDate(2000, 1, 1)

        from_label = QLabel("From")
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDisplayFormat("dd MMM yyyy")
        self.from_date.setMinimumDate(earliest_date)
        self.from_date.setDate(earliest_date)
        self.from_date.setSpecialValueText("Select date")
        self.from_date.setFixedWidth(205)

        to_label = QLabel("To")
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDisplayFormat("dd MMM yyyy")
        self.to_date.setMinimumDate(earliest_date)
        self.to_date.setDate(earliest_date)
        self.to_date.setSpecialValueText("Select date")
        self.to_date.setFixedWidth(205)

        apply_dates_button = QPushButton("Apply Dates")
        apply_dates_button.setObjectName("SecondaryButton")
        apply_dates_button.clicked.connect(self._apply_filters)

        clear_dates_button = QPushButton("Clear")
        clear_dates_button.setObjectName("SecondaryButton")
        clear_dates_button.clicked.connect(self._clear_dates)

        date_row.addWidget(QLabel("Purchase Date"))
        date_row.addWidget(from_label)
        date_row.addWidget(self.from_date)
        date_row.addWidget(to_label)
        date_row.addWidget(self.to_date)
        date_row.addWidget(apply_dates_button)
        date_row.addWidget(clear_dates_button)
        date_row.addStretch()
        layout.addLayout(date_row)

        table_card = QFrame()
        table_card.setObjectName("Card")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(12, 12, 12, 12)

        self.table = DataTable(COLUMNS)
        table_layout.addWidget(self.table)

        layout.addWidget(table_card, stretch=1)

        self.pagination = PaginationControls(PAGE_SIZE)
        self.pagination.page_changed.connect(self.load_orders)
        layout.addWidget(self.pagination)

        self.load_orders()

    def load_orders(self, page=1):
        try:
            orders, total = get_orders_page(
                page,
                PAGE_SIZE,
                self.current_query,
                self.current_from_date,
                self.current_to_date,
            )
            self.current_page = page
            self.table.load_data(orders)
            self.pagination.set_pagination(total, page)
        except Exception as e:
            show_notification(self, f"Could not load orders: {e}", "error")

    def _apply_filters(self):
        query = self.search_bar.text()
        from_date = self._date_value(self.from_date)
        to_date = self._date_value(self.to_date)

        if from_date and to_date and from_date > to_date:
            show_notification(self, "The From date must be before the To date.", "warning")
            return

        try:
            self.current_query = query
            self.current_from_date = from_date
            self.current_to_date = to_date
            self.load_orders(1)
        except Exception as e:
            show_notification(self, f"Filter failed: {e}", "error")

    @staticmethod
    def _date_value(date_edit):
        if date_edit.date() == date_edit.minimumDate():
            return None
        return date_edit.date().toString("yyyy-MM-dd")

    def _clear_dates(self):
        self.from_date.setDate(self.from_date.minimumDate())
        self.to_date.setDate(self.to_date.minimumDate())
        self._apply_filters()

    def _sort(self, field, descending):
        self.table.sort_data(field, descending)

    def showEvent(self, event):
        super().showEvent(event)
        self.load_orders(self.current_page)
