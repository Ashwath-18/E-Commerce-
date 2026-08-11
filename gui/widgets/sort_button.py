"""Reusable icon button with field-specific sort menus."""

import os

from PySide6.QtCore import Signal, QSize
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenu, QToolButton


class SortButton(QToolButton):
    """Show sort choices and emit the selected field and direction."""

    sort_requested = Signal(str, bool)

    def __init__(self, options=None, parent=None):
        super().__init__(parent)

        self.setObjectName("SortButton")
        self.setToolTip("Sort results")
        self.setFixedSize(46, 46)
        self.setIconSize(QSize(27, 27))
        self.setPopupMode(QToolButton.InstantPopup)

        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "assets", "sort_icon.png"
        )
        if os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
        else:
            self.setText("↕")

        self.sort_menu = QMenu(self)
        self.setMenu(self.sort_menu)
        self.set_sort_options(options or [])

    def set_sort_options(self, options):
        """Set options as (field_name, visible_label, field_kind) tuples."""
        self.sort_menu.clear()

        for field_name, label, field_kind in options:
            field_menu = self.sort_menu.addMenu(label)
            ascending_label, descending_label = self._direction_labels(field_kind)

            ascending = QAction(ascending_label, self)
            ascending.triggered.connect(
                lambda checked=False, field=field_name: self.sort_requested.emit(field, False)
            )
            field_menu.addAction(ascending)

            descending = QAction(descending_label, self)
            descending.triggered.connect(
                lambda checked=False, field=field_name: self.sort_requested.emit(field, True)
            )
            field_menu.addAction(descending)

    @staticmethod
    def _direction_labels(field_kind):
        if field_kind == "number":
            return "Low to High", "High to Low"
        if field_kind == "date":
            return "Oldest to Newest", "Newest to Oldest"
        return "Ascending (A–Z)", "Descending (Z–A)"
