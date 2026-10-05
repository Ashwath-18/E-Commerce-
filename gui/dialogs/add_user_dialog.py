"""
Add User Dialog
Simple form to create a new User document, wired to
crud.create.create_user().
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QHBoxLayout, QPushButton, QLabel, QMessageBox
)
from PySide6.QtCore import Qt

from crud.create import create_user
from gui.widgets import icons
from gui.widgets.page_header import dialog_header


class AddUserDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Add User")
        self.setMinimumWidth(460)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 28, 30, 26)
        layout.setSpacing(20)

        layout.addWidget(
            dialog_header("Add New User", "Create a user record by ID.", "users")
        )

        form = QFormLayout()
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(12)

        self.user_id_input = QLineEdit()
        self.user_id_input.setPlaceholderText("e.g. U000123")
        self.user_id_input.setMinimumHeight(48)

        form.addRow("User ID *", self.user_id_input)

        layout.addLayout(form)

        # ---------------- Buttons ----------------

        button_row = QHBoxLayout()
        button_row.setSpacing(10)
        button_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("SecondaryButton")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save User")
        save_btn.setObjectName("PrimaryButton")
        save_btn.setCursor(Qt.PointingHandCursor)
        icons.bind(save_btn, "check", 18, "white")
        save_btn.clicked.connect(self._save)

        button_row.addWidget(cancel_btn)
        button_row.addWidget(save_btn)

        layout.addLayout(button_row)

    def _save(self):
        user_id = self.user_id_input.text().strip()

        if not user_id:
            QMessageBox.warning(self, "Missing Field", "User ID is required.")
            return

        try:
            create_user(user_id)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save user:\n{e}")
