"""
Settings Page
Theme switcher (light/dark) plus basic app info.
Emits theme_changed("light"|"dark") for main_window to apply.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt, Signal

from gui.dialogs.settings_dialog import SettingsDialog
from gui.widgets.notification import show_notification


class SettingsPage(QWidget):

    theme_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_theme = "light"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        title = QLabel("Settings")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Manage app preferences.")
        subtitle.setObjectName("PageSubtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(14)

        appearance_label = QLabel("Appearance")
        appearance_label.setObjectName("PageSubtitle")

        appearance_row = QHBoxLayout()

        theme_btn = QPushButton("Change Theme")
        theme_btn.setObjectName("PrimaryButton")
        theme_btn.setCursor(Qt.PointingHandCursor)
        theme_btn.setFixedWidth(180)
        theme_btn.clicked.connect(self._open_theme_dialog)

        appearance_row.addWidget(theme_btn)
        appearance_row.addStretch()

        card_layout.addWidget(appearance_label)
        card_layout.addLayout(appearance_row)

        card_layout.addSpacing(10)

        about_label = QLabel("About Cartify")
        about_label.setObjectName("PageSubtitle")

        about_text = QLabel(
            "Cartify — Smart E-Commerce Management Platform\n"
            "Built with PySide6 + MongoDB."
        )

        card_layout.addWidget(about_label)
        card_layout.addWidget(about_text)

        card_layout.addStretch()

        layout.addWidget(card, stretch=1)

    def _open_theme_dialog(self):
        dialog = SettingsDialog(self.current_theme, self)
        dialog.theme_selected.connect(self._apply_theme)
        dialog.exec()

    def _apply_theme(self, theme):
        self.current_theme = theme
        self.theme_changed.emit(theme)
        show_notification(self, f"{theme.capitalize()} theme applied.", "success")
