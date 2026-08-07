"""
Chart Card Widget
A card containing a simple bar chart, drawn manually with QPainter
so no extra dependency (QtCharts / matplotlib) is required.
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QWidget
from PySide6.QtGui import QPainter, QColor, QFont, QPen
from PySide6.QtCore import Qt

from gui.styles import colors


class _BarChart(QWidget):

    def __init__(self, data, parent=None):
        """
        data: list of tuples [(label, value), ...]
        """
        super().__init__(parent)
        self.data = data or []
        self.setMinimumHeight(220)

    def set_data(self, data):
        self.data = data or []
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        palette = colors.CURRENT

        if not self.data:
            painter.setPen(QColor(palette["TEXT_LIGHT"]))
            painter.drawText(self.rect(), Qt.AlignCenter, "No data")
            return

        width = self.width()
        height = self.height()

        padding_bottom = 40
        padding_top = 20
        padding_side = 20

        chart_h = height - padding_bottom - padding_top
        chart_w = width - (padding_side * 2)

        max_value = max((v for _, v in self.data), default=1)
        max_value = max(max_value, 1)

        bar_count = len(self.data)
        gap = 24
        bar_width = max(
            (chart_w - gap * (bar_count - 1)) / bar_count, 20
        ) if bar_count else 20

        font = QFont("Segoe UI", 10)
        painter.setFont(font)

        x = padding_side

        for label, value in self.data:
            bar_h = (value / max_value) * chart_h if max_value else 0
            y = padding_top + (chart_h - bar_h)

            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(palette["PRIMARY"]))
            painter.drawRoundedRect(int(x), int(y), int(bar_width), int(bar_h), 6, 6)

            # value on top of bar
            painter.setPen(QColor(palette["ACCENT"]))
            painter.drawText(
                int(x), int(y) - 6, int(bar_width), 16,
                Qt.AlignCenter, str(value)
            )

            # label under bar
            painter.setPen(QColor(palette["TEXT_LIGHT"]))
            painter.drawText(
                int(x) - 10, height - padding_bottom + 6, int(bar_width) + 20, 20,
                Qt.AlignCenter, str(label)
            )

            x += bar_width + gap


class ChartCard(QFrame):

    def __init__(self, title="Chart", data=None, parent=None):
        super().__init__(parent)

        self.setObjectName("ChartCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("PageSubtitle")
        layout.addWidget(self.title_label)

        self.chart = _BarChart(data)
        layout.addWidget(self.chart)

    def set_data(self, data):
        self.chart.set_data(data)
