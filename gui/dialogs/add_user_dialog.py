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


class AddUserDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Add User")
        self.setMinimumWidth(380)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Add New User")
        title.setObjectName("PageTitle")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)

        self.user_id_input = QLineEdit()
        self.user_id_input.setPlaceholderText("e.g. U000123")

        form.addRow("User ID *", self.user_id_input)

        layout.addLayout(form)

        # ---------------- Buttons ----------------

        button_row = QHBoxLayout()
        button_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("SecondaryButton")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save User")
        save_btn.setObjectName("PrimaryButton")
        save_btn.setCursor(Qt.PointingHandCursor)
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
