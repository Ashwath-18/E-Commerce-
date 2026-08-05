import customtkinter as ctk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# -----------------------------
# Colors — light premium palette
# -----------------------------

BACKGROUND = "#F5EFE6"        # Soft cream background
SIDEBAR = "#FBF7F1"           # Near-white sidebar, subtly distinct from bg
CARD = "#FFFFFF"              # Pure white cards

PRIMARY = "#C6A27A"
SECONDARY = "#A67C52"
ACCENT = "#5C4033"            # Deep brown — used for icons/headings

TEXT = "#3E2C23"
TEXT_LIGHT = "#8A7360"

BORDER = "#E6D9C6"            # Subtle border instead of fake shadows

SIDEBAR_TEXT = "#5C4033"
SIDEBAR_TEXT_MUTED = "#9C8672"
SIDEBAR_ACTIVE_BG = "#EFE1CC"   # Soft tan highlight for active nav item
SIDEBAR_ACTIVE_TEXT = "#5C4033"

HOVER = "#F3E7D6"              # Hover background for nav buttons

SUCCESS = "#4CAF50"
WARNING = "#FF9800"
DANGER = "#E53935"

# -----------------------------
# Fonts
# -----------------------------

TITLE_FONT = ("Segoe UI", 26, "bold")
HEADING_FONT = ("Segoe UI", 18, "bold")
SUB_FONT = ("Segoe UI", 13)
BUTTON_FONT = ("Segoe UI", 14, "bold")
TABLE_FONT = ("Segoe UI", 13)
STAT_FONT = ("Segoe UI", 30, "bold")
LABEL_FONT = ("Segoe UI", 12)

# -----------------------------
# Sizes
# -----------------------------

SIDEBAR_WIDTH = 270
ICON_SIZE = (30, 30)
LOGO_SIZE = (55, 55)
CARD_RADIUS = 18
BUTTON_HEIGHT = 50