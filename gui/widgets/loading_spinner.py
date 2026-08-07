"""
Loading Spinner Widget
A lightweight rotating-arc spinner drawn with QPainter — no
external gif/asset dependency required.
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtCore import Qt, QTimer

from gui.styles import colors


class LoadingSpinner(QWidget):

    def __init__(self, parent=None, size=40, line_width=4):
        super().__init__(parent)

        self._angle = 0
        self._size = size
        self._line_width = line_width

        self.setFixedSize(size, size)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate)
        self._timer.setInterval(40)

    def start(self):
        self.show()
        self._timer.start()

    def stop(self):
        self._timer.stop()
        self.hide()

    def _rotate(self):
        self._angle = (self._angle + 20) % 360
        self.update()

    def paintEvent(self, event):
        palette = colors.CURRENT

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(QColor(palette["PRIMARY"]))
        pen.setWidth(self._line_width)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)

        rect = self.rect().adjusted(
            self._line_width, self._line_width,
            -self._line_width, -self._line_width
        )

        span_angle = 120 * 16
        start_angle = -self._angle * 16

        painter.drawArc(rect, start_angle, span_angle)
