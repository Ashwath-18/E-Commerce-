"""
Cartify — Centralized Color Palette (PySide6)
Pure white / pure black monochrome base with a violet brand accent.
"""

# -----------------------------
# LIGHT THEME — Pure White
# -----------------------------
LIGHT = {
    "BACKGROUND": "#FFFFFF",
    "SIDEBAR": "#FFFFFF",
    "CARD": "#FFFFFF",

    "PRIMARY": "#5A3DFF",       # violet brand accent
    "SECONDARY": "#7C6CFF",
    "ACCENT": "#0A0A0A",

    "TEXT": "#0A0A0A",
    "TEXT_LIGHT": "#6B7280",

    "BORDER": "#EAEAEA",

    "SIDEBAR_TEXT": "#0A0A0A",
    "SIDEBAR_TEXT_MUTED": "#8A8A8A",
    "SIDEBAR_ACTIVE_BG": "#F1EEFF",
    "SIDEBAR_ACTIVE_TEXT": "#5A3DFF",

    "HOVER": "#F5F5F7",

    "SUCCESS": "#16A34A",
    "WARNING": "#F59E0B",
    "DANGER": "#DC2626",
}

# -----------------------------
# DARK THEME — Pure Black
# -----------------------------
DARK = {
    "BACKGROUND": "#000000",
    "SIDEBAR": "#000000",
    "CARD": "#0B0B0B",

    "PRIMARY": "#7C6CFF",
    "SECONDARY": "#9B8FFF",
    "ACCENT": "#FFFFFF",

    "TEXT": "#FFFFFF",
    "TEXT_LIGHT": "#BFC4CF",

    "BORDER": "#1E1E1E",

    "SIDEBAR_TEXT": "#FFFFFF",
    "SIDEBAR_TEXT_MUTED": "#7A7A7A",
    "SIDEBAR_ACTIVE_BG": "#1B1640",
    "SIDEBAR_ACTIVE_TEXT": "#9B8FFF",

    "HOVER": "#111111",

    "SUCCESS": "#22C55E",
    "WARNING": "#FBBF24",
    "DANGER": "#F87171",
}

CURRENT = LIGHT


def get_palette(theme="light"):
    return LIGHT if theme == "light" else DARK


# -----------------------------
# Fonts
# -----------------------------
FONT_FAMILY = "Segoe UI"

TITLE_FONT_SIZE = 26
HEADING_FONT_SIZE = 18
STAT_FONT_SIZE = 28
SUB_FONT_SIZE = 13
LABEL_FONT_SIZE = 12
BUTTON_FONT_SIZE = 14

# -----------------------------
# Sizes
# -----------------------------
SIDEBAR_WIDTH = 270
CARD_RADIUS = 18
NAV_BUTTON_HEIGHT = 50