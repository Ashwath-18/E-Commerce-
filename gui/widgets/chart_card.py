"""
Chart widgets
Drawn manually with QPainter so no extra dependency (QtCharts / matplotlib)
is required.

* AreaChart  - smooth gradient curve with a highlighted point + value bubble
               (the signature "Overview" curve of the dashboard).
* _BarChart  - rounded gradient bars (used by ChartCard).
* ChartCard  - a card wrapping a bar chart.
"""

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontMetrics,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from gui.styles import colors


def _smooth_path(points, top, bottom):
    """Catmull-Rom spline through points, converted to cubic beziers."""
    path = QPainterPath()
    if not points:
        return path

    path.moveTo(points[0])
    if len(points) == 1:
        return path

    def clamp_y(y):
        return min(max(y, top), bottom)

    for i in range(len(points) - 1):
        p0 = points[i - 1] if i > 0 else points[i]
        p1 = points[i]
        p2 = points[i + 1]
        p3 = points[i + 2] if i + 2 < len(points) else p2

        c1 = QPointF(
            p1.x() + (p2.x() - p0.x()) / 6.0,
            clamp_y(p1.y() + (p2.y() - p0.y()) / 6.0),
        )
        c2 = QPointF(
            p2.x() - (p3.x() - p1.x()) / 6.0,
            clamp_y(p2.y() - (p3.y() - p1.y()) / 6.0),
        )
        path.cubicTo(c1, c2, p2)

    return path


class AreaChart(QWidget):
    """
    Smooth area chart.

    data        : list of (label, value)
    on_gradient : True when drawn on a violet / pink card (white ink),
                  False when drawn on a normal card (violet ink)
    """

    def __init__(
        self,
        data=None,
        on_gradient=False,
        show_labels=True,
        show_bubble=True,
        caption="records",
        min_height=150,
        parent=None,
    ):
        super().__init__(parent)
        self.data = list(data or [])
        self.on_gradient = on_gradient
        self.show_labels = show_labels
        self.show_bubble = show_bubble
        self.caption = caption
        self.highlight = None
        self.setMinimumHeight(min_height)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

    def set_data(self, data, highlight=None):
        self.data = list(data or [])
        self.highlight = highlight
        self.update()

    def _scaled(self, value, max_value):
        # sqrt keeps small collections visible next to very large ones
        return math.sqrt(max(value, 0) / max_value) if max_value > 0 else 0.0

    def paintEvent(self, event):
        p = colors.CURRENT
        dark = colors.is_dark()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if not self.data:
            ink = QColor(255, 255, 255, 170) if self.on_gradient else QColor(p["TEXT_LIGHT"])
            painter.setPen(ink)
            painter.drawText(self.rect(), Qt.AlignCenter, "No data")
            return

        w, h = self.width(), self.height()
        left = right = 40 if self.show_labels else 18
        top = 34 if self.show_bubble else 10
        bottom_pad = 34 if self.show_labels else 6
        chart_top = top
        chart_bottom = h - bottom_pad
        chart_h = max(chart_bottom - chart_top, 1)
        chart_w = max(w - left - right, 1)

        values = [v for _, v in self.data]
        max_value = max(values) if values else 1
        max_value = max(max_value, 1)

        count = len(self.data)
        denom = max(count - 1, 1)
        points = []
        for i, (_, value) in enumerate(self.data):
            x = left + chart_w * (i / denom)
            y = chart_bottom - chart_h * 0.92 * self._scaled(value, max_value)
            points.append(QPointF(x, y))

        hi = self.highlight
        if hi is None:
            hi = values.index(max(values))

        # ---- highlight column (frosted band behind the active point) ----
        if self.show_bubble and 0 <= hi < count:
            band_w = min(46, chart_w / max(count, 1) * 0.9)
            band = QRectF(points[hi].x() - band_w / 2, 8, band_w, chart_bottom + 22)
            if self.on_gradient:
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(255, 255, 255, 34))
            else:
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(p["SOFT"]))
            painter.drawRoundedRect(band, band_w / 2.2, band_w / 2.2)

        # ---- fill under the curve ----
        curve = _smooth_path(points, chart_top, chart_bottom)
        fill = QPainterPath(curve)
        fill.lineTo(points[-1].x(), chart_bottom)
        fill.lineTo(points[0].x(), chart_bottom)
        fill.closeSubpath()

        grad = QLinearGradient(0, chart_top, 0, chart_bottom)
        if self.on_gradient:
            grad.setColorAt(0.0, QColor(255, 255, 255, 80))
            grad.setColorAt(1.0, QColor(255, 255, 255, 0))
        else:
            c = QColor(p["PRIMARY"])
            c.setAlpha(90 if dark else 70)
            c0 = QColor(p["PRIMARY"])
            c0.setAlpha(0)
            grad.setColorAt(0.0, c)
            grad.setColorAt(1.0, c0)
        painter.setPen(Qt.NoPen)
        painter.setBrush(grad)
        painter.drawPath(fill)

        # ---- the curve ----
        if self.on_gradient:
            line_color = QColor(255, 255, 255, 235)
        else:
            line_color = QColor(p["PRIMARY"])
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(line_color, 2.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawPath(curve)

        # ---- highlighted point + bubble ----
        if self.show_bubble and 0 <= hi < count:
            pt = points[hi]
            painter.setPen(QPen(QColor(255, 255, 255), 3))
            painter.setBrush(QColor(p["PINK_B"]) if self.on_gradient else QColor(p["PRIMARY"]))
            painter.drawEllipse(pt, 6.5, 6.5)

            value_text = f"{self.data[hi][1]:,}"
            vf = QFont(colors.FONT_FAMILY, 10)
            vf.setBold(True)
            cf = QFont(colors.FONT_FAMILY, 8)
            fm_v, fm_c = QFontMetrics(vf), QFontMetrics(cf)
            bw = max(fm_v.horizontalAdvance(value_text), fm_c.horizontalAdvance(self.caption)) + 22
            bh = 40
            bx = min(max(pt.x() - bw / 2, 4), w - bw - 4)
            by = max(pt.y() - bh - 14, 2)
            bubble = QRectF(bx, by, bw, bh)

            painter.setPen(QPen(QColor(255, 255, 255, 40), 1))
            painter.setBrush(QColor(34, 26, 92, 215) if self.on_gradient else QColor(p["GRAD_B"]))
            painter.drawRoundedRect(bubble, 12, 12)

            painter.setPen(QColor("#FFFFFF"))
            painter.setFont(vf)
            painter.drawText(
                QRectF(bx, by + 5, bw, 18), Qt.AlignCenter, value_text
            )
            painter.setPen(QColor(255, 255, 255, 170))
            painter.setFont(cf)
            painter.drawText(
                QRectF(bx, by + 21, bw, 14), Qt.AlignCenter, self.caption
            )

        # ---- x labels ----
        if self.show_labels:
            lf = QFont(colors.FONT_FAMILY, 8)
            lf.setBold(False)
            painter.setFont(lf)
            fm = QFontMetrics(lf)
            for i, (label, _) in enumerate(self.data):
                x = points[i].x()
                text = str(label)
                tw = fm.horizontalAdvance(text) + 18
                rect = QRectF(x - tw / 2, h - 28, tw, 22)
                if i == hi and self.show_bubble:
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(QColor("#FFFFFF") if self.on_gradient else QColor(p["PRIMARY"]))
                    painter.drawRoundedRect(rect, 11, 11)
                    painter.setPen(QColor(p["GRAD_B"]) if self.on_gradient else QColor("#FFFFFF"))
                else:
                    painter.setPen(
                        QColor(255, 255, 255, 175) if self.on_gradient else QColor(p["TEXT_LIGHT"])
                    )
                painter.drawText(rect, Qt.AlignCenter, text)


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

        padding_bottom = 42
        padding_top = 26
        padding_side = 24

        chart_h = height - padding_bottom - padding_top
        chart_w = width - (padding_side * 2)

        max_value = max((v for _, v in self.data), default=1)
        max_value = max(max_value, 1)

        bar_count = len(self.data)
        gap = 26
        bar_width = max(
            (chart_w - gap * (bar_count - 1)) / bar_count, 20
        ) if bar_count else 20

        font = QFont(colors.FONT_FAMILY, 10)
        painter.setFont(font)

        # faint guide lines
        painter.setPen(QPen(QColor(palette["ROW_LINE"]), 1))
        for step in range(4):
            y = padding_top + chart_h * step / 3
            painter.drawLine(padding_side, int(y), width - padding_side, int(y))

        x = padding_side

        for label, value in self.data:
            bar_h = (value / max_value) * chart_h if max_value else 0
            y = padding_top + (chart_h - bar_h)

            grad = QLinearGradient(0, y, 0, y + max(bar_h, 1))
            grad.setColorAt(0.0, QColor(palette["GRAD_A"]))
            grad.setColorAt(1.0, QColor(palette["GRAD_B"]))
            painter.setPen(Qt.NoPen)
            painter.setBrush(grad)
            painter.drawRoundedRect(QRectF(x, y, bar_width, bar_h), 10, 10)

            # value on top of bar
            painter.setPen(QColor(palette["SOFT_TEXT"]))
            painter.drawText(
                int(x), int(y) - 22, int(bar_width), 18,
                Qt.AlignCenter, str(value)
            )

            # label under bar
            painter.setPen(QColor(palette["TEXT_LIGHT"]))
            painter.drawText(
                int(x) - 10, height - padding_bottom + 8, int(bar_width) + 20, 20,
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
        self.title_label.setObjectName("ChartTitle")
        layout.addWidget(self.title_label)

        self.chart = _BarChart(data)
        layout.addWidget(self.chart)

    def set_data(self, data):
        self.chart.set_data(data)
