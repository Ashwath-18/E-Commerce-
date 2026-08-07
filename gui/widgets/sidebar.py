"""
Sidebar Widget
Left navigation panel with page switching + logout.
Logo swaps between logo_light.png / logo_dark.png based on theme,
matching the Navbar branding. Active state indicator (left accent
bar) is handled entirely via QSS (:checked).
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap


class Sidebar(QWidget):

    page_changed = Signal(str)
    logout_requested = Signal()

    NAV_ITEMS = [
        ("products", "Products", "products.png"),
        ("database", "Database", "database.png"),
        ("orders", "Orders", "orders.png"),
        ("shipping", "Shipping", "shipping.png"),
        ("users", "Users", "users.png"),
        ("reviews", "Reviews", "reviews.png"),
        ("search", "Search", "search.png"),
        ("ai", "AI Assistant", "ai.png"),
        ("analytics", "Analytics", "analytics.png"),
        ("settings", "Settings", "settings.png"),
    ]

    def __init__(self, asset_path, parent=None):
        super().__init__(parent)

        self.asset_path = asset_path
        self.current_theme = "light"
        self.buttons = {}
        self.active_page = "dashboard"

        self.setObjectName("Sidebar")
        self.setFixedWidth(270)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 26, 0, 0)
        layout.setSpacing(0)

        # ---------------- Logo ----------------

        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo_label)

        self._load_logo()

        # ---------------- Title ----------------

        title = QLabel("Cartify")
        title.setObjectName("SidebarTitle")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        divider = QFrame()
        divider.setObjectName("SidebarDivider")
        divider.setFixedHeight(1)
        layout.addWidget(divider)

        # ---------------- Scrollable Nav ----------------

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        nav_container = QWidget()
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(14, 6, 14, 10)
        nav_layout.setSpacing(4)

        dashboard_btn = self._create_nav_button("Dashboard", "dashboard.png")
        dashboard_btn.clicked.connect(lambda: self.select("dashboard"))
        nav_layout.addWidget(dashboard_btn)
        self.buttons["dashboard"] = dashboard_btn

        for key, label, icon_file in self.NAV_ITEMS:
            btn = self._create_nav_button(label, icon_file)
            btn.clicked.connect(lambda checked=False, k=key: self.select(k))
            nav_layout.addWidget(btn)
            self.buttons[key] = btn

        nav_layout.addStretch()

        logout_btn = self._create_nav_button("Logout", "logout.png")
        logout_btn.clicked.connect(self.logout_requested.emit)
        nav_layout.addWidget(logout_btn)

        scroll.setWidget(nav_container)
        layout.addWidget(scroll)

        self.select("dashboard")

    def _create_nav_button(self, text, icon_file):
        btn = QPushButton("   " + text)
        btn.setObjectName("NavButton")
        btn.setCheckable(True)
        btn.setFixedHeight(50)
        btn.setCursor(Qt.PointingHandCursor)

        icon_path = os.path.join(self.asset_path, icon_file)
        if os.path.exists(icon_path):
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(22, 22))

        return btn

    def select(self, page_key):
        for key, btn in self.buttons.items():
            btn.setChecked(key == page_key)

        self.active_page = page_key
        self.page_changed.emit(page_key)

    def set_theme(self, theme):
        """Called by MainWindow whenever the theme is switched."""
        self.current_theme = theme
        self._load_logo()

    def _load_logo(self):
        filename = "logo_dark.png" if self.current_theme == "dark" else "logo_light.png"
        logo_path = os.path.join(self.asset_path, filename)

        if not os.path.exists(logo_path):
            logo_path = os.path.join(self.asset_path, "logo.png")

        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(
                88, 88, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.logo_label.setPixmap(pixmap)
        else:
            self.logo_label.clear()