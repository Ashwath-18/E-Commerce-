"""Dashboard Page with live Cartify database statistics."""

import time

from PySide6.QtCore import QThread, Qt, Signal
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
from database.dashboard_details import get_detail
from gui.widgets import icons
from gui.widgets.interactive_chart import InteractiveAreaChart
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

DETAIL_CACHE_SECONDS = 180

OVERVIEW_SUBTITLE = "Records across every collection · click one to see its graph"

BACK_BUTTON_STYLE = """
QPushButton {
    background-color: rgba(255, 255, 255, 48);
    color: #FFFFFF;
    border: 1px solid rgba(255, 255, 255, 84);
    border-radius: 16px;
    padding: 7px 16px;
    font-size: 12px;
    font-weight: 700;
}
QPushButton:hover {
    background-color: rgba(255, 255, 255, 82);
}
"""


def _short(text, limit=13):
    text = str(text)
    return text if len(text) <= limit else text[: limit - 1] + "…"


class _DetailWorker(QThread):
    """Loads one collection's graph data without freezing the window."""

    loaded = Signal(int, str, dict)

    def __init__(self, request_id, name, parent=None):
        super().__init__(parent)
        self.request_id = request_id
        self.name = name

    def run(self):
        try:
            payload = get_detail(self.name)
        except Exception as exc:
            payload = {"title": self.name, "subtitle": "", "caption": "records",
                       "unit_per": "group", "scale": "zero", "data": [],
                       "note": f"Could not load this graph: {exc}"}
        self.loaded.emit(self.request_id, self.name, payload)


class DashboardPage(QWidget):
    """Show live MongoDB collection counts."""

    page_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # overview / detail state
        self._counts = {}
        self._series = []
        self._selected_index = None
        self._detail_name = None
        self._detail_request = 0
        self._detail_cache = {}
        self._workers = []

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
        refresh_button.clicked.connect(lambda: self.refresh(clear_cache=True))
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
        self.hero_title = QLabel("Overview")
        self.hero_title.setObjectName("HeroTitle")
        self.hero_sub = QLabel(OVERVIEW_SUBTITLE)
        self.hero_sub.setObjectName("HeroSub")
        text.addWidget(self.hero_title)
        text.addWidget(self.hero_sub)
        head.addLayout(text)
        head.addStretch()

        self.back_button = QPushButton("‹  All collections")
        self.back_button.setStyleSheet(BACK_BUTTON_STYLE)
        self.back_button.setCursor(Qt.PointingHandCursor)
        self.back_button.clicked.connect(self._back_to_overview)
        self.back_button.hide()
        head.addWidget(self.back_button, alignment=Qt.AlignTop)
        layout.addLayout(head)

        self.hero_chart = InteractiveAreaChart(
            on_gradient=True, caption="records", min_height=170
        )
        self.hero_chart.point_clicked.connect(self._on_chart_click)
        layout.addWidget(self.hero_chart, stretch=1)

        kpis = QHBoxLayout()
        kpis.setSpacing(14)
        self.kpi_values = {}
        self.kpi_captions = {}
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
            self.kpi_captions[key] = caption

        layout.addLayout(kpis)
        return hero

    # ---------------- Overview <-> single-collection graph ----------------

    def _on_chart_click(self, index):
        if self._detail_name is not None:
            return
        if 0 <= index < len(self._series):
            self._selected_index = index
            self._open_detail(self._series[index][0])

    def _open_detail(self, name):
        self._detail_name = name
        self._detail_request += 1
        request_id = self._detail_request

        self.back_button.show()
        self.hero_title.setText(name)
        self.hero_sub.setText("Loading…")
        self.hero_chart.set_clickable(False)
        self.hero_chart.set_message("Loading…")
        self.hero_chart.set_data([])
        for key, caption in (("Users", "Highest"), ("Total", "Total records"), ("Reviews", "Average")):
            self.kpi_captions[key].setText(caption)
            self.kpi_values[key].setText("—")

        cached = self._detail_cache.get(name)
        if cached and time.time() - cached[0] < DETAIL_CACHE_SECONDS:
            self._apply_detail(name, cached[1])
            return

        worker = _DetailWorker(request_id, name, self)
        worker.loaded.connect(self._on_detail_loaded)
        worker.finished.connect(lambda w=worker: self._worker_done(w))
        self._workers.append(worker)
        worker.start()

    def _worker_done(self, worker):
        if worker in self._workers:
            self._workers.remove(worker)
        worker.deleteLater()

    def _on_detail_loaded(self, request_id, name, payload):
        self._detail_cache[name] = (time.time(), payload)
        # ignore results for a graph the user has already left
        if request_id == self._detail_request and self._detail_name == name:
            self._apply_detail(name, payload)

    def _apply_detail(self, name, payload):
        data = payload.get("data", [])
        self.hero_title.setText(payload.get("title", name))
        self.hero_sub.setText(payload.get("subtitle", ""))

        chart = self.hero_chart
        chart.scale_mode = payload.get("scale", "zero")
        chart.caption = payload.get("caption", "records")
        chart.set_clickable(False)

        if len(data) >= 2:
            chart.set_data(data)
        elif len(data) == 1:
            label, value = data[0]
            chart.set_message(f"Only one group found:  {label} — {value:,}")
            chart.set_data([])
        else:
            chart.set_message(payload.get("note", "No data to show."))
            chart.set_data([])

        if data:
            values = [v for _, v in data]
            peak_label = data[values.index(max(values))][0]
            average = sum(values) / len(values)
            unit = payload.get("unit_per", "group")
            total = self._counts.get(name)

            self.kpi_captions["Users"].setText("Highest")
            self.kpi_values["Users"].setText(_short(peak_label))
            self.kpi_captions["Total"].setText("Total records")
            self.kpi_values["Total"].setText("N/A" if total is None else f"{total:,}")
            self.kpi_captions["Reviews"].setText(f"Average per {unit}")
            self.kpi_values["Reviews"].setText(f"{average:,.0f}" if average >= 100 else f"{average:,.1f}")
        else:
            total = self._counts.get(name)
            self.kpi_values["Total"].setText("N/A" if total is None else f"{total:,}")

    def _back_to_overview(self):
        self._detail_name = None
        self._detail_request += 1  # drop any graph still loading
        self.back_button.hide()
        self.hero_title.setText("Overview")
        self.hero_sub.setText(OVERVIEW_SUBTITLE)
        self.hero_chart.scale_mode = "sqrt"
        self.hero_chart.caption = "records"
        self.hero_chart.set_message("No data")
        self.hero_chart.set_clickable(True)
        for key, caption in (("Users", "Users"), ("Total", "Total records"), ("Reviews", "Reviews")):
            self.kpi_captions[key].setText(caption)
        self._render_overview()

    def _render_overview(self):
        total = sum((v or 0) for v in self._counts.values())
        highlight = self._selected_index
        if highlight is None and total and self._series:
            highlight = max(range(len(self._series)), key=lambda i: self._series[i][1])
        self.hero_chart.set_data(self._series, highlight)

        for key in ("Users", "Reviews"):
            value = self._counts.get(key)
            self.kpi_values[key].setText("N/A" if value is None else f"{value:,}")
        self.kpi_values["Total"].setText(f"{total:,}" if total else "—")

    # ---------------- Data ----------------

    def refresh(self, clear_cache=False):
        """Refresh every displayed count from MongoDB."""
        if clear_cache:
            self._detail_cache.clear()

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

        if clear_cache and self._detail_name is not None:
            self._open_detail(self._detail_name)

        if unavailable:
            show_notification(
                self,
                "Some dashboard data could not be loaded. Check MongoDB.",
                "warning",
            )

    def _update_visuals(self, counts):
        self._counts = counts
        numbers = {name: (value or 0) for name, value in counts.items()}
        total = sum(numbers.values())

        self._series = [(name, numbers[name]) for name, _ in COLLECTIONS]

        if self._detail_name is None:
            self._render_overview()

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
            accent.set_chart(self._series)

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()
