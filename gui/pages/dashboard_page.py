"""Dashboard Page with live Cartify database statistics."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from config.mongodb import db
from gui.widgets import icons
from gui.widgets.chart_card import AreaChart
from gui.widgets.notification import show_notification
from gui.widgets.page_header import PageHeader
from gui.widgets.stat_card import AccentCard, StatCard


# (collection, icon glyph)
COLLECTIONS = [
    ("Products", "products"),
    ("Users", "users"),
    ("Orders", "orders"),
    ("Reviews", "reviews"),
    ("Shipping", "shipping"),
    ("Payments", "payments"),
    ("Inventory", "inventory"),
    ("Sellers", "sellers"),
]

CARD_PAGES = {
    "Products": "products",
    "Users": "users",
    "Orders": "orders",
    "Reviews": "reviews",
    "Shipping": "shipping",
}


class DashboardPage(QWidget):
    """Show live MongoDB collection counts."""

    page_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.viewport().setAutoFillBackground(False)
        outer.addWidget(scroll)

        content = QWidget()
        scroll.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(4, 4, 8, 20)
        layout.setSpacing(18)

        # ---------------- Header ----------------

        header = PageHeader(
            "Dashboard", "Live overview of your Cartify database.", "dashboard"
        )

        refresh_button = QPushButton("Refresh Data")
        refresh_button.setObjectName("SecondaryButton")
        refresh_button.setCursor(Qt.PointingHandCursor)
        icons.bind(refresh_button, "refresh", 18, "muted", "primary")
        refresh_button.clicked.connect(self.refresh)
        header.add_action(refresh_button)

        layout.addWidget(header)

        # ---------------- Hero + accent column ----------------

        top_row = QHBoxLayout()
        top_row.setSpacing(18)
        top_row.addWidget(self._build_hero(), stretch=3)

        accent_column = QVBoxLayout()
        accent_column.setSpacing(18)

        self.products_accent = AccentCard(
            "Products", "Items in your catalog", "products", "violet"
        )
        self.orders_accent = AccentCard(
            "Orders", "Purchases placed", "orders", "pink"
        )
        for card, page_key, label in (
            (self.products_accent, "products", "Products"),
            (self.orders_accent, "orders", "Orders"),
        ):
            card.set_clickable(True, f"Open {label}")
            card.clicked.connect(lambda page=page_key: self.page_requested.emit(page))
            accent_column.addWidget(card, stretch=1)

        top_row.addLayout(accent_column, stretch=1)
        layout.addLayout(top_row)

        # ---------------- Stat cards ----------------

        self.cards = {}
        stats_grid = QGridLayout()
        stats_grid.setHorizontalSpacing(18)
        stats_grid.setVerticalSpacing(18)

        for index, (collection_name, glyph) in enumerate(COLLECTIONS):
            card = StatCard(glyph, collection_name, "—")
            page_key = CARD_PAGES.get(collection_name)
            if page_key:
                card.set_clickable(True, f"Open {collection_name}")
                card.clicked.connect(
                    lambda page=page_key: self.page_requested.emit(page)
                )
            else:
                card.set_clickable(False)
            stats_grid.addWidget(card, index // 4, index % 4)
            self.cards[collection_name] = card

        for col in range(4):
            stats_grid.setColumnStretch(col, 1)

        layout.addLayout(stats_grid)
        layout.addStretch()

        self.refresh()

    # ---------------- Hero ----------------

    def _build_hero(self):
        hero = QFrame()
        hero.setObjectName("HeroCard")
        hero.setMinimumHeight(330)

        layout = QVBoxLayout(hero)
        layout.setContentsMargins(26, 22, 26, 22)
        layout.setSpacing(8)

        head = QHBoxLayout()
        text = QVBoxLayout()
        text.setSpacing(1)
        title = QLabel("Overview")
        title.setObjectName("HeroTitle")
        sub = QLabel("Records across every collection")
        sub.setObjectName("HeroSub")
        text.addWidget(title)
        text.addWidget(sub)
        head.addLayout(text)
        head.addStretch()
        layout.addLayout(head)

        self.hero_chart = AreaChart(
            on_gradient=True, caption="records", min_height=170
        )
        layout.addWidget(self.hero_chart, stretch=1)

        kpis = QHBoxLayout()
        kpis.setSpacing(14)
        self.kpi_values = {}
        for key, label, strong in (
            ("Users", "Users", False),
            ("Total", "Total records", True),
            ("Reviews", "Reviews", False),
        ):
            tile = QFrame()
            tile.setObjectName("HeroGlassStrong" if strong else "HeroGlass")
            tile_layout = QVBoxLayout(tile)
            tile_layout.setContentsMargins(18, 12, 18, 12)
            tile_layout.setSpacing(0)
            tile_layout.setAlignment(Qt.AlignCenter)

            caption = QLabel(label)
            caption.setObjectName("HeroKpiLabel")
            caption.setAlignment(Qt.AlignCenter)
            value = QLabel("—")
            value.setObjectName("HeroKpiValue")
            value.setAlignment(Qt.AlignCenter)
            tile_layout.addWidget(caption)
            tile_layout.addWidget(value)

            kpis.addWidget(tile, stretch=3 if strong else 2)
            self.kpi_values[key] = value

        layout.addLayout(kpis)
        return hero

    # ---------------- Data ----------------

    def refresh(self):
        """Refresh every displayed count from MongoDB."""
        unavailable = False
        counts = {}

        for collection_name, card in self.cards.items():
            try:
                count = db[collection_name].count_documents({})
                counts[collection_name] = count
                card.set_value(f"{count:,}")
            except Exception:
                counts[collection_name] = None
                card.set_value("N/A")
                unavailable = True

        self._update_visuals(counts)

        if unavailable:
            show_notification(
                self,
                "Some dashboard data could not be loaded. Check MongoDB.",
                "warning",
            )

    def _update_visuals(self, counts):
        numbers = {name: (value or 0) for name, value in counts.items()}
        total = sum(numbers.values())

        series = [(name, numbers[name]) for name, _ in COLLECTIONS]
        highlight = None
        if total:
            highlight = max(range(len(series)), key=lambda i: series[i][1])
        self.hero_chart.set_data(series, highlight)

        for key in ("Users", "Reviews"):
            value = counts.get(key)
            self.kpi_values[key].setText("N/A" if value is None else f"{value:,}")
        self.kpi_values["Total"].setText(f"{total:,}" if total else "—")

        for name, card in self.cards.items():
            if counts.get(name) is None or not total:
                card.set_share(None)
            else:
                card.set_share(counts[name] / total * 100)

        for name, accent in (
            ("Products", self.products_accent),
            ("Orders", self.orders_accent),
        ):
            value = counts.get(name)
            accent.set_value("N/A" if value is None else f"{value:,}")
            accent.set_chart(series)

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()
