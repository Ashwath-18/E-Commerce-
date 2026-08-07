"""
Navbar Widget
Top header bar showing branding + admin avatar/name.
Logo swaps automatically between logo_light.png / logo_dark.png
based on the active theme. All colors come from the stylesheet
(#NavbarTitle, #NavbarSubtitle, #NavbarAdmin, #AdminAvatar) —
nothing is hardcoded here.
"""

import os
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap


class Navbar(QWidget):

    def __init__(self, asset_path, parent=None):
        super().__init__(parent)

        self.asset_path = asset_path
        self.current_theme = "light"

        self.setObjectName("Navbar")
        self.setFixedHeight(90)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 10, 26, 10)

        # ---------------- Logo ----------------

        self.logo_label = QLabel()
        layout.addWidget(self.logo_label)

        # ---------------- Title Block ----------------

        title_block = QVBoxLayout()
        title_block.setSpacing(2)

        title = QLabel("CARTIFY")
        title.setObjectName("NavbarTitle")

        subtitle = QLabel("Smart E-Commerce Platform")
        subtitle.setObjectName("NavbarSubtitle")

        title_block.addWidget(title)
        title_block.addWidget(subtitle)

        layout.addSpacing(12)
        layout.addLayout(title_block)

        layout.addStretch()

        # ---------------- Admin Avatar + Name ----------------

        self.avatar_label = QLabel("A")
        self.avatar_label.setObjectName("AdminAvatar")
        self.avatar_label.setFixedSize(36, 36)
        self.avatar_label.setAlignment(Qt.AlignCenter)

        self.admin_label = QLabel("Administrator")
        self.admin_label.setObjectName("NavbarAdmin")

        layout.addWidget(self.avatar_label)
        layout.addSpacing(10)
        layout.addWidget(self.admin_label)

        self._load_logo()

    def set_admin_name(self, name):
        self.admin_label.setText(name)
        self.avatar_label.setText(name[:1].upper() if name else "A")

    def set_theme(self, theme):
        """Called by MainWindow whenever the theme is switched."""
        self.current_theme = theme
        self._load_logo()

    def _load_logo(self):
        filename = "logo_dark.png" if self.current_theme == "dark" else "logo_light.png"
        logo_path = os.path.join(self.asset_path, filename)

        # Falls back to the original logo.png if the themed
        # asset hasn't been added to gui/assets yet.
        if not os.path.exists(logo_path):
            logo_path = os.path.join(self.asset_path, "logo.png")

        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(
                58, 58, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.logo_label.setPixmap(pixmap)
        else:
            self.logo_label.clear()