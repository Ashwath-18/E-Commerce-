"""
Stat Card Widget
Displays a single metric with a circular icon badge, big value,
and label.
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class StatCard(QFrame):

    def __init__(self, icon_text, title, value="0", parent=None):
        super().__init__(parent)

        self.setObjectName("StatCard")
        self.setMinimumHeight(160)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 26, 26, 22)
        layout.setSpacing(8)

        # ---------------- Circular Icon Badge ----------------

        self.icon_label = QLabel(icon_text)
        self.icon_label.setObjectName("StatIconBadge")
        self.icon_label.setFixedSize(48, 48)
        self.icon_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.icon_label)
        layout.addSpacing(12)

        # ---------------- Value ----------------

        self.value_label = QLabel(str(value))
        self.value_label.setObjectName("StatValue")
        layout.addWidget(self.value_label)

        # ---------------- Title ----------------

        self.title_label = QLabel(title.upper())
        self.title_label.setObjectName("StatTitle")
        layout.addWidget(self.title_label)

        layout.addStretch()

    def set_value(self, value):
        self.value_label.setText(str(value))