"""
Settings Page
Cartify-specific settings surface with section cards and a
clickable theme toggle.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter
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
from gui.widgets.notification import show_notification


class _ToggleSwitch(QCheckBox):
    """Small pill toggle with a visible sliding knob."""

    def __init__(self, checked=False, parent=None):
        super().__init__(parent)
        self.setChecked(checked)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(48, 26)

    def paintEvent(self, event):
        palette = colors.CURRENT
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        checked = self.isChecked()
        track_color = palette["PRIMARY"] if checked else palette["BORDER"]
        knob_color = "#FFFFFF" if checked else palette["TEXT_LIGHT"]

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(track_color))
        painter.drawRoundedRect(0, 2, 48, 22, 11, 11)

        knob_x = 25 if checked else 3
        painter.setBrush(QColor(knob_color))
        painter.drawEllipse(knob_x, 4, 18, 18)


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
        outer_layout.addWidget(scroll_area)

        content = QWidget()
        scroll_area.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 8)
        layout.setSpacing(16)

        title = QLabel("Settings")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Customize your Cartify workspace.")
        subtitle.setObjectName("PageSubtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        self.dark_mode_toggle = self._toggle(self.current_theme == "dark")
        self.dark_mode_toggle.toggled.connect(self._toggle_theme)

        appearance_card = self._section_card(
            "Appearance",
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
            [
                self._static_row(
                    "Live Database Metrics",
                    "Dashboard and analytics pages read current MongoDB collection counts.",
                    "Enabled",
                ),
                self._static_row(
                    "CRUD Safety",
                    "Deletes continue to use confirmation dialogs before changing records.",
                    "Protected",
                ),
            ],
        )

        admin_card = self._section_card(
            "Admin Session",
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

    def _section_card(self, title, rows):
        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 22, 24, 22)
        card_layout.setSpacing(18)

        title_label = QLabel(title)
        title_label.setObjectName("ChartTitle")
        card_layout.addWidget(title_label)

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

    def _static_row(self, title, description, value):
        value_label = QLabel(value)
        value_label.setObjectName("SettingsValuePill")
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setMinimumWidth(92)
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
