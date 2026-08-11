"""Reusable pagination controls for database tables."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget


class PaginationControls(QWidget):
    """Display page progress and emit requests for another result page."""

    page_changed = Signal(int)

    def __init__(self, page_size=100, parent=None):
        super().__init__(parent)
        self.page_size = page_size
        self.current_page = 1
        self.total_records = 0

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.summary_label = QLabel()
        self.summary_label.setObjectName("PageSubtitle")

        self.previous_button = QPushButton("Previous")
        self.previous_button.setObjectName("SecondaryButton")
        self.previous_button.clicked.connect(self._previous_page)

        self.page_label = QLabel()
        self.page_label.setObjectName("PageSubtitle")
        self.page_label.setAlignment(Qt.AlignCenter)
        self.page_label.setMinimumWidth(100)

        self.next_button = QPushButton("Next")
        self.next_button.setObjectName("SecondaryButton")
        self.next_button.clicked.connect(self._next_page)

        layout.addWidget(self.summary_label)
        layout.addStretch()
        layout.addWidget(self.previous_button)
        layout.addWidget(self.page_label)
        layout.addWidget(self.next_button)

        self.set_pagination(0, 1)

    def set_pagination(self, total_records, current_page):
        self.total_records = total_records
        total_pages = max(1, (total_records + self.page_size - 1) // self.page_size)
        self.current_page = min(max(1, current_page), total_pages)

        if total_records:
            first_record = (self.current_page - 1) * self.page_size + 1
            last_record = min(self.current_page * self.page_size, total_records)
            self.summary_label.setText(
                f"Showing {first_record:,}–{last_record:,} of {total_records:,} records"
            )
        else:
            self.summary_label.setText("No records found")

        self.page_label.setText(f"Page {self.current_page} of {total_pages}")
        self.previous_button.setEnabled(self.current_page > 1)
        self.next_button.setEnabled(self.current_page < total_pages)

    def _previous_page(self):
        if self.current_page > 1:
            self.page_changed.emit(self.current_page - 1)

    def _next_page(self):
        total_pages = max(1, (self.total_records + self.page_size - 1) // self.page_size)
        if self.current_page < total_pages:
            self.page_changed.emit(self.current_page + 1)
