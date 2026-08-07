"""
Analytics Page
A simple overview chart comparing collection counts, using the
lightweight ChartCard widget (no external chart library needed).
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

from gui.widgets.chart_card import ChartCard
from gui.widgets.notification import show_notification

from database.dashboard_stats import (
    total_products,
    total_users,
    total_orders,
    total_reviews,
)


class AnalyticsPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        title = QLabel("Analytics")
        title.setObjectName("PageTitle")
        subtitle = QLabel("A quick overview of your store's key metrics.")
        subtitle.setObjectName("PageSubtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        self.chart_card = ChartCard(title="Collection Overview", data=[])
        layout.addWidget(self.chart_card, stretch=1)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("SecondaryButton")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setFixedWidth(140)
        refresh_btn.clicked.connect(self.refresh)
        layout.addWidget(refresh_btn, alignment=Qt.AlignLeft)

        self.refresh()

    def refresh(self):
        try:
            data = [
                ("Products", total_products()),
                ("Users", total_users()),
                ("Orders", total_orders()),
                ("Reviews", total_reviews()),
            ]
            self.chart_card.set_data(data)
        except Exception as e:
            show_notification(self, f"Could not load analytics: {e}", "error")

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()
