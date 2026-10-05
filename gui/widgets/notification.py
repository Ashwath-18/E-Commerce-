"""
Notification Widget
A gradient toast shown briefly over a parent widget to confirm success,
warn, or report errors.
"""

from PySide6.QtWidgets import QGraphicsDropShadowEffect, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor

from gui.styles import colors


class Notification(QLabel):

    GLYPHS = {"success": "✓", "warning": "!", "error": "✕"}

    def __init__(self, parent, message, kind="success", duration_ms=2500):
        super().__init__(parent)

        palette = colors.CURRENT

        gradients = {
            "success": (palette["GREEN_A"], palette["GREEN_B"]),
            "warning": (palette["AMBER_A"], palette["AMBER_B"]),
            "error": (palette["DANGER"], "#B8323F"),
        }
        start, end = gradients.get(kind, gradients["success"])
        glyph = self.GLYPHS.get(kind, "✓")

        self.setText(f"{glyph}    {message}")
        self.setAlignment(Qt.AlignCenter)
        self.setWordWrap(True)
        self.setStyleSheet(
            f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {start}, stop:1 {end});
            color: white;
            font-weight: 700;
            font-size: 13px;
            border: 1px solid rgba(255, 255, 255, 70);
            border-radius: 20px;
            padding: 12px 24px;
            """
        )

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(26)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 70))
        self.setGraphicsEffect(shadow)

        max_width = max(260, (parent.width() - 48) if parent else 520)
        text_width = int(self.fontMetrics().horizontalAdvance(self.text()) * 1.3) + 64
        self.setFixedWidth(min(max(text_width, 220), max_width))
        self.ensurePolished()
        self.setFixedHeight(max(self.heightForWidth(self.width()), 46))
        self._position(parent)
        self.show()
        self.raise_()

        QTimer.singleShot(duration_ms, self.close)

    def _position(self, parent):
        if not parent:
            return
        parent_rect = parent.rect()
        x = (parent_rect.width() - self.width()) // 2
        y = 24
        self.move(max(x, 8), y)


def show_notification(parent, message, kind="success", duration_ms=2500):
    """
    Convenience function.
    kind: "success" | "warning" | "error"
    """
    return Notification(parent, message, kind, duration_ms)
