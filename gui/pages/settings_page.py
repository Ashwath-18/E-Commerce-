"""
Settings Page
Cartify-specific settings surface with section cards and a
clickable theme toggle.
"""

from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QColor, QLinearGradient, QPainter
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from gui.styles import colors
from gui.widgets.icons import IconBadge
from gui.widgets.notification import show_notification
from gui.widgets.page_header import PageHeader


class _ToggleSwitch(QCheckBox):
    """Pill toggle with a gradient track and a sliding knob."""

    def __init__(self, checked=False, parent=None):
        super().__init__(parent)
        self.setChecked(checked)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(54, 30)

    def paintEvent(self, event):
        palette = colors.CURRENT
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        checked = self.isChecked()
        track = QRectF(1, 2, 52, 26)

        painter.setPen(Qt.NoPen)
        if checked:
            grad = QLinearGradient(track.topLeft(), track.topRight())
            grad.setColorAt(0.0, QColor(palette["GRAD_A"]))
            grad.setColorAt(1.0, QColor(palette["GRAD_B"]))
            painter.setBrush(grad)
        else:
            painter.setBrush(QColor(palette["TRACK"]))
        painter.drawRoundedRect(track, 13, 13)

        knob_x = 29 if checked else 5
        # soft knob shadow
        painter.setBrush(QColor(0, 0, 0, 38))
        painter.drawEllipse(QRectF(knob_x, 6, 20, 20))
        painter.setBrush(QColor("#FFFFFF"))
        painter.drawEllipse(QRectF(knob_x, 5, 20, 20))


class SettingsPage(QWidget):

    theme_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_theme = "light"
        self._syncing_toggle = False

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.viewport().setAutoFillBackground(False)
        outer_layout.addWidget(scroll_area)

        content = QWidget()
        scroll_area.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(4, 4, 8, 20)
        layout.setSpacing(18)

        layout.addWidget(
            PageHeader("Settings", "Customize your Cartify workspace.", "settings")
        )

        self.dark_mode_toggle = self._toggle(self.current_theme == "dark")
        self.dark_mode_toggle.toggled.connect(self._toggle_theme)

        appearance_card = self._section_card(
            "Appearance",
            "sun",
            [
                self._setting_row(
                    "Dark Mode",
                    "Switch between Cartify light and dark themes.",
                    self.dark_mode_toggle,
                ),
                self._static_row(
                    "Brand Accent",
                    "Cartify violet is used across navigation, charts, and actions.",
                    "Violet",
                ),
            ],
        )

        data_card = self._section_card(
            "Data & Workspace",
            "database",
            [
                self._static_row(
                    "Live Database Metrics",
                    "Dashboard and analytics pages read current MongoDB collection counts.",
                    "Enabled",
                    "green",
                ),
                self._static_row(
                    "CRUD Safety",
                    "Deletes continue to use confirmation dialogs before changing records.",
                    "Protected",
                    "green",
                ),
            ],
        )

        admin_card = self._section_card(
            "Admin Session",
            "user",
            [
                self._static_row(
                    "Access Level",
                    "Signed in with the current Cartify administrator session.",
                    "Admin",
                ),
                self._static_row(
                    "Default Theme",
                    "Theme changes apply instantly for this running session.",
                    "Session",
                ),
            ],
        )

        about_card = self._section_card(
            "About Cartify",
            "info",
            [
                self._static_row(
                    "Application",
                    "Smart E-Commerce Management Platform built with PySide6 and MongoDB.",
                    "Cartify",
                ),
            ],
        )

        layout.addWidget(appearance_card)
        layout.addWidget(data_card)
        layout.addWidget(admin_card)
        layout.addWidget(about_card)
        layout.addStretch()

    def _section_card(self, title, glyph, rows):
        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(26, 22, 26, 22)
        card_layout.setSpacing(18)

        head = QHBoxLayout()
        head.setSpacing(12)
        head.addWidget(IconBadge(glyph, 38, "soft", glyph=0.56))
        title_label = QLabel(title)
        title_label.setObjectName("ChartTitle")
        head.addWidget(title_label)
        head.addStretch()
        card_layout.addLayout(head)

        for index, row in enumerate(rows):
            card_layout.addWidget(row)
            if index < len(rows) - 1:
                divider = QFrame()
                divider.setObjectName("SettingsDivider")
                divider.setFixedHeight(1)
                card_layout.addWidget(divider)

        return card

    def _setting_row(self, title, description, control):
        row = QFrame()
        row.setObjectName("SettingsRow")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(18)

        text_block = QVBoxLayout()
        text_block.setSpacing(4)

        title_label = QLabel(title)
        title_label.setObjectName("SettingsItemTitle")
        description_label = QLabel(description)
        description_label.setObjectName("SettingsItemDescription")
        description_label.setWordWrap(True)

        text_block.addWidget(title_label)
        text_block.addWidget(description_label)

        row_layout.addLayout(text_block, stretch=1)
        row_layout.addWidget(control, alignment=Qt.AlignRight | Qt.AlignVCenter)
        return row

    def _static_row(self, title, description, value, tone=None):
        value_label = QLabel(value)
        value_label.setObjectName("SettingsValuePill")
        if tone:
            value_label.setObjectName("Pill")
            value_label.setProperty("tone", tone)
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setMinimumWidth(96)
        return self._setting_row(title, description, value_label)

    def _toggle(self, checked=False):
        toggle = _ToggleSwitch(checked)
        toggle.setObjectName("ToggleSwitch")
        return toggle

    def _toggle_theme(self, checked):
        if self._syncing_toggle:
            return
        theme = "dark" if checked else "light"
        self._apply_theme(theme)

    def _apply_theme(self, theme):
        self.current_theme = theme
        self._syncing_toggle = True
        self.dark_mode_toggle.setChecked(theme == "dark")
        self._syncing_toggle = False
        self.theme_changed.emit(theme)
        show_notification(self, f"{theme.capitalize()} theme applied.", "success")

    def set_theme(self, theme):
        self.current_theme = theme
        self._syncing_toggle = True
        self.dark_mode_toggle.setChecked(theme == "dark")
        self._syncing_toggle = False
