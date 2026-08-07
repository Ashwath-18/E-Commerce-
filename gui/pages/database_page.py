"""
Database Page
Shows live collection counts and lets the admin run maintenance
tasks (create collections/indexes, re-check counts) safely from
the GUI.

NOTE: This file didn't exist in the uploaded gui/pages/ folder —
the sidebar has a "Database" nav item pointing to it, so it's
added here to keep the app from crashing on that page.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QGridLayout
)
from PySide6.QtCore import Qt

from gui.widgets.notification import show_notification
from gui.dialogs.delete_dialog import confirm_delete  # reused as a generic confirm

from config.mongodb import db
from database.create_collections import create_collections
from database.create_indexes import create_indexes


COLLECTIONS = [
    "Users", "Products", "Sellers", "Orders",
    "Reviews", "Shipping", "Payments", "Inventory"
]


class DatabasePage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        title = QLabel("Database")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Live collection counts and maintenance tools.")
        subtitle.setObjectName("PageSubtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        # ---------------- Collection Count Grid ----------------

        self.count_card = QFrame()
        self.count_card.setObjectName("Card")
        self.grid = QGridLayout(self.count_card)
        self.grid.setContentsMargins(24, 24, 24, 24)
        self.grid.setSpacing(14)

        self.count_labels = {}

        for i, name in enumerate(COLLECTIONS):
            row, col = divmod(i, 2)

            name_label = QLabel(name)
            name_label.setObjectName("PageSubtitle")

            count_label = QLabel("—")
            count_label.setObjectName("StatValue")

            box = QVBoxLayout()
            box.addWidget(name_label)
            box.addWidget(count_label)

            wrapper = QWidget()
            wrapper.setLayout(box)

            self.grid.addWidget(wrapper, row, col)
            self.count_labels[name] = count_label

        layout.addWidget(self.count_card)

        # ---------------- Maintenance Actions ----------------

        action_card = QFrame()
        action_card.setObjectName("Card")
        action_layout = QHBoxLayout(action_card)
        action_layout.setContentsMargins(24, 20, 24, 20)

        refresh_btn = QPushButton("Refresh Counts")
        refresh_btn.setObjectName("SecondaryButton")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.clicked.connect(self.refresh_counts)

        ensure_btn = QPushButton("Ensure Collections + Indexes")
        ensure_btn.setObjectName("PrimaryButton")
        ensure_btn.setCursor(Qt.PointingHandCursor)
        ensure_btn.clicked.connect(self._ensure_setup)

        action_layout.addWidget(refresh_btn)
        action_layout.addWidget(ensure_btn)
        action_layout.addStretch()

        layout.addWidget(action_card)
        layout.addStretch()

        self.refresh_counts()

    def refresh_counts(self):
        for name, label in self.count_labels.items():
            try:
                count = db[name].count_documents({})
                label.setText(str(count))
            except Exception:
                label.setText("N/A")

    def _ensure_setup(self):
        if not confirm_delete(self, "run collection + index setup (safe, non-destructive)"):
            return

        try:
            create_collections()
            create_indexes()
            show_notification(self, "Collections and indexes are ready.", "success")
            self.refresh_counts()
        except Exception as e:
            show_notification(self, f"Setup failed: {e}", "error")

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_counts()
