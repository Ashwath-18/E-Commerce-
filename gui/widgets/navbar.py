"""
Navbar Widget
Slim header: breadcrumb on the left; theme switch and the signed-in admin
chip on the right. All colors come from the stylesheet.
"""

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QToolButton, QVBoxLayout,
)

from gui.widgets import icons


class Navbar(QFrame):

    theme_toggle_requested = Signal()

    def __init__(self, asset_path, parent=None):
        super().__init__(parent)

        self.asset_path = asset_path
        self.current_theme = "light"

        self.setObjectName("Navbar")
        self.setFixedHeight(66)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 4, 4)
        layout.setSpacing(0)

        # ---------------- Breadcrumb ----------------

        crumb = QLabel("Cartify")
        crumb.setObjectName("NavbarCrumb")
        layout.addWidget(crumb)

        self.crumb_sep = QLabel()
        self.crumb_sep.setFixedSize(22, 22)
        self.crumb_sep.setAlignment(Qt.AlignCenter)
        icons.bind(self.crumb_sep, "chevron_right", 14, "muted")
        layout.addWidget(self.crumb_sep)

        self.page_label = QLabel("Dashboard")
        self.page_label.setObjectName("NavbarTitle")
        layout.addWidget(self.page_label)

        layout.addStretch()

        # ---------------- Theme toggle ----------------

        self.theme_button = QToolButton()
        self.theme_button.setObjectName("ThemeToggle")
        self.theme_button.setFixedSize(46, 46)
        self.theme_button.setCursor(Qt.PointingHandCursor)
        self.theme_button.setIconSize(QSize(22, 22))
        self.theme_button.clicked.connect(self.theme_toggle_requested.emit)
        icons.bind(self.theme_button, "moon", 22, "accent")
        layout.addWidget(self.theme_button)
        layout.addSpacing(12)

        # ---------------- Admin chip ----------------

        chip = QFrame()
        chip.setObjectName("NavbarUserChip")
        chip.setFixedHeight(50)
        chip_layout = QHBoxLayout(chip)
        chip_layout.setContentsMargins(7, 7, 18, 7)
        chip_layout.setSpacing(10)

        self.avatar_label = QLabel("A")
        self.avatar_label.setObjectName("AdminAvatar")
        self.avatar_label.setFixedSize(36, 36)
        self.avatar_label.setAlignment(Qt.AlignCenter)
        chip_layout.addWidget(self.avatar_label)

        text_block = QVBoxLayout()
        text_block.setSpacing(0)
        text_block.setContentsMargins(0, 0, 0, 0)
        self.admin_label = QLabel("Administrator")
        self.admin_label.setObjectName("NavbarAdmin")
        role = QLabel("Admin access")
        role.setObjectName("NavbarRole")
        text_block.addWidget(self.admin_label)
        text_block.addWidget(role)
        chip_layout.addLayout(text_block)

        layout.addWidget(chip)

    def set_admin_name(self, name):
        self.admin_label.setText(name)
        self.avatar_label.setText(name[:1].upper() if name else "A")

    def set_page_title(self, title):
        self.page_label.setText(title)

    def set_theme(self, theme):
        """Called by MainWindow whenever the theme is switched."""
        self.current_theme = theme
        # moon = "switch to dark", sun = "switch to light"
        icons.rebind(self.theme_button, "sun" if theme == "dark" else "moon")
        self.theme_button.setToolTip(
            "Switch to light theme" if theme == "dark" else "Switch to dark theme"
        )
