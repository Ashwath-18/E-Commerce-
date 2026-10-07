"""
InteractiveAreaChart
The dashboard's smooth area curve, plus:

* hover  - the value bubble follows the mouse
* click  - emits point_clicked(index) for the column under the cursor
* scale modes: "sqrt" (overview, keeps small collections visible),
               "zero" (honest zero-based bars-as-curve),
               "auto" (zoomed to the data range, good for monthly trends)
* a custom message when there is nothing to draw ("Loading...", etc.)
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter

from gui.styles import colors
from gui.widgets.chart_card import AreaChart


class InteractiveAreaChart(AreaChart):

    point_clicked = Signal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseTracking(True)
        self.scale_mode = "sqrt"
        self.message = "No data"
        self._clickable = True
        self._selected = None

    # ---------------- public ----------------

    def set_data(self, data, highlight=None):
        self._selected = highlight
        super().set_data(data, highlight)

    def set_clickable(self, enabled):
        self._clickable = enabled
        self.setCursor(Qt.PointingHandCursor if enabled and self.data else Qt.ArrowCursor)

    def set_message(self, text):
        self.message = text
        self.update()

    # ---------------- geometry ----------------

    def _index_at(self, x):
        count = len(self.data)
        if count == 0:
            return None
        margin = 40 if self.show_labels else 18
        chart_w = max(self.width() - 2 * margin, 1)
        denom = max(count - 1, 1)
        index = round((x - margin) / chart_w * denom)
        return min(max(index, 0), count - 1)

    # ---------------- mouse ----------------

    def mouseMoveEvent(self, event):
        index = self._index_at(event.position().x())
        if index is not None and index != self.highlight:
            self.highlight = index
            self.update()
        self.setCursor(Qt.PointingHandCursor if self._clickable and self.data else Qt.ArrowCursor)
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self.highlight = self._selected
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self._clickable and self.data:
            index = self._index_at(event.position().x())
            if index is not None:
                self.point_clicked.emit(index)
        super().mousePressEvent(event)

    # ---------------- drawing ----------------

    def _scaled(self, value, max_value):
        if self.scale_mode == "sqrt":
            return super()._scaled(value, max_value)

        values = [v for _, v in self.data] or [0]
        if self.scale_mode == "auto":
            low = min(values)
            span = max_value - low
            return 0.7 if span <= 0 else 0.3 + 0.7 * (value - low) / span
        return value / max_value if max_value > 0 else 0.0

    def paintEvent(self, event):
        if not self.data:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(QColor(255, 255, 255, 190) if self.on_gradient else QColor(colors.CURRENT["TEXT_LIGHT"]))
            painter.setFont(QFont(colors.FONT_FAMILY, 11))
            painter.drawText(self.rect().adjusted(20, 0, -20, 0), Qt.AlignCenter | Qt.TextWordWrap, self.message)
            return
        super().paintEvent(event)
