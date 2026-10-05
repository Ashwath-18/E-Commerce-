"""
Main Window
Lavender canvas -> rounded shell holding: floating Sidebar (left) and a
column with the Navbar (header) + a QStackedWidget holding every page.
Applies theme-aware drop-shadows / glows and keeps the logo, header icons
and shadows in sync with the active theme.
"""

import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget,
    QFrame, QGraphicsDropShadowEffect
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt

from gui.widgets.sidebar import Sidebar
from gui.widgets.navbar import Navbar
from gui.styles import apply_theme, colors

from gui.pages.dashboard_page import DashboardPage
from gui.pages.products_page import ProductsPage
from gui.pages.orders_page import OrdersPage
from gui.pages.shipping_page import ShippingPage
from gui.pages.users_page import UsersPage
from gui.pages.reviews_page import ReviewsPage
from gui.pages.search_page import SearchPage
from gui.pages.ai_page import AIAssistantPage
from gui.pages.analytics_page import AnalyticsPage
from gui.pages.settings_page import SettingsPage

SHADOW_OBJECT_NAMES = {"Card", "StatCard", "ChartCard", "FilterBar"}
HERO_SHADOW_OBJECT_NAMES = {"HeroCard", "AccentCardViolet", "AccentCardPink"}

PAGE_TITLES = {
    "dashboard": "Dashboard",
    "products": "Products",
    "orders": "Orders",
    "shipping": "Shipping",
    "users": "Users",
    "reviews": "Reviews",
    "search": "Search",
    "ai": "AI Assistant",
    "analytics": "Analytics",
    "settings": "Settings",
}


class MainWindow(QMainWindow):

    def __init__(self, app, admin_name="Administrator"):
        super().__init__()

        self.app = app
        self.current_theme = "light"
        self._logging_out = False

        self.setWindowTitle("Cartify")
        self.resize(1500, 880)
        self.setMinimumSize(1120, 700)

        self.asset_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "assets"
        )

        # ---------------- Canvas + Shell ----------------

        canvas = QFrame()
        canvas.setObjectName("Canvas")
        self.setCentralWidget(canvas)

        canvas_layout = QVBoxLayout(canvas)
        canvas_layout.setContentsMargins(18, 18, 18, 18)

        shell = QFrame()
        shell.setObjectName("Shell")
        canvas_layout.addWidget(shell)

        root_layout = QHBoxLayout(shell)
        root_layout.setContentsMargins(14, 14, 14, 14)
        root_layout.setSpacing(16)

        # ---------------- Sidebar ----------------

        self.sidebar = Sidebar(self.asset_path)
        self.sidebar.page_changed.connect(self.show_page)
        self.sidebar.logout_requested.connect(self.logout)
        root_layout.addWidget(self.sidebar)

        # ---------------- Main Column ----------------

        main_column = QVBoxLayout()
        main_column.setContentsMargins(0, 0, 10, 0)
        main_column.setSpacing(12)

        self.navbar = Navbar(self.asset_path)
        self.navbar.set_admin_name(admin_name)
        self.navbar.theme_toggle_requested.connect(self._toggle_theme)
        main_column.addWidget(self.navbar)

        self.stack = QStackedWidget()
        main_column.addWidget(self.stack, stretch=1)

        main_wrapper = QWidget()
        main_wrapper.setLayout(main_column)
        root_layout.addWidget(main_wrapper, stretch=1)

        # ---------------- Register Pages ----------------

        self.pages = {}

        self.dashboard_page = DashboardPage()
        self.dashboard_page.page_requested.connect(self.sidebar.select)
        self.products_page = ProductsPage()
        self.orders_page = OrdersPage()
        self.shipping_page = ShippingPage()
        self.users_page = UsersPage()
        self.reviews_page = ReviewsPage()
        self.search_page = SearchPage()
        self.ai_page = AIAssistantPage()
        self.analytics_page = AnalyticsPage()
        self.settings_page = SettingsPage()

        self.settings_page.theme_changed.connect(self.apply_theme)

        page_map = {
            "dashboard": self.dashboard_page,
            "products": self.products_page,
            "orders": self.orders_page,
            "shipping": self.shipping_page,
            "users": self.users_page,
            "reviews": self.reviews_page,
            "search": self.search_page,
            "ai": self.ai_page,
            "analytics": self.analytics_page,
            "settings": self.settings_page,
        }

        for key, widget in page_map.items():
            self.pages[key] = widget
            self.stack.addWidget(widget)

        self.navbar.set_theme(self.current_theme)
        self.show_page("dashboard")

        self._apply_shadows()

    def show_page(self, page_key):
        page = self.pages.get(page_key)
        if page:
            self.stack.setCurrentWidget(page)
            self.navbar.set_page_title(PAGE_TITLES.get(page_key, page_key.title()))

    def _toggle_theme(self):
        self.apply_theme("light" if self.current_theme == "dark" else "dark")

    def apply_theme(self, theme):
        self.current_theme = theme
        apply_theme(self.app, theme)

        # Keep branding (logo), header icons and shadows in sync
        self.navbar.set_theme(theme)
        self.sidebar.set_theme(theme)
        self.settings_page.set_theme(theme)
        self._apply_shadows()

    def _apply_shadows(self):
        """
        Light theme -> soft violet-tinted shadow.
        Dark theme  -> restrained violet glow that stays visible on
        deep indigo surfaces. Hero / accent cards get a stronger glow.
        """
        palette = colors.CURRENT
        soft = QColor(*palette["SHADOW"])
        hero = QColor(*palette["SHADOW_HERO"])

        for frame in self.findChildren(QFrame):
            name = frame.objectName()
            if name in SHADOW_OBJECT_NAMES:
                effect = QGraphicsDropShadowEffect(frame)
                effect.setBlurRadius(30)
                effect.setXOffset(0)
                effect.setYOffset(8)
                effect.setColor(soft)
                frame.setGraphicsEffect(effect)
            elif name in HERO_SHADOW_OBJECT_NAMES:
                effect = QGraphicsDropShadowEffect(frame)
                effect.setBlurRadius(38)
                effect.setXOffset(0)
                effect.setYOffset(14)
                effect.setColor(hero)
                frame.setGraphicsEffect(effect)

    def closeEvent(self, event):
        super().closeEvent(event)
        # Closing the window with the X button must end the application
        # (app.py disables quit-on-last-window-closed for splash/login).
        if not self._logging_out:
            QApplication.quit()

    def logout(self):
        from gui.windows.login_window import LoginWindow

        self._logging_out = True
        self.close()

        self._login_window = LoginWindow(self.asset_path)
        self._login_window.login_success.connect(self._on_relogin)
        self._login_window.show()

    def _on_relogin(self, admin_name):
        new_window = MainWindow(self.app, admin_name)
        new_window.apply_theme(self.current_theme)
        new_window.show()
        self.app.main_window = new_window
