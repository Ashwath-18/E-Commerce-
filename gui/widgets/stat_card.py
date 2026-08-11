"""
Stat Card Widget
Displays a single metric with a circular icon badge, big value,
and label.
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal


class StatCard(QFrame):

    clicked = Signal()

    def __init__(self, icon_text, title, value="0", parent=None):
        super().__init__(parent)

        self.setObjectName("StatCard")
        self.setMinimumHeight(156)
        self._clickable = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 22)
        layout.setSpacing(7)

        # ---------------- Circular Icon Badge ----------------

        self.icon_label = QLabel(icon_text)
        self.icon_label.setObjectName("StatIconBadge")
        self.icon_label.setFixedSize(46, 46)
        self.icon_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.icon_label)
        layout.addSpacing(10)

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

    def set_clickable(self, enabled, tooltip=""):
        """Configure the card as a navigation control when a page exists."""
        self._clickable = enabled
        self.setProperty("clickable", enabled)
        self.setToolTip(tooltip)
        self.setCursor(Qt.PointingHandCursor if enabled else Qt.ArrowCursor)
        self.style().unpolish(self)
        self.style().polish(self)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if self._clickable and event.button() == Qt.LeftButton:
            self.clicked.emit()
