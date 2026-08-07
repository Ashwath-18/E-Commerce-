"""
Delete Confirmation Dialog
A generic, reusable "are you sure?" confirmation dialog used
before any destructive action.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import Qt


class DeleteDialog(QDialog):

    def __init__(self, item_description, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Confirm Delete")
        self.setMinimumWidth(380)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Delete Confirmation")
        title.setObjectName("PageTitle")
        layout.addWidget(title)

        message = QLabel(
            f"Are you sure you want to delete {item_description}?\n"
            "This action cannot be undone."
        )
        message.setWordWrap(True)
        message.setObjectName("PageSubtitle")
        layout.addWidget(message)

        button_row = QHBoxLayout()
        button_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("SecondaryButton")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)

        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("DangerButton")
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.clicked.connect(self.accept)

        button_row.addWidget(cancel_btn)
        button_row.addWidget(delete_btn)

        layout.addLayout(button_row)


def confirm_delete(parent, item_description):
    """
    Convenience function. Returns True if the user confirmed deletion.
    """
    dialog = DeleteDialog(item_description, parent)
    return dialog.exec() == QDialog.Accepted
