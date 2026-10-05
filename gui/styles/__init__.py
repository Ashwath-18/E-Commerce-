"""
Theme loader for Cartify.
Reads the .qss file matching the requested theme and applies it
to the whole QApplication.

* `@ASSETS@` inside a .qss file is replaced with the absolute path of
  gui/assets, so dropdown / spinner / calendar arrows load correctly no
  matter which folder the app is launched from.
* After the stylesheet is applied, every theme-aware icon is re-tinted.
"""

import os
from gui.styles import colors

ASSETS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets"
)


def load_stylesheet(theme="light"):
    folder = os.path.dirname(__file__)
    filename = "light.qss" if theme == "light" else "dark.qss"
    path = os.path.join(folder, filename)

    with open(path, "r", encoding="utf-8") as f:
        css = f.read()

    return css.replace("@ASSETS@", ASSETS_DIR.replace("\\", "/"))


def apply_theme(app, theme="light"):
    """
    Applies the stylesheet to the given QApplication instance
    and updates the active color palette pointer used by
    python-drawn widgets (charts, icons, badges, etc).
    """
    colors.CURRENT = colors.get_palette(theme)
    app.setStyleSheet(load_stylesheet(theme))

    # Imported lazily: icons imports this package for the palette.
    from gui.widgets import icons
    icons.refresh_all()
