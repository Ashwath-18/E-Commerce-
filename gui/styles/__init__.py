"""
Theme loader for Cartify.
Reads the .qss file matching the requested theme and applies it
to the whole QApplication.
"""

import os
from gui.styles import colors


def load_stylesheet(theme="light"):
    folder = os.path.dirname(__file__)
    filename = "light.qss" if theme == "light" else "dark.qss"
    path = os.path.join(folder, filename)

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def apply_theme(app, theme="light"):
    """
    Applies the stylesheet to the given QApplication instance
    and updates the active color palette pointer used by
    python-drawn widgets (chart_card, stat_card icons, etc).
    """
    colors.CURRENT = colors.get_palette(theme)
    app.setStyleSheet(load_stylesheet(theme))
