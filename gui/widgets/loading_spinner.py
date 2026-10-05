"""
Loading Spinner Widget
A lightweight rotating gradient-arc spinner drawn with QPainter — no
external gif/asset dependency required.
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen, QColor, QConicalGradient, QBrush
from PySide6.QtCore import Qt, QTimer, QRectF

from gui.styles import colors


class LoadingSpinner(QWidget):

    def __init__(self, parent=None, size=40, line_width=4, color=None):
        """color: optional hex string (e.g. "#FFFFFF") for use on gradients."""
        super().__init__(parent)

        self._angle = 0
        self._size = size
        self._line_width = line_width
        self._color = color

        self.setFixedSize(size, size)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate)
        self._timer.setInterval(30)

    def start(self):
        self.show()
        self._timer.start()

    def stop(self):
        self._timer.stop()
        self.hide()

    def _rotate(self):
        self._angle = (self._angle + 12) % 360
        self.update()

    def paintEvent(self, event):
        palette = colors.CURRENT
        base = QColor(self._color or palette["PRIMARY"])

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        half = self._line_width / 2 + 1
        rect = QRectF(self.rect()).adjusted(half, half, -half, -half)

        # faint full track
        track = QColor(base)
        track.setAlpha(46)
        painter.setPen(QPen(track, self._line_width, Qt.SolidLine, Qt.RoundCap))
        painter.drawEllipse(rect)

        # comet-tail arc
        head = QColor(base)
        tail = QColor(base)
        tail.setAlpha(0)
        grad = QConicalGradient(rect.center(), -self._angle)
        grad.setColorAt(0.0, head)
        grad.setColorAt(0.7, tail)
        grad.setColorAt(1.0, tail)

        pen = QPen(QBrush(grad), self._line_width, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect, int(-self._angle * 16), 252 * 16)
