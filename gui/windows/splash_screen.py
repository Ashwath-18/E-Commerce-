"""
Splash Screen
Frameless, translucent floating card with logo + spinner —
matches the new premium theme. Emits finished so app.py can move
on to the login window.
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPixmap, QColor

from gui.widgets.loading_spinner import LoadingSpinner


class SplashScreen(QWidget):

    finished = Signal()

    def __init__(self, asset_path, duration_ms=1800):
        super().__init__()

        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(440, 460)

        # Outer layout is transparent — gives the inner card
        # room to "float" with a visible drop-shadow around it.
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)

        card = QFrame()
        card.setObjectName("Card")

        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(40)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 70))
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignCenter)
        card_layout.setSpacing(14)
        card_layout.setContentsMargins(30, 30, 30, 30)

        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)

        logo_path = os.path.join(asset_path, "logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(
                120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            logo_label.setPixmap(pixmap)

        title = QLabel("CARTIFY")
        title.setObjectName("PageTitle")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Smart E-Commerce Platform")
        subtitle.setObjectName("PageSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        self.spinner = LoadingSpinner(size=34)

        card_layout.addWidget(logo_label)
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(8)
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