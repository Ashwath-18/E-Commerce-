"""
Cartify - Centralized Color Palette (PySide6).
Soft neutral surfaces with a violet brand accent.
"""

# -----------------------------
# LIGHT THEME
# -----------------------------
LIGHT = {
    "BACKGROUND": "#F8FAFC",
    "SIDEBAR": "#FFFFFF",
    "CARD": "#FFFFFF",

    "PRIMARY": "#4F46E5",
    "SECONDARY": "#7C3AED",
    "ACCENT": "#3730A3",

    "TEXT": "#111827",
    "TEXT_LIGHT": "#64748B",

    "BORDER": "#E5E7EB",

    "SIDEBAR_TEXT": "#111827",
    "SIDEBAR_TEXT_MUTED": "#6B7280",
    "SIDEBAR_ACTIVE_BG": "#EEF2FF",
    "SIDEBAR_ACTIVE_TEXT": "#4F46E5",

    "HOVER": "#F3F4F8",

    "SUCCESS": "#16A34A",
    "WARNING": "#F59E0B",
    "DANGER": "#DC2626",
}

# -----------------------------
# DARK THEME
# -----------------------------
DARK = {
    "BACKGROUND": "#09090F",
    "SIDEBAR": "#0D0D16",
    "CARD": "#0F0F1A",

    "PRIMARY": "#A78BFA",
    "SECONDARY": "#7C3AED",
    "ACCENT": "#DDD6FE",

    "TEXT": "#F8FAFC",
    "TEXT_LIGHT": "#A5ADBD",

    "BORDER": "#232335",

    "SIDEBAR_TEXT": "#F8FAFC",
    "SIDEBAR_TEXT_MUTED": "#A5ADBD",
    "SIDEBAR_ACTIVE_BG": "#211C4D",
    "SIDEBAR_ACTIVE_TEXT": "#C4B5FD",

    "HOVER": "#171727",

    "SUCCESS": "#22C55E",
    "WARNING": "#FBBF24",
    "DANGER": "#EF4444",
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
SIDEBAR_WIDTH = 268
CARD_RADIUS = 16
NAV_BUTTON_HEIGHT = 48
