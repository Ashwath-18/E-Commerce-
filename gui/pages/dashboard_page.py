"""Dashboard Page with live Cartify database statistics."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config.mongodb import db
from gui.widgets.notification import show_notification
from gui.widgets.stat_card import StatCard


COLLECTIONS = [
    ("Products", "P"),
    ("Users", "U"),
    ("Orders", "O"),
    ("Reviews", "R"),
    ("Shipping", "S"),
    ("Payments", "$"),
    ("Inventory", "I"),
    ("Sellers", "V"),
]


class DashboardPage(QWidget):
    """Show live MongoDB collection counts."""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        header_row = QHBoxLayout()

        title_block = QVBoxLayout()
        title = QLabel("Dashboard")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Live overview of your Cartify database.")
        subtitle.setObjectName("PageSubtitle")
        title_block.addWidget(title)
        title_block.addWidget(subtitle)

        header_row.addLayout(title_block)
        header_row.addStretch()

        refresh_button = QPushButton("Refresh Data")
        refresh_button.setObjectName("SecondaryButton")
        refresh_button.setCursor(Qt.PointingHandCursor)
        refresh_button.clicked.connect(self.refresh)
        header_row.addWidget(refresh_button)

        layout.addLayout(header_row)

        self.cards = {}
        stats_grid = QGridLayout()
        stats_grid.setHorizontalSpacing(16)
        stats_grid.setVerticalSpacing(16)

        for index, (collection_name, icon_text) in enumerate(COLLECTIONS):
            card = StatCard(icon_text, collection_name, "—")
            stats_grid.addWidget(card, index // 4, index % 4)
            self.cards[collection_name] = card

        layout.addLayout(stats_grid)
        layout.addStretch()

        self.refresh()

    def refresh(self):
        """Refresh every displayed count from MongoDB."""
        unavailable = False

        for collection_name, card in self.cards.items():
            try:
                card.set_value(f"{db[collection_name].count_documents({}):,}")
            except Exception:
                card.set_value("N/A")
                unavailable = True

        if unavailable:
            show_notification(
                self,
                "Some dashboard data could not be loaded. Check MongoDB.",
                "warning",
            )

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()
