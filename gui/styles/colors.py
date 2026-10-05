"""
Cartify - Centralized Design Tokens (PySide6).

Lavender canvas, a floating violet navigation pill, soft white cards and
violet/pink gradient accents. Every token exists in BOTH palettes and each
theme is tuned on its own (the dark theme is not an inverted light theme):

  * LIGHT - bright lavender canvas, near-white surfaces, soft shadows.
  * DARK  - deep indigo layers, luminous violet accents, brighter borders.

The original keys (BACKGROUND, SIDEBAR, CARD, PRIMARY, SECONDARY, ACCENT,
TEXT, TEXT_LIGHT, BORDER, SIDEBAR_*, HOVER, SUCCESS, WARNING, DANGER) are
kept so existing code that reads `colors.CURRENT[...]` keeps working.
"""

# -----------------------------
# LIGHT THEME
# -----------------------------
LIGHT = {
    # --- original keys ---
    "BACKGROUND": "#EEF0FB",
    "SIDEBAR": "#5E4FC4",
    "CARD": "#FFFFFF",

    "PRIMARY": "#6C5CD6",
    "SECONDARY": "#8777EA",
    "ACCENT": "#4A3DA8",

    "TEXT": "#1C1A3A",
    "TEXT_LIGHT": "#8B8EAB",

    "BORDER": "#E6E8F5",

    "SIDEBAR_TEXT": "#FFFFFF",
    "SIDEBAR_TEXT_MUTED": "#D9D4FF",
    "SIDEBAR_ACTIVE_BG": "#FFFFFF",
    "SIDEBAR_ACTIVE_TEXT": "#FFFFFF",

    "HOVER": "#F0F1FB",

    "SUCCESS": "#27AE6B",
    "WARNING": "#F0A020",
    "DANGER": "#E5484D",

    # --- surfaces ---
    "CANVAS_A": "#D3D8F3",
    "CANVAS_B": "#E9EBFA",
    "SHELL": "#F7F8FE",
    "SHELL_BORDER": "#FFFFFF",
    "CARD_BORDER": "#ECEEF8",
    "CARD_BORDER_HOVER": "#CFC8F5",
    "SURFACE_ALT": "#F4F5FC",

    # --- tinted "soft" surfaces (badges, pills, selection) ---
    "SOFT": "#EFECFD",
    "SOFT_BORDER": "#DDD7F8",
    "SOFT_TEXT": "#5B4BC4",

    # --- gradients ---
    "GRAD_A": "#7A6BDC",
    "GRAD_B": "#5848B8",
    "PINK_A": "#F58BB0",
    "PINK_B": "#EA5C8D",
    "GREEN_A": "#3CC98A",
    "GREEN_B": "#1F9F66",
    "AMBER_A": "#F7B84B",
    "AMBER_B": "#EE8F1E",
    "ICON_G1": "#6C5CD6",
    "ICON_G2": "#E86BA5",

    # --- navigation pill ---
    "SIDEBAR_A": "#7060D4",
    "SIDEBAR_B": "#4C3DA4",
    "SIDEBAR_BORDER": "#8B7DE6",

    # --- inputs & tables ---
    "INPUT_BG": "#F4F5FC",
    "INPUT_BORDER": "#E4E6F4",
    "INPUT_BORDER_HOVER": "#C9C2F2",
    "ROW_LINE": "#F0F1F9",
    "ROW_HOVER": "#F6F5FF",
    "ROW_SELECTED": "#EDE9FD",
    "TRACK": "#E9EAF6",

    # --- shadows (r, g, b, a) ---
    "SHADOW": (84, 70, 170, 34),
    "SHADOW_HERO": (88, 72, 184, 90),
}

# -----------------------------
# DARK THEME
# -----------------------------
DARK = {
    # --- original keys ---
    "BACKGROUND": "#0B0B1C",
    "SIDEBAR": "#3B2E9A",
    "CARD": "#16173A",

    "PRIMARY": "#9C8CFF",
    "SECONDARY": "#7B6AF0",
    "ACCENT": "#D9D2FF",

    "TEXT": "#F3F2FF",
    "TEXT_LIGHT": "#9C9EC9",

    "BORDER": "#272954",

    "SIDEBAR_TEXT": "#FFFFFF",
    "SIDEBAR_TEXT_MUTED": "#C4BDF5",
    "SIDEBAR_ACTIVE_BG": "#FFFFFF",
    "SIDEBAR_ACTIVE_TEXT": "#FFFFFF",

    "HOVER": "#1E2048",

    "SUCCESS": "#35D08A",
    "WARNING": "#F5B83D",
    "DANGER": "#FF6B72",

    # --- surfaces ---
    "CANVAS_A": "#080817",
    "CANVAS_B": "#1A1840",
    "SHELL": "#0F0F26",
    "SHELL_BORDER": "#26285A",
    "CARD_BORDER": "#262853",
    "CARD_BORDER_HOVER": "#4B47A6",
    "SURFACE_ALT": "#1B1C42",

    # --- tinted "soft" surfaces ---
    "SOFT": "#25225A",
    "SOFT_BORDER": "#3E3888",
    "SOFT_TEXT": "#CBC3FF",

    # --- gradients ---
    "GRAD_A": "#6A58E0",
    "GRAD_B": "#35298F",
    "PINK_A": "#F27BB0",
    "PINK_B": "#B63F86",
    "GREEN_A": "#35D08A",
    "GREEN_B": "#14805A",
    "AMBER_A": "#F5B83D",
    "AMBER_B": "#C97812",
    "ICON_G1": "#A99BFF",
    "ICON_G2": "#FF86BC",

    # --- navigation pill ---
    "SIDEBAR_A": "#4A3BB8",
    "SIDEBAR_B": "#221A64",
    "SIDEBAR_BORDER": "#5F52D0",

    # --- inputs & tables ---
    "INPUT_BG": "#0E0F27",
    "INPUT_BORDER": "#2C2E5C",
    "INPUT_BORDER_HOVER": "#4A47A0",
    "ROW_LINE": "#212349",
    "ROW_HOVER": "#1C1E45",
    "ROW_SELECTED": "#2A2570",
    "TRACK": "#262853",

    # --- shadows / glows (r, g, b, a) ---
    "SHADOW": (110, 90, 255, 40),
    "SHADOW_HERO": (110, 90, 255, 110),
}

CURRENT = LIGHT


def get_palette(theme="light"):
    return LIGHT if theme == "light" else DARK


def is_dark():
    return CURRENT is DARK


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
SIDEBAR_WIDTH = 240
SIDEBAR_RAIL_WIDTH = 88
CARD_RADIUS = 22
NAV_BUTTON_HEIGHT = 48
