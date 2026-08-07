"""
Users Page
Table of users with add / delete, wired to crud/.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt

from gui.widgets.table import DataTable
from gui.widgets.notification import show_notification
from gui.dialogs.add_user_dialog import AddUserDialog
from gui.dialogs.delete_dialog import confirm_delete

from crud.read import get_all_users
from crud.delete import delete_user

DISPLAY_LIMIT = 300

COLUMNS = [
    ("user_id", "User ID"),
]


class UsersPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.selected_user = None

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

        table_card = QFrame()
        table_card.setObjectName("Card")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(12, 12, 12, 12)

        self.table = DataTable(COLUMNS)
        self.table.row_selected.connect(self._on_row_selected)
        table_layout.addWidget(self.table)

        layout.addWidget(table_card, stretch=1)

        action_row = QHBoxLayout()
        action_row.addStretch()

        delete_btn = QPushButton("Delete Selected")
        delete_btn.setObjectName("DangerButton")
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.clicked.connect(self._delete_user)

        action_row.addWidget(delete_btn)
        layout.addLayout(action_row)

        self.load_users()

    def load_users(self):
        try:
            users = get_all_users()
            self.table.load_data(users[:DISPLAY_LIMIT])
        except Exception as e:
            show_notification(self, f"Could not load users: {e}", "error")

    def _on_row_selected(self, row):
        self.selected_user = row

    def _add_user(self):
        dialog = AddUserDialog(self)
        if dialog.exec():
            show_notification(self, "User added successfully.", "success")
            self.load_users()

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
                self.load_users()
            except Exception as e:
                show_notification(self, f"Delete failed: {e}", "error")

    def showEvent(self, event):
        super().showEvent(event)
        self.load_users()
