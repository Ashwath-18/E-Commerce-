"""
Stat Card widgets

StatCard   - white metric card: gradient icon badge, title, big value and an
             optional "share of records" progress bar.
AccentCard - gradient hero-style card (violet or pink) with a mini curve,
             used for the two highlighted collections on the dashboard.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
)

from gui.widgets import icons
from gui.widgets.chart_card import AreaChart


def _repolish(widget):
    widget.style().unpolish(widget)
    widget.style().polish(widget)


class StatCard(QFrame):

    clicked = Signal()

    def __init__(self, icon_text, title, value="0", parent=None, tone="violet"):
        """
        icon_text: name of a glyph in gui.widgets.icons.GLYPHS
                   (unknown names fall back to the database glyph)
        """
        super().__init__(parent)

        self.setObjectName("StatCard")
        self.setMinimumHeight(172)
        self._clickable = False

        glyph = icon_text if icon_text in icons.GLYPHS else "database"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(4)

        # ---------------- Top row: badge + link ----------------

        top = QHBoxLayout()
        top.setSpacing(0)

        self.icon_label = icons.IconBadge(glyph, 50, tone)
        top.addWidget(self.icon_label)
        top.addStretch()

        self.link_label = QLabel("View")
        self.link_label.setObjectName("StatLink")
        self.link_label.hide()
        top.addWidget(self.link_label, alignment=Qt.AlignTop)

        layout.addLayout(top)
        layout.addSpacing(10)

        # ---------------- Title + value ----------------

        self.title_label = QLabel(title)
        self.title_label.setObjectName("StatTitle")
        layout.addWidget(self.title_label)

        self.value_label = QLabel(str(value))
        self.value_label.setObjectName("StatValue")
        layout.addWidget(self.value_label)

        layout.addStretch()

        # ---------------- Share of records ----------------

        self.share_bar = QProgressBar()
        self.share_bar.setRange(0, 100)
        self.share_bar.setTextVisible(False)
        self.share_bar.setProperty("tone", "green")
        self.share_bar.setProperty("thin", True)
        self.share_bar.hide()
        layout.addWidget(self.share_bar)

        caption_row = QHBoxLayout()
        caption_row.setContentsMargins(0, 0, 0, 0)
        self.caption_label = QLabel("Share of records")
        self.caption_label.setObjectName("StatCaption")
        self.share_label = QLabel("")
        self.share_label.setObjectName("StatShare")
        caption_row.addWidget(self.caption_label)
        caption_row.addStretch()
        caption_row.addWidget(self.share_label)
        self.caption_label.hide()
        self.share_label.hide()
        layout.addLayout(caption_row)

    def set_value(self, value):
        self.value_label.setText(str(value))

    def set_share(self, percent):
        """Show the card's share of all records (0-100), or hide it (None)."""
        if percent is None:
            self.share_bar.hide()
            self.caption_label.hide()
            self.share_label.hide()
            return

        percent = max(0, min(100, int(round(percent))))
        self.share_bar.setValue(percent)
        self.share_label.setText(f"{percent}%")
        self.share_bar.show()
        self.caption_label.show()
        self.share_label.show()

    def set_clickable(self, enabled, tooltip=""):
        """Configure the card as a navigation control when a page exists."""
        self._clickable = enabled
        self.setProperty("clickable", enabled)
        self.setToolTip(tooltip)
        self.setCursor(Qt.PointingHandCursor if enabled else Qt.ArrowCursor)
        self.link_label.setVisible(enabled)
        _repolish(self)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if self._clickable and event.button() == Qt.LeftButton:
            self.clicked.emit()


class AccentCard(QFrame):
    """Gradient highlight card. tone: 'violet' or 'pink'."""

    clicked = Signal()

    def __init__(self, title, subtitle, icon_name, tone="violet", value="—", parent=None):
        super().__init__(parent)

        self.setObjectName("AccentCardPink" if tone == "pink" else "AccentCardViolet")
        self.setMinimumHeight(158)
        self._clickable = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(2)

        # ---------------- Header ----------------

        header = QHBoxLayout()
        header.setSpacing(14)

        badge = icons.IconBadge(icon_name, 52, "glass")
        header.addWidget(badge)

        text_block = QVBoxLayout()
        text_block.setSpacing(1)
        self.title_label = QLabel(title)
        self.title_label.setObjectName("AccentTitle")
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setObjectName("AccentSub")
        text_block.addStretch()
        text_block.addWidget(self.title_label)
        text_block.addWidget(self.subtitle_label)
        text_block.addStretch()
        header.addLayout(text_block, stretch=1)

        layout.addLayout(header)

        # ---------------- Mini curve ----------------

        self.chart = AreaChart(
            on_gradient=True,
            show_labels=False,
            show_bubble=False,
            min_height=40,
        )
        layout.addWidget(self.chart, stretch=1)

        # ---------------- Footer ----------------

        footer = QHBoxLayout()
        self.value_label = QLabel(str(value))
        self.value_label.setObjectName("AccentValue")
        footer.addWidget(self.value_label)
        footer.addStretch()

        self.go_button = QPushButton()
        self.go_button.setObjectName("GlassButton")
        self.go_button.setCursor(Qt.PointingHandCursor)
        icons.bind(self.go_button, "chevron_right", 18, "white")
        self.go_button.clicked.connect(self.clicked.emit)
        footer.addWidget(self.go_button, alignment=Qt.AlignBottom)

        layout.addLayout(footer)

    def set_value(self, value):
        self.value_label.setText(str(value))

    def set_chart(self, data):
        self.chart.set_data(data)

    def set_clickable(self, enabled, tooltip=""):
        self._clickable = enabled
        self.setProperty("clickable", enabled)
        self.setToolTip(tooltip)
        self.setCursor(Qt.PointingHandCursor if enabled else Qt.ArrowCursor)
        self.go_button.setVisible(enabled)
        _repolish(self)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if self._clickable and event.button() == Qt.LeftButton:
            self.clicked.emit()
