"""
Notification Widget
A small toast-style popup shown briefly over a parent window
to confirm success, warn, or report errors.
"""

from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, QTimer

from gui.styles import colors


class Notification(QLabel):

    def __init__(self, parent, message, kind="success", duration_ms=2500):
        super().__init__(parent)

        palette = colors.CURRENT

        color_map = {
            "success": palette["SUCCESS"],
            "warning": palette["WARNING"],
            "error": palette["DANGER"],
        }

        bg = color_map.get(kind, palette["SUCCESS"])

        self.setText("  " + message + "  ")
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(
            f"""
            background-color: {bg};
            color: white;
            font-weight: 600;
            font-size: 13px;
            border-radius: 10px;
            padding: 10px 18px;
            """
        )

        self.adjustSize()
        self._position(parent)
        self.show()
        self.raise_()

        QTimer.singleShot(duration_ms, self.close)

    def _position(self, parent):
        if not parent:
            return
        parent_rect = parent.rect()
        x = (parent_rect.width() - self.width()) // 2
        y = 30
        self.move(x, y)


def show_notification(parent, message, kind="success", duration_ms=2500):
    """
    Convenience function.
    kind: "success" | "warning" | "error"
    """
    return Notification(parent, message, kind, duration_ms)
