"""
Cartify — Application Entry Point (PySide6)

Flow: Splash Screen -> Login Window -> Main Window
"""

import sys
import os

from PySide6.QtWidgets import QApplication

from gui.windows.splash_screen import SplashScreen
from gui.windows.login_window import LoginWindow
from gui.windows.main_window import MainWindow
from gui.styles import apply_theme


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Cartify")

    apply_theme(app, "light")

    asset_path = os.path.join(
        os.path.dirname(__file__), "gui", "assets"
    )

    app.main_window = None
    app._login_window = None
    app._splash = None

    def show_login():
        app._login_window = LoginWindow(asset_path)
        app._login_window.login_success.connect(show_main_window)
        app._login_window.show()

    def show_main_window(admin_name):
        app.main_window = MainWindow(app, admin_name)
        app.main_window.show()

    app._splash = SplashScreen(asset_path)
    app._splash.finished.connect(show_login)
    app._splash.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
