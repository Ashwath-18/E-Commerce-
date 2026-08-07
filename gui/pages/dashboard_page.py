"""
Dashboard Page
Welcome Panel Only
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFrame,
    QLabel,
)

from PySide6.QtCore import Qt


class DashboardPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # ---------------- Welcome Panel ----------------

        hero = QFrame()
        hero.setObjectName("Card")

        hero_layout = QVBoxLayout(hero)
        hero_layout.setAlignment(Qt.AlignCenter)
        hero_layout.setSpacing(12)

        hero_layout.addStretch()

        welcome_title = QLabel("Welcome to E-Com Admin")
        welcome_title.setObjectName("PageTitle")
        welcome_title.setAlignment(Qt.AlignCenter)

        welcome_subtitle = QLabel(
            "Smart E-Commerce Management Dashboard"
        )
        welcome_subtitle.setObjectName("PageSubtitle")
        welcome_subtitle.setAlignment(Qt.AlignCenter)

        hero_layout.addWidget(welcome_title)
        hero_layout.addWidget(welcome_subtitle)

        hero_layout.addStretch()

        layout.addWidget(hero)

    def refresh(self):
        pass

    def showEvent(self, event):
        super().showEvent(event)