"""
Login Window
Simple admin gate before the main app opens, styled to match the
premium theme with a floating shadowed card. Credentials are
hardcoded for now (admin / admin) — swap _check_credentials() for
a real auth check whenever you're ready.
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFrame,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QColor

DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin"


class LoginWindow(QWidget):

    login_success = Signal(str)  # emits admin display name

    def __init__(self, asset_path):
        super().__init__()

        self.setWindowTitle("Cartify — Login")
        self.setFixedSize(440, 520)

        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignCenter)
        outer.setContentsMargins(24, 24, 24, 24)

        card = QFrame()
        card.setObjectName("Card")
        card.setFixedWidth(370)

        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(36)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QColor(0, 0, 0, 45))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 34, 32, 30)
        layout.setSpacing(14)

        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        logo_path = os.path.join(asset_path, "logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(
                74, 74, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            logo_label.setPixmap(pixmap)
        layout.addWidget(logo_label)

        title = QLabel("Welcome Back")
        title.setObjectName("PageTitle")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Sign in to manage Cartify")
        subtitle.setObjectName("PageSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(12)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setText(DEFAULT_USERNAME)
        self.username_input.setFixedHeight(42)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(42)
        self.password_input.returnPressed.connect(self._attempt_login)

        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #E53935; font-size: 12px; background: transparent;")
        self.error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.error_label)

        login_btn = QPushButton("Login")
        login_btn.setObjectName("PrimaryButton")
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.setFixedHeight(44)
        login_btn.clicked.connect(self._attempt_login)
        layout.addWidget(login_btn)

        hint = QLabel("Default: admin / admin")
        hint.setObjectName("PageSubtitle")
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)

        outer.addWidget(card, alignment=Qt.AlignCenter)

    def showEvent(self, event):
        super().showEvent(event)
        self._center()

    def _center(self):
        screen = self.screen()
        if screen:
            geo = screen.availableGeometry()
            x = geo.center().x() - self.width() // 2
            y = geo.center().y() - self.height() // 2
            self.move(x, y)

    def _attempt_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if self._check_credentials(username, password):
            self.error_label.setText("")
            self.close()
            self.login_success.emit(username.capitalize() or "Administrator")
        else:
            self.error_label.setText("Invalid username or password.")

    def _check_credentials(self, username, password):
        return username == DEFAULT_USERNAME and password == DEFAULT_PASSWORD