"""
Sidebar Widget
Floating violet navigation pill with page switching + logout.

* Expanded: logo, brand, icon + label for every page.
* Collapsed: icon-only rail (like the reference) with tooltips.
The logo is white-on-violet (logo_dark.png) in both themes because the
pill is violet in both themes.
"""

import os

from PySide6.QtCore import QEasingCurve, QSize, QVariantAnimation, Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget,
)

from gui.styles import colors
from gui.widgets import icons


class Sidebar(QFrame):

    page_changed = Signal(str)
    logout_requested = Signal()

    # (key, label, icon glyph)
    NAV_ITEMS = [
        ("products", "Products", "products"),
        ("orders", "Orders", "orders"),
        ("shipping", "Shipping", "shipping"),
        ("users", "Users", "users"),
        ("reviews", "Reviews", "reviews"),
        ("search", "Search", "search"),
        ("ai", "AI Assistant", "ai"),
        ("analytics", "Analytics", "analytics"),
        ("settings", "Settings", "settings"),
    ]

    def __init__(self, asset_path, parent=None):
        super().__init__(parent)

        self.asset_path = asset_path
        self.current_theme = "light"
        self.buttons = {}
        self.active_page = "dashboard"
        self._collapsed = False
        self._labels = {}

        self.setObjectName("Sidebar")
        self.setFixedWidth(colors.SIDEBAR_WIDTH)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 24, 14, 16)
        layout.setSpacing(0)

        # ---------------- Brand ----------------

        brand = QHBoxLayout()
        brand.setContentsMargins(6, 0, 6, 0)
        brand.setSpacing(12)

        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        brand.addWidget(self.logo_label)

        self.brand_text = QWidget()
        text_layout = QVBoxLayout(self.brand_text)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(0)
        title = QLabel("Cartify")
        title.setObjectName("SidebarTitle")
        caption = QLabel("Smart E-Commerce")
        caption.setObjectName("SidebarCaption")
        text_layout.addWidget(title)
        text_layout.addWidget(caption)
        brand.addWidget(self.brand_text, stretch=1)

        self.brand_row = QWidget()
        self.brand_row.setLayout(brand)
        layout.addWidget(self.brand_row)
        layout.addSpacing(18)

        self._load_logo()

        divider = QFrame()
        divider.setObjectName("SidebarDivider")
        divider.setFixedHeight(1)
        layout.addWidget(divider)
        layout.addSpacing(14)

        # ---------------- Scrollable Nav ----------------

        scroll = QScrollArea()
        scroll.setObjectName("SidebarScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.viewport().setAutoFillBackground(False)

        nav_container = QWidget()
        nav_container.setObjectName("SidebarNav")
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(6)

        dashboard_btn = self._create_nav_button("Dashboard", "dashboard")
        dashboard_btn.clicked.connect(lambda: self.select("dashboard"))
        nav_layout.addWidget(dashboard_btn)
        self.buttons["dashboard"] = dashboard_btn

        for key, label, glyph in self.NAV_ITEMS:
            btn = self._create_nav_button(label, glyph)
            btn.clicked.connect(lambda checked=False, k=key: self.select(k))
            nav_layout.addWidget(btn)
            self.buttons[key] = btn

        nav_layout.addStretch()
        scroll.setWidget(nav_container)
        layout.addWidget(scroll, stretch=1)

        # ---------------- Footer ----------------

        layout.addSpacing(8)

        self.collapse_btn = self._create_nav_button("Collapse", "chevron_left", checkable=False)
        self.collapse_btn.clicked.connect(self.toggle_collapsed)
        layout.addWidget(self.collapse_btn)
        layout.addSpacing(6)

        logout_btn = self._create_nav_button("Logout", "logout", checkable=False)
        logout_btn.clicked.connect(self.logout_requested.emit)
        layout.addWidget(logout_btn)
        self.logout_btn = logout_btn

        self.select("dashboard")

    # ---------------- Buttons ----------------

    def _create_nav_button(self, text, glyph, checkable=True):
        btn = QPushButton("  " + text)
        btn.setObjectName("NavButton")
        btn.setCheckable(checkable)
        btn.setFixedHeight(48)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setToolTip(text)
        btn.setProperty("collapsed", False)
        self._labels[btn] = text
        icons.bind(btn, glyph, 22, "nav")
        return btn

    def select(self, page_key):
        for key, btn in self.buttons.items():
            btn.setChecked(key == page_key)

        self.active_page = page_key
        self.page_changed.emit(page_key)

    # ---------------- Collapse ----------------

    def is_collapsed(self):
        return self._collapsed

    def toggle_collapsed(self):
        self.set_collapsed(not self._collapsed)

    def set_collapsed(self, collapsed):
        if collapsed == self._collapsed:
            return
        self._collapsed = collapsed

        target = colors.SIDEBAR_RAIL_WIDTH if collapsed else colors.SIDEBAR_WIDTH

        if collapsed:
            self._apply_collapsed_state(True)

        anim = QVariantAnimation(self)
        anim.setDuration(180)
        anim.setStartValue(self.width())
        anim.setEndValue(target)
        anim.setEasingCurve(QEasingCurve.InOutCubic)
        anim.valueChanged.connect(lambda v: self.setFixedWidth(int(v)))
        if not collapsed:
            anim.finished.connect(lambda: self._apply_collapsed_state(False))
        anim.start(QVariantAnimation.DeleteWhenStopped)
        self._anim = anim

    def _apply_collapsed_state(self, collapsed):
        self.brand_text.setVisible(not collapsed)

        all_buttons = list(self.buttons.values()) + [self.collapse_btn, self.logout_btn]
        for btn in all_buttons:
            btn.setText("" if collapsed else "  " + self._labels[btn])
            btn.setProperty("collapsed", collapsed)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        icons.rebind(self.collapse_btn, "chevron_right" if collapsed else "chevron_left")

    # ---------------- Theme / logo ----------------

    def set_theme(self, theme):
        """Called by MainWindow whenever the theme is switched."""
        self.current_theme = theme
        self._load_logo()

    def _load_logo(self):
        pix = icons.logo_pixmap(self.asset_path, "dark", 40)
        if pix is not None:
            self.logo_label.setPixmap(pix)
        else:
            self.logo_label.clear()
