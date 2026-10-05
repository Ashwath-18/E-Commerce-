"""
Splash Screen
Frameless, translucent floating violet card with logo + spinner —
matches the premium theme. Emits finished so app.py can move
on to the login window.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColor

from gui.widgets import icons
from gui.widgets.loading_spinner import LoadingSpinner


class SplashScreen(QWidget):

    finished = Signal()

    def __init__(self, asset_path, duration_ms=1800):
        super().__init__()

        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(460, 480)

        # Outer layout is transparent — gives the inner card
        # room to "float" with a visible glow around it.
        outer = QVBoxLayout(self)
        outer.setContentsMargins(26, 26, 26, 26)

        card = QFrame()
        card.setObjectName("SplashCard")

        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(46)
        shadow.setXOffset(0)
        shadow.setYOffset(14)
        shadow.setColor(QColor(60, 40, 170, 120))
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignCenter)
        card_layout.setSpacing(12)
        card_layout.setContentsMargins(30, 30, 30, 30)

        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        pix = icons.logo_pixmap(asset_path, "dark", 96)
        if pix is not None:
            logo_label.setPixmap(pix)

        title = QLabel("CARTIFY")
        title.setObjectName("SplashTitle")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Smart E-Commerce Platform")
        subtitle.setObjectName("SplashSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        self.spinner = LoadingSpinner(size=36, color="#FFFFFF")

        card_layout.addWidget(logo_label)
        card_layout.addSpacing(6)
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(14)
        card_layout.addWidget(self.spinner, alignment=Qt.AlignCenter)

        outer.addWidget(card)

        QTimer.singleShot(duration_ms, self._finish)

    def showEvent(self, event):
        super().showEvent(event)
        self._center()
        self.spinner.start()

    def _finish(self):
        self.spinner.stop()
        self.close()
        self.finished.emit()

    def _center(self):
        screen = self.screen()
        if screen:
            geo = screen.availableGeometry()
            x = geo.center().x() - self.width() // 2
            y = geo.center().y() - self.height() // 2
            self.move(x, y)
