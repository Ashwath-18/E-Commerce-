"""
Settings Dialog
Quick popup to switch between Light and Dark theme.
Emits theme_selected with "light" or "dark".
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QRadioButton, QButtonGroup
)
from PySide6.QtCore import Qt, Signal


class SettingsDialog(QDialog):

    theme_selected = Signal(str)

    def __init__(self, current_theme="light", parent=None):
        super().__init__(parent)

        self.setWindowTitle("Settings")
        self.setMinimumWidth(360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Appearance")
        title.setObjectName("PageTitle")
        layout.addWidget(title)

        subtitle = QLabel("Choose how Cartify looks on your device.")
        subtitle.setObjectName("PageSubtitle")
        layout.addWidget(subtitle)

        self.light_radio = QRadioButton("Light — Cream & Brown")
        self.dark_radio = QRadioButton("Dark")

        self.group = QButtonGroup(self)
        self.group.addButton(self.light_radio)
        self.group.addButton(self.dark_radio)

        if current_theme == "dark":
            self.dark_radio.setChecked(True)
        else:
            self.light_radio.setChecked(True)

        layout.addWidget(self.light_radio)
        layout.addWidget(self.dark_radio)

        button_row = QHBoxLayout()
        button_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("SecondaryButton")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)

        apply_btn = QPushButton("Apply")
        apply_btn.setObjectName("PrimaryButton")
        apply_btn.setCursor(Qt.PointingHandCursor)
        apply_btn.clicked.connect(self._apply)

        button_row.addWidget(cancel_btn)
        button_row.addWidget(apply_btn)

        layout.addLayout(button_row)

    def _apply(self):
        theme = "dark" if self.dark_radio.isChecked() else "light"
        self.theme_selected.emit(theme)
        self.accept()
