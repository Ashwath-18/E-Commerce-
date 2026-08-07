"""
Main Window
Combines Sidebar (left nav) + Navbar (top header) + a QStackedWidget
holding every page. Applies theme-aware drop-shadows, and keeps
the Navbar/Sidebar logo in sync with the active theme.
"""

import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget,
    QFrame, QGraphicsDropShadowEffect
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt

from gui.widgets.sidebar import Sidebar
from gui.widgets.navbar import Navbar
from gui.styles import apply_theme

from gui.pages.dashboard_page import DashboardPage
from gui.pages.products_page import ProductsPage
from gui.pages.database_page import DatabasePage
from gui.pages.orders_page import OrdersPage
from gui.pages.shipping_page import ShippingPage
from gui.pages.users_page import UsersPage
from gui.pages.reviews_page import ReviewsPage
from gui.pages.search_page import SearchPage
from gui.pages.ai_page import AIAssistantPage
from gui.pages.analytics_page import AnalyticsPage
from gui.pages.settings_page import SettingsPage

SHADOW_OBJECT_NAMES = {"Card", "StatCard", "ChartCard", "Navbar"}


class MainWindow(QMainWindow):

    def __init__(self, app, admin_name="Administrator"):
        super().__init__()

        self.app = app
        self.current_theme = "light"

        self.setWindowTitle("Cartify")
        self.resize(1500, 850)
        self.setMinimumSize(1300, 750)

        self.asset_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "assets"
        )

        # ---------------- Central Layout ----------------

        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ---------------- Sidebar ----------------

        self.sidebar = Sidebar(self.asset_path)
        self.sidebar.page_changed.connect(self.show_page)
        self.sidebar.logout_requested.connect(self.logout)
        root_layout.addWidget(self.sidebar)

        # ---------------- Main Column ----------------

        main_column = QVBoxLayout()
        main_column.setContentsMargins(22, 22, 22, 22)
        main_column.setSpacing(22)

        self.navbar = Navbar(self.asset_path)
        self.navbar.set_admin_name(admin_name)
        main_column.addWidget(self.navbar)

        self.stack = QStackedWidget()
        main_column.addWidget(self.stack, stretch=1)

        main_wrapper = QWidget()
        main_wrapper.setLayout(main_column)
        root_layout.addWidget(main_wrapper, stretch=1)

        # ---------------- Register Pages ----------------

        self.pages = {}

        self.dashboard_page = DashboardPage()
        self.products_page = ProductsPage()
        self.database_page = DatabasePage()
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
            "database": self.database_page,
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

        self.show_page("dashboard")

        self._apply_shadows()

    def show_page(self, page_key):
        page = self.pages.get(page_key)
        if page:
            self.stack.setCurrentWidget(page)

    def apply_theme(self, theme):
        self.current_theme = theme
        apply_theme(self.app, theme)

        # Keep branding (logo) and shadows in sync with the new theme
        self.navbar.set_theme(theme)
        self.sidebar.set_theme(theme)
        self._apply_shadows()

    def _apply_shadows(self):
        """
        Light theme -> subtle black shadow.
        Dark theme  -> subtle white glow (black shadow is invisible
        on a pure black background).
        """
        is_dark = self.current_theme == "dark"
        shadow_color = QColor(255, 255, 255, 18) if is_dark else QColor(0, 0, 0, 35)

        for frame in self.findChildren(QFrame):
            if frame.objectName() in SHADOW_OBJECT_NAMES:
                effect = QGraphicsDropShadowEffect(frame)
                effect.setBlurRadius(24)
                effect.setXOffset(0)
                effect.setYOffset(6 if not is_dark else 0)
                effect.setColor(shadow_color)
                frame.setGraphicsEffect(effect)

    def logout(self):
        from gui.windows.login_window import LoginWindow

        self.close()

        self._login_window = LoginWindow(self.asset_path)
        self._login_window.login_success.connect(self._on_relogin)
        self._login_window.show()

    def _on_relogin(self, admin_name):
        new_window = MainWindow(self.app, admin_name)
        new_window.apply_theme(self.current_theme)
        new_window.show()
        self.app.main_window = new_window