"""
Database Page
Shows live collection counts and lets the admin run maintenance
tasks (create collections/indexes, re-check counts) safely from
the GUI.

NOTE: This page is not registered in the sidebar; it is kept (and
restyled) so it can be wired up whenever it is needed.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QGridLayout
)
from PySide6.QtCore import Qt

from gui.widgets import icons
from gui.widgets.notification import show_notification
from gui.widgets.page_header import PageHeader
from gui.dialogs.delete_dialog import confirm_delete  # reused as a generic confirm

from config.mongodb import db
from database.create_collections import create_collections
from database.create_indexes import create_indexes


COLLECTIONS = [
    "Users", "Products", "Sellers", "Orders",
    "Reviews", "Shipping", "Payments", "Inventory"
]

GLYPHS = {
    "Users": "users", "Products": "products", "Sellers": "sellers",
    "Orders": "orders", "Reviews": "reviews", "Shipping": "shipping",
    "Payments": "payments", "Inventory": "inventory",
}


class DatabasePage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 8, 8)
        layout.setSpacing(16)

        layout.addWidget(
            PageHeader(
                "Database", "Live collection counts and maintenance tools.", "database"
            )
        )

        # ---------------- Collection Count Grid ----------------

        self.count_card = QFrame()
        self.count_card.setObjectName("Card")
        self.grid = QGridLayout(self.count_card)
        self.grid.setContentsMargins(24, 24, 24, 24)
        self.grid.setSpacing(14)

        self.count_labels = {}

        for i, name in enumerate(COLLECTIONS):
            row, col = divmod(i, 2)

            tile = QFrame()
            tile.setObjectName("MetricTile")
            tile_layout = QHBoxLayout(tile)
            tile_layout.setContentsMargins(16, 14, 16, 14)
            tile_layout.setSpacing(14)
            tile_layout.addWidget(
                icons.IconBadge(GLYPHS.get(name, "database"), 44, "soft")
            )

            box = QVBoxLayout()
            box.setSpacing(0)
            name_label = QLabel(name)
            name_label.setObjectName("PanelLabel")

            count_label = QLabel("—")
            count_label.setObjectName("StatValue")

            box.addWidget(name_label)
            box.addWidget(count_label)
            tile_layout.addLayout(box)
            tile_layout.addStretch()

            self.grid.addWidget(tile, row, col)
            self.count_labels[name] = count_label

        layout.addWidget(self.count_card)

        # ---------------- Maintenance Actions ----------------

        action_card = QFrame()
        action_card.setObjectName("Card")
        action_layout = QHBoxLayout(action_card)
        action_layout.setContentsMargins(24, 20, 24, 20)
        action_layout.setSpacing(12)

        refresh_btn = QPushButton("Refresh Counts")
        refresh_btn.setObjectName("SecondaryButton")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        icons.bind(refresh_btn, "refresh", 18, "muted", "primary")
        refresh_btn.clicked.connect(self.refresh_counts)

        ensure_btn = QPushButton("Ensure Collections + Indexes")
        ensure_btn.setObjectName("PrimaryButton")
        ensure_btn.setCursor(Qt.PointingHandCursor)
        icons.bind(ensure_btn, "database", 18, "white")
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
