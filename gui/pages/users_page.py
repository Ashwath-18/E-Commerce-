"""
Users Page
Table of users with add / delete, wired to crud/.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt

from gui.widgets.search_bar import SearchBar
from gui.widgets.sort_button import SortButton
from gui.widgets.table import DataTable
from gui.widgets.notification import show_notification
from gui.widgets.pagination import PaginationControls
from gui.dialogs.add_user_dialog import AddUserDialog
from gui.dialogs.delete_dialog import confirm_delete

from crud.delete import delete_user
from search.search_products import get_users_page

PAGE_SIZE = 100

SORT_OPTIONS = [("user_id", "User ID", "text")]

COLUMNS = [
    ("user_id", "User ID"),
]


class UsersPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.selected_user = None
        self.current_query = ""
        self.current_page = 1

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        header_row = QHBoxLayout()

        title_block = QVBoxLayout()
        title = QLabel("Users")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Manage registered users.")
        subtitle.setObjectName("PageSubtitle")
        title_block.addWidget(title)
        title_block.addWidget(subtitle)

        header_row.addLayout(title_block)
        header_row.addStretch()

        add_btn = QPushButton("+ Add User")
        add_btn.setObjectName("PrimaryButton")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self._add_user)

        header_row.addWidget(add_btn)
        layout.addLayout(header_row)

        self.search_bar = SearchBar(placeholder="Search by User ID...")
        self.search_bar.search_triggered.connect(self._search)
        self.search_bar.setMaximumWidth(780)

        self.sort_button = SortButton(SORT_OPTIONS)
        self.sort_button.sort_requested.connect(self._sort)

        search_row = QHBoxLayout()
        search_row.addWidget(self.search_bar)
        search_row.addWidget(self.sort_button)
        search_row.addStretch()
        layout.addLayout(search_row)

        table_card = QFrame()
        table_card.setObjectName("Card")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(12, 12, 12, 12)

        self.table = DataTable(COLUMNS)
        self.table.row_selected.connect(self._on_row_selected)
        table_layout.addWidget(self.table)

        layout.addWidget(table_card, stretch=1)

        self.pagination = PaginationControls(PAGE_SIZE)
        self.pagination.page_changed.connect(self.load_users)
        layout.addWidget(self.pagination)

        action_row = QHBoxLayout()
        action_row.addStretch()

        delete_btn = QPushButton("Delete Selected")
        delete_btn.setObjectName("DangerButton")
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.clicked.connect(self._delete_user)

        action_row.addWidget(delete_btn)
        layout.addLayout(action_row)

        self.load_users()

    def load_users(self, page=1):
        try:
            users, total = get_users_page(page, PAGE_SIZE, self.current_query)
            self.current_page = page
            self.table.load_data(users)
            self.pagination.set_pagination(total, page)
        except Exception as e:
            show_notification(self, f"Could not load users: {e}", "error")

    def _on_row_selected(self, row):
        self.selected_user = row

    def _search(self, user_id):
        if not user_id:
            self.current_query = ""
            self.load_users(1)
            return

        try:
            self.current_query = user_id
            self.load_users(1)
        except Exception as e:
            show_notification(self, f"Search failed: {e}", "error")

    def _sort(self, field, descending):
        self.table.sort_data(field, descending)

    def _add_user(self):
        dialog = AddUserDialog(self)
        if dialog.exec():
            show_notification(self, "User added successfully.", "success")
            self.load_users(self.current_page)

    def _delete_user(self):
        if not self.selected_user:
            show_notification(self, "Select a user first.", "warning")
            return

        user_id = self.selected_user.get("user_id")

        if confirm_delete(self, f"user '{user_id}'"):
            try:
                delete_user(user_id)
                show_notification(self, "User deleted.", "success")
                self.selected_user = None
                self.load_users(self.current_page)
            except Exception as e:
                show_notification(self, f"Delete failed: {e}", "error")

    def showEvent(self, event):
        super().showEvent(event)
        self.load_users(self.current_page)
