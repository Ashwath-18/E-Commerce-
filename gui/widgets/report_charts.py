"""Dependency-free report charts drawn with Qt's QPainter."""

from math import cos, radians, sin

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QWidget

from gui.styles import colors


CHART_COLORS = ["#4F46E5", "#7C3AED", "#0891B2", "#F59E0B", "#DC2626"]


def _format_number(value, currency=False):
    if currency:
        return f"₹{value:,.0f}"
    return f"{value:,.0f}"


class ChartPanel(QFrame):
    """Consistent card container for custom report charts."""

    def __init__(self, title, chart, parent=None):
        super().__init__(parent)
        self.setObjectName("ChartCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 18, 22, 20)
        layout.setSpacing(8)
        title_label = QLabel(title)
        title_label.setObjectName("ChartTitle")
        layout.addWidget(title_label)
        layout.addWidget(chart)


class HorizontalBarChart(QWidget):
    def __init__(self, data=None, currency=False, parent=None):
        super().__init__(parent)
        self.data = data or []
        self.currency = currency
        self.setMinimumHeight(220)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        palette = colors.CURRENT
        rect = self.rect()
        if not self.data:
            painter.setPen(QColor(palette["TEXT_LIGHT"]))
            painter.drawText(rect, Qt.AlignCenter, "No data available")
            return

        left, right, top, bottom = 145, 64, 18, 18
        chart_width = max(1, rect.width() - left - right)
        row_height = max(30, (rect.height() - top - bottom) // len(self.data))
        max_value = max(value for _, value in self.data) or 1
        painter.setFont(QFont("Segoe UI", 9))

        for index, (label, value) in enumerate(self.data):
            y = top + index * row_height
            painter.setPen(QColor(palette["TEXT"]))
            painter.drawText(0, y, left - 12, row_height, Qt.AlignRight | Qt.AlignVCenter, str(label))

            bar_width = int(chart_width * (value / max_value))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(CHART_COLORS[index % len(CHART_COLORS)]))
            painter.drawRoundedRect(left, y + 7, max(bar_width, 2), max(row_height - 14, 8), 5, 5)

            painter.setPen(QColor(palette["TEXT_LIGHT"]))
            painter.drawText(left + bar_width + 8, y, right - 4, row_height, Qt.AlignLeft | Qt.AlignVCenter, _format_number(value, self.currency))


class VerticalBarChart(QWidget):
    def __init__(self, data=None, max_value=None, parent=None):
        super().__init__(parent)
        self.data = data or []
        self.max_value = max_value
        self.setMinimumHeight(240)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        palette = colors.CURRENT
        rect = self.rect()
        if not self.data:
            painter.setPen(QColor(palette["TEXT_LIGHT"]))
            painter.drawText(rect, Qt.AlignCenter, "No data available")
            return

        left, right, top, bottom = 30, 22, 28, 48
        chart_height = max(1, rect.height() - top - bottom)
        chart_width = max(1, rect.width() - left - right)
        max_value = self.max_value or max(value for _, value in self.data) or 1
        gap = 18
        bar_width = max(22, (chart_width - gap * (len(self.data) - 1)) // len(self.data))
        painter.setFont(QFont("Segoe UI", 9))

        x = left
        for index, (label, value) in enumerate(self.data):
            bar_height = int(chart_height * (value / max_value))
            y = top + chart_height - bar_height
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(CHART_COLORS[index % len(CHART_COLORS)]))
            painter.drawRoundedRect(x, y, bar_width, max(bar_height, 2), 5, 5)
            painter.setPen(QColor(palette["TEXT"]))
            painter.drawText(x - 5, y - 22, bar_width + 10, 18, Qt.AlignCenter, f"{value:.1f}")
            painter.setPen(QColor(palette["TEXT_LIGHT"]))
            painter.drawText(x - 12, top + chart_height + 7, bar_width + 24, 35, Qt.AlignHCenter | Qt.AlignTop, str(label))
            x += bar_width + gap


class DonutChart(QWidget):
    def __init__(self, data=None, chart_colors=None, parent=None):
        super().__init__(parent)
        self.data = [(label, value) for label, value in (data or []) if value >= 0]
        self.chart_colors = chart_colors or CHART_COLORS
        self.setMinimumHeight(230)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        palette = colors.CURRENT
        rect = self.rect()
        total = sum(value for _, value in self.data)
        if not total:
            painter.setPen(QColor(palette["TEXT_LIGHT"]))
            painter.drawText(rect, Qt.AlignCenter, "No data available")
            return

        size = min(rect.height() - 24, rect.width() // 2)
        circle = QRectF(18, (rect.height() - size) / 2, size, size)
        start_angle = 90 * 16
        for index, (_, value) in enumerate(self.data):
            if value <= 0:
                continue
            span = -int(360 * 16 * value / total)
            painter.setPen(QPen(QColor(colors.CURRENT["CARD"]), 2))
            painter.setBrush(QColor(self.chart_colors[index % len(self.chart_colors)]))
            painter.drawPie(circle, start_angle, span)
            start_angle += span

        inner = circle.adjusted(size * 0.28, size * 0.28, -size * 0.28, -size * 0.28)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(palette["CARD"]))
        painter.drawEllipse(inner)
        painter.setPen(QColor(palette["TEXT"]))
        painter.setFont(QFont("Segoe UI", 15, QFont.Bold))
        painter.drawText(inner, Qt.AlignCenter, f"{total:,}")

        legend_x = int(circle.right() + 28)
        painter.setFont(QFont("Segoe UI", 10))
        for index, (label, value) in enumerate(self.data):
            y = 32 + index * 34
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(self.chart_colors[index % len(self.chart_colors)]))
            painter.drawRoundedRect(legend_x, y, 13, 13, 3, 3)
            painter.setPen(QColor(palette["TEXT"]))
            painter.drawText(legend_x + 22, y - 4, max(1, rect.width() - legend_x - 22), 22, Qt.AlignLeft | Qt.AlignVCenter, f"{label}: {value:,}")


class RatingGauge(QWidget):
    def __init__(self, value=0, maximum=5, parent=None):
        super().__init__(parent)
        self.value = value or 0
        self.maximum = maximum
        self.setMinimumHeight(230)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        palette = colors.CURRENT
        size = min(self.width() - 40, self.height() * 1.45)
        rect = QRectF((self.width() - size) / 2, 18, size, size)
        painter.setPen(QPen(QColor(palette["BORDER"]), 18, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(rect, 225 * 16, -270 * 16)
        painter.setPen(QPen(QColor("#4F46E5"), 18, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(rect, 225 * 16, -int(270 * 16 * min(self.value / self.maximum, 1)))
        painter.setPen(QColor(palette["TEXT"]))
        painter.setFont(QFont("Segoe UI", 25, QFont.Bold))
        painter.drawText(self.rect().adjusted(0, 60, 0, -36), Qt.AlignCenter, f"{self.value:.2f}")
        painter.setFont(QFont("Segoe UI", 10))
        painter.setPen(QColor(palette["TEXT_LIGHT"]))
        painter.drawText(self.rect().adjusted(0, 112, 0, -6), Qt.AlignCenter, f"out of {self.maximum}")
