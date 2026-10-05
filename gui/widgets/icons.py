"""
Cartify icon family.

Every glyph is an original, hand-built vector drawn on a shared 24 x 24 grid:

  * one rounded stroke weight (1.8) with round caps and joins
  * a soft translucent fill on the main shape for subtle depth ("duotone")
  * optional violet -> pink gradient stroke for the premium accent treatment

Icons are rendered with Qt's SVG renderer and tinted from the active
palette, so they stay crisp at any DPI and re-tint instantly when the theme
changes. No image files are required.

Public helpers
--------------
pixmap(name, size, tone)        -> QPixmap
icon(name, size, tone)          -> QIcon
nav_icon(name, size)            -> QIcon (idle / hover / checked states)
bind(target, name, ...)         -> set an icon now and keep it in sync with
                                   the theme (QPushButton, QToolButton,
                                   QAction, QLabel)
refresh_all()                   -> called by gui.styles.apply_theme()
IconBadge                       -> rounded gradient tile with a glyph
logo_pixmap(asset_path, ...)    -> cropped brand logo
"""

import os
import weakref
from functools import lru_cache

from PySide6.QtCore import QByteArray, QRectF, QSize, Qt
from PySide6.QtGui import (
    QColor,
    QIcon,
    QImage,
    QLinearGradient,
    QPainter,
    QPixmap,
)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QLabel, QWidget

from gui.styles import colors


# ---------------------------------------------------------------------------
# Geometry helpers (SVG path data)
# ---------------------------------------------------------------------------

def _c(cx, cy, r):
    """Circle as path data."""
    return (
        f"M{cx - r} {cy}a{r} {r} 0 1 0 {2 * r} 0"
        f"a{r} {r} 0 1 0 {-2 * r} 0Z"
    )


def _rr(x, y, w, h, r):
    """Rounded rectangle as path data."""
    return (
        f"M{x + r} {y}H{x + w - r}a{r} {r} 0 0 1 {r} {r}"
        f"V{y + h - r}a{r} {r} 0 0 1 {-r} {r}"
        f"H{x + r}a{r} {r} 0 0 1 {-r} {-r}"
        f"V{y + r}a{r} {r} 0 0 1 {r} {-r}Z"
    )


# Each glyph: (soft_shapes, line_shapes)
#   soft shapes -> translucent fill + stroke
#   line shapes -> stroke only
_STAR = "M12 3.6l2.6 5.3 5.8.8-4.2 4.1 1 5.8L12 16.8l-5.2 2.8 1-5.8-4.2-4.1 5.8-.8Z"
_SPARKLE = (
    "M11 3.8c.7 4.6 2.6 6.5 7.2 7.2-4.6.7-6.5 2.6-7.2 7.2"
    "-.7-4.6-2.6-6.5-7.2-7.2 4.6-.7 6.5-2.6 7.2-7.2Z"
)
_INBOX = (
    "M3.6 13l2.4-7a2 2 0 0 1 1.9-1.4h8.2a2 2 0 0 1 1.9 1.4l2.4 7v4.5"
    "a2.5 2.5 0 0 1-2.5 2.5H6.1a2.5 2.5 0 0 1-2.5-2.5Z"
)

GLYPHS = {
    # --- navigation -------------------------------------------------------
    "dashboard": (
        [_rr(3.5, 3.5, 7, 10, 2.2), _rr(13.5, 12.5, 7, 8, 2.2)],
        [_rr(13.5, 3.5, 7, 6, 2.2), _rr(3.5, 16.5, 7, 4, 2)],
    ),
    "products": (
        ["M12 3.2 20 7.6 12 12 4 7.6Z"],
        ["M12 3.2 20 7.6V16.4L12 20.8 4 16.4V7.6Z", "M4 7.6 12 12 20 7.6", "M12 12V20.8"],
    ),
    "orders": (
        [_rr(4.5, 8, 15, 12.5, 3.5)],
        ["M8.6 8V7a3.4 3.4 0 0 1 6.8 0V8", "M9.2 14.2l2.1 2.1 3.7-3.9"],
    ),
    "shipping": (
        [_rr(2.5, 6.5, 11, 10, 2.2)],
        ["M13.5 9.5h3.6l3.4 3.4v3.6h-7", _c(7.2, 17.8, 1.9), _c(17, 17.8, 1.9)],
    ),
    "users": (
        [_c(9, 8.2, 3.4)],
        [
            "M3.2 19.6c0-3.4 2.5-5.6 5.8-5.6s5.8 2.2 5.8 5.6",
            _c(17, 9.4, 2.5),
            "M16.4 14.2c2.5.1 4.4 1.9 4.4 5",
        ],
    ),
    "reviews": ([_STAR], []),
    "search": ([_c(10.6, 10.6, 6.4)], ["M15.4 15.4 20.4 20.4"]),
    "ai": (
        [_SPARKLE],
        ["M18.6 3.4v3.6M16.8 5.2h3.6", "M19 16.5v3M17.5 18h3"],
    ),
    "analytics": (
        [_rr(10, 5.5, 4.4, 15, 1.8)],
        [_rr(3.8, 12, 4.4, 8.5, 1.8), _rr(16.2, 9, 4.4, 11.5, 1.8)],
    ),
    "settings": (
        [_c(14.5, 7, 2.3), _c(9.5, 12, 2.3), _c(16.5, 17, 2.3)],
        ["M4 7h8M17 7h3", "M4 12h3M12 12h8", "M4 17h10M19 17h1"],
    ),
    "logout": (
        ["M4.5 7A2.5 2.5 0 0 1 7 4.5h3v15H7A2.5 2.5 0 0 1 4.5 17Z"],
        ["M14.5 8l4 4-4 4", "M18.5 12H9.5"],
    ),
    "database": (
        ["M4.5 6.2C4.5 4.8 7.9 3.6 12 3.6s7.5 1.2 7.5 2.6S16.1 8.8 12 8.8 4.5 7.6 4.5 6.2Z"],
        [
            "M4.5 6.2v11.6c0 1.4 3.4 2.6 7.5 2.6s7.5-1.2 7.5-2.6V6.2",
            "M4.5 12c0 1.4 3.4 2.6 7.5 2.6s7.5-1.2 7.5-2.6",
        ],
    ),
    # --- collections ------------------------------------------------------
    "payments": (
        [_rr(3, 5.5, 18, 13, 3.2)],
        ["M3 10h18", "M7 14.6h3.2"],
    ),
    "inventory": (
        ["M12 3.6 20.6 8 12 12.4 3.4 8Z"],
        ["M3.4 12 12 16.4 20.6 12", "M3.4 16 12 20.4 20.6 16"],
    ),
    "sellers": (
        ["M3.6 9 5.2 4.6H18.8L20.4 9Z"],
        [
            "M3.6 9a2.8 2.8 0 0 0 5.6 0a2.8 2.8 0 0 0 5.6 0a2.8 2.8 0 0 0 5.6 0",
            "M5.2 11.8V18a2 2 0 0 0 2 2h9.6a2 2 0 0 0 2-2v-6.2",
            "M10 20v-4.2a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1V20",
        ],
    ),
    # --- actions ----------------------------------------------------------
    "plus": ([], ["M12 5v14M5 12h14"]),
    "refresh": ([], ["M19.5 12a7.5 7.5 0 1 1-2.2-5.3", "M19.6 4.6v4.2h-4.2"]),
    "edit": (
        ["M4 20l1-4.2L16.2 4.6a2 2 0 0 1 2.8 0l.4.4a2 2 0 0 1 0 2.8L8.2 19 4 20Z"],
        ["M14.5 6.4l3.1 3.1"],
    ),
    "trash": (
        ["M6.3 7l.8 11.5a2 2 0 0 0 2 1.9h5.8a2 2 0 0 0 2-1.9L17.7 7"],
        [
            "M4.5 7h15",
            "M9.5 7V5.2a1.2 1.2 0 0 1 1.2-1.2h2.6a1.2 1.2 0 0 1 1.2 1.2V7",
            "M10.2 11v5M13.8 11v5",
        ],
    ),
    "calendar": (
        [_rr(3.5, 5, 17, 15.5, 3.2)],
        ["M3.5 10h17", "M8 3.2v3.6M16 3.2v3.6"],
    ),
    "send": (
        ["M20.4 3.8 3.6 10.6l6.6 2.6 2.6 6.6Z"],
        ["M20.4 3.8 10.2 13.2"],
    ),
    "sort": (
        [],
        [
            "M8 4.5v15", "M4.8 7.7 8 4.5l3.2 3.2",
            "M16 19.5v-15", "M12.8 16.3l3.2 3.2 3.2-3.2",
        ],
    ),
    "filter": (["M4 5.5h16l-6.2 7.3V19l-3.6-1.8v-4.4Z"], []),
    "check": ([], ["M5 12.6l4.4 4.4L19 7.4"]),
    "close": ([], ["M6 6l12 12M18 6 6 18"]),
    "trend": ([], ["M3.5 16.5l5.2-5.4 3.8 3.4 7.8-8", "M15.2 6.5h5.1v5.1"]),
    "info": ([_c(12, 12, 8.5)], ["M12 11v5", "M12 7.9h.01"]),
    "alert": (
        ["M12 4.2 21 19.5H3Z"],
        ["M12 10v4.2", "M12 16.9h.01"],
    ),
    # --- chevrons / theme -------------------------------------------------
    "chevron_left": ([], ["M14.5 5.5 8 12l6.5 6.5"]),
    "chevron_right": ([], ["M9.5 5.5 16 12l-6.5 6.5"]),
    "chevron_down": ([], ["M5.5 9.5 12 16l6.5-6.5"]),
    "sun": (
        [_c(12, 12, 4)],
        ["M12 2.8v2.2M12 19v2.2M2.8 12H5M19 12h2.2",
         "M5.5 5.5 7 7M17 17l1.5 1.5M5.5 18.5 7 17M17 7l1.5-1.5"],
    ),
    "moon": (["M20 14.2A8.2 8.2 0 0 1 9.8 4a8.2 8.2 0 1 0 10.2 10.2Z"], []),
    # --- misc -------------------------------------------------------------
    "user": (
        [_c(12, 8, 3.8)],
        ["M4.5 20c0-4 3.3-6.4 7.5-6.4s7.5 2.4 7.5 6.4"],
    ),
    "lock": (
        [_rr(5, 10.5, 14, 9.5, 3)],
        ["M8.5 10.5V8a3.5 3.5 0 0 1 7 0v2.5", "M12 14.6v1.9"],
    ),
    "eye": (
        [_c(12, 12, 2.8)],
        ["M2.8 12S6 5.8 12 5.8 21.2 12 21.2 12 18 18.2 12 18.2 2.8 12 2.8 12Z"],
    ),
    "eye_off": (
        [],
        ["M9.6 6.2A9 9 0 0 1 12 5.8C18 5.8 21.2 12 21.2 12a15 15 0 0 1-2.6 3.4",
         "M6.2 8.3A15.5 15.5 0 0 0 2.8 12S6 18.2 12 18.2a8.6 8.6 0 0 0 3.3-.7",
         "M4 4l16 16"],
    ),
    "empty": ([_INBOX], ["M3.6 13h5l1 2.2h4l1-2.2h5"]),
    "bell": (
        ["M6.5 16.5v-5a5.5 5.5 0 0 1 11 0v5l1.5 1.5H5Z"],
        ["M10 20.5a2 2 0 0 0 4 0"],
    ),
    "cart": (
        ["M7.2 7.3h12.3l-1.8 7.4H8.7Z"],
        ["M3.5 4.5h2.4l2.8 10.2h9.6", _c(9.5, 19, 1.4), _c(16.8, 19, 1.4)],
    ),
}


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def _build_svg(name, stroke, fill, fill_opacity, width, opacity):
    soft, line = GLYPHS.get(name, GLYPHS["info"])

    defs = ""
    if isinstance(stroke, tuple):
        defs = (
            '<defs><linearGradient id="g" gradientUnits="userSpaceOnUse" '
            'x1="3" y1="3" x2="21" y2="21">'
            f'<stop offset="0" stop-color="{stroke[0]}"/>'
            f'<stop offset="1" stop-color="{stroke[1]}"/>'
            "</linearGradient></defs>"
        )
        stroke_paint = "url(#g)"
    else:
        stroke_paint = stroke

    fill_paint = stroke_paint if fill is None else fill

    soft_fill = "".join(
        f'<path d="{d}" fill="{fill_paint}" fill-opacity="{fill_opacity}" stroke="none"/>'
        for d in soft
    )
    strokes = "".join(
        f'<path d="{d}"/>' for d in list(soft) + list(line)
    )

    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
        f"{defs}"
        f'<g opacity="{opacity}">'
        f"{soft_fill}"
        f'<g fill="none" stroke="{stroke_paint}" stroke-width="{width}" '
        f'stroke-linecap="round" stroke-linejoin="round">{strokes}</g>'
        "</g></svg>"
    )


@lru_cache(maxsize=1024)
def _render(name, size, stroke, fill, fill_opacity, width, opacity, dpr):
    svg = _build_svg(name, stroke, fill, fill_opacity, width, opacity)
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))

    px = int(round(size * dpr))
    pixmap = QPixmap(px, px)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.SmoothPixmapTransform)
    renderer.render(painter, QRectF(0, 0, px, px))
    painter.end()

    pixmap.setDevicePixelRatio(dpr)
    return pixmap


def _tone(tone):
    """Resolve a tone name to (stroke, fill, fill_opacity, opacity)."""
    p = colors.CURRENT
    dark = colors.is_dark()

    if tone == "accent":
        return (p["ICON_G1"], p["ICON_G2"]), None, 0.22 if not dark else 0.28, 1.0
    if tone == "primary":
        return p["PRIMARY"], p["PRIMARY"], 0.18, 1.0
    if tone == "text":
        return p["TEXT"], p["PRIMARY"], 0.20, 1.0
    if tone == "muted":
        return p["TEXT_LIGHT"], p["TEXT_LIGHT"], 0.14, 1.0
    if tone == "white":
        return "#FFFFFF", "#FFFFFF", 0.26, 1.0
    if tone == "white_dim":
        return "#FFFFFF", "#FFFFFF", 0.14, 0.74
    if tone == "danger":
        return p["DANGER"], p["DANGER"], 0.18, 1.0
    if tone == "success":
        return p["SUCCESS"], p["SUCCESS"], 0.18, 1.0
    if tone == "warning":
        return p["WARNING"], p["WARNING"], 0.18, 1.0
    return p["TEXT"], p["PRIMARY"], 0.20, 1.0


def pixmap(name, size=24, tone="text", dpr=2.0, width=1.8):
    stroke, fill, fill_opacity, opacity = _tone(tone)
    return _render(name, size, stroke, fill, fill_opacity, width, opacity, dpr)


def icon(name, size=24, tone="text", hover_tone=None):
    ico = QIcon()
    ico.addPixmap(pixmap(name, size, tone), QIcon.Normal, QIcon.Off)
    ico.addPixmap(pixmap(name, size, tone), QIcon.Normal, QIcon.On)
    if hover_tone:
        ico.addPixmap(pixmap(name, size, hover_tone), QIcon.Active, QIcon.Off)
        ico.addPixmap(pixmap(name, size, hover_tone), QIcon.Active, QIcon.On)
    return ico


def nav_icon(name, size=22):
    """Sidebar icon: dim when idle, bright on hover and when checked."""
    ico = QIcon()
    ico.addPixmap(pixmap(name, size, "white_dim"), QIcon.Normal, QIcon.Off)
    ico.addPixmap(pixmap(name, size, "white"), QIcon.Active, QIcon.Off)
    ico.addPixmap(pixmap(name, size, "white"), QIcon.Normal, QIcon.On)
    ico.addPixmap(pixmap(name, size, "white"), QIcon.Active, QIcon.On)
    return ico


# ---------------------------------------------------------------------------
# Theme-aware binding
# ---------------------------------------------------------------------------

_BOUND = []


def _apply(entry, target):
    name, size, tone, hover_tone = (
        entry["name"], entry["size"], entry["tone"], entry["hover_tone"],
    )
    if isinstance(target, QLabel):
        target.setPixmap(pixmap(name, size, tone))
        return

    if tone == "nav":
        target.setIcon(nav_icon(name, size))
    else:
        target.setIcon(icon(name, size, tone, hover_tone))

    if hasattr(target, "setIconSize"):
        target.setIconSize(QSize(size, size))


def bind(target, name, size=20, tone="muted", hover_tone=None):
    """
    Set an icon on a button / action / label and keep it in sync with the
    active theme. Returns the target for chaining.
    """
    entry = {
        "ref": weakref.ref(target),
        "name": name,
        "size": size,
        "tone": tone,
        "hover_tone": hover_tone,
    }
    _BOUND.append(entry)
    _apply(entry, target)
    return target


def rebind(target, name):
    """Change the glyph of an already-bound target."""
    for entry in _BOUND:
        if entry["ref"]() is target:
            entry["name"] = name
            try:
                _apply(entry, target)
            except RuntimeError:
                pass
            return


def refresh_all():
    """Re-render every bound icon (called after a theme change)."""
    _render.cache_clear()

    alive = []
    for entry in _BOUND:
        target = entry["ref"]()
        if target is None:
            continue
        try:
            _apply(entry, target)
            alive.append(entry)
        except RuntimeError:
            # underlying Qt object was deleted
            continue

    _BOUND[:] = alive


# ---------------------------------------------------------------------------
# IconBadge
# ---------------------------------------------------------------------------

_BADGE_GRADIENTS = {
    "violet": ("GRAD_A", "GRAD_B"),
    "pink": ("PINK_A", "PINK_B"),
    "green": ("GREEN_A", "GREEN_B"),
    "amber": ("AMBER_A", "AMBER_B"),
}


class IconBadge(QWidget):
    """Rounded gradient tile holding one glyph (matches the reference badges)."""

    def __init__(self, name, size=48, tone="violet", glyph=0.5, radius=0.32, parent=None):
        super().__init__(parent)
        self._name = name
        self._tone = tone
        self._glyph = glyph
        self._radius = radius
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

    def set_name(self, name):
        self._name = name
        self.update()

    def set_tone(self, tone):
        self._tone = tone
        self.update()

    def paintEvent(self, event):
        p = colors.CURRENT
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        radius = self.width() * self._radius

        glyph_tone = "white"

        if self._tone in _BADGE_GRADIENTS:
            key_a, key_b = _BADGE_GRADIENTS[self._tone]
            grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
            grad.setColorAt(0.0, QColor(p[key_a]))
            grad.setColorAt(1.0, QColor(p[key_b]))
            painter.setPen(Qt.NoPen)
            painter.setBrush(grad)
            painter.drawRoundedRect(rect, radius, radius)

            # soft top-left highlight gives the tile a little depth
            shine = QLinearGradient(rect.topLeft(), rect.bottomLeft())
            shine.setColorAt(0.0, QColor(255, 255, 255, 70))
            shine.setColorAt(0.6, QColor(255, 255, 255, 0))
            painter.setBrush(shine)
            painter.drawRoundedRect(rect, radius, radius)

        elif self._tone == "glass":
            painter.setPen(QColor(255, 255, 255, 80))
            painter.setBrush(QColor(255, 255, 255, 48))
            painter.drawRoundedRect(rect, radius, radius)

        else:  # "soft"
            painter.setPen(QColor(p["SOFT_BORDER"]))
            painter.setBrush(QColor(p["SOFT"]))
            painter.drawRoundedRect(rect, radius, radius)
            glyph_tone = "accent"

        glyph_size = int(self.width() * self._glyph)
        dpr = max(2.0, self.devicePixelRatioF())
        pix = pixmap(self._name, glyph_size, glyph_tone, dpr=dpr)
        x = (self.width() - glyph_size) / 2
        y = (self.height() - glyph_size) / 2
        painter.drawPixmap(int(round(x)), int(round(y)), pix)


# ---------------------------------------------------------------------------
# Brand logo
# ---------------------------------------------------------------------------

_LOGO_CACHE = {}


def _content_rect(image):
    """Bounding box of the visible (non-transparent) logo pixels."""
    sw, sh = 384, 256
    small = image.scaled(sw, sh, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    small = small.convertToFormat(QImage.Format_Alpha8)
    stride = small.bytesPerLine()
    data = bytes(small.constBits())

    rows = [y for y in range(sh) if max(data[y * stride:y * stride + sw]) > 40]
    cols = [x for x in range(sw) if max(data[x::stride][:sh]) > 40]
    if not rows or not cols:
        return QRectF(0, 0, image.width(), image.height())

    fx = image.width() / sw
    fy = image.height() / sh
    pad = 2
    x0 = max((cols[0] - pad) * fx, 0)
    y0 = max((rows[0] - pad) * fy, 0)
    x1 = min((cols[-1] + 1 + pad) * fx, image.width())
    y1 = min((rows[-1] + 1 + pad) * fy, image.height())
    return QRectF(x0, y0, x1 - x0, y1 - y0)


def logo_pixmap(asset_path, variant="light", height=40):
    """
    Return the brand logo cropped to its visible content, scaled to `height`.

    variant="dark"  -> white bag (use on violet / dark surfaces)
    variant="light" -> violet bag (use on light surfaces)
    Returns None when no logo file exists.
    """
    key = (asset_path, variant, height)
    if key in _LOGO_CACHE:
        return _LOGO_CACHE[key]

    names = (
        ["logo_dark.png", "logo_light.png", "logo.png"]
        if variant == "dark"
        else ["logo_light.png", "logo_dark.png", "logo.png"]
    )
    path = next(
        (os.path.join(asset_path, n) for n in names
         if os.path.exists(os.path.join(asset_path, n))),
        None,
    )
    if path is None:
        _LOGO_CACHE[key] = None
        return None

    image = QImage(path)
    if image.isNull():
        _LOGO_CACHE[key] = None
        return None

    rect = _content_rect(image).toRect()
    cropped = image.copy(rect)
    scaled = cropped.scaledToHeight(
        int(height * 2), Qt.SmoothTransformation
    )
    result = QPixmap.fromImage(scaled)
    result.setDevicePixelRatio(2.0)
    _LOGO_CACHE[key] = result
    return result
