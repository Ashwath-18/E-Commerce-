"""
Analytics Page
Dashboard-style analytics layout using live Cartify collection counts:
a violet "flow" hero curve, a pink highlight card, a donut for the
collection mix, progress bars and metric tiles.
"""

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from config.mongodb import db
from database.dashboard_stats import (
    total_orders,
    total_products,
    total_reviews,
    total_users,
)
from gui.styles import colors
from gui.widgets import icons
from gui.widgets.chart_card import AreaChart
from gui.widgets.notification import show_notification
from gui.widgets.page_header import PageHeader


CORE_COLLECTIONS = ["Products", "Users", "Orders", "Reviews"]
SUPPORT_COLLECTIONS = ["Shipping", "Payments", "Inventory", "Sellers"]

# palette keys used for each core collection (ring + legend dots)
SEGMENT_KEYS = ["PRIMARY", "PINK_B", "AMBER_A", "SUCCESS"]


class _Dot(QWidget):
    """Small legend dot that follows the active theme."""

    def __init__(self, key, parent=None):
        super().__init__(parent)
        self._key = key
        self.setFixedSize(12, 12)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(colors.CURRENT[self._key]))
        painter.drawEllipse(QRectF(1, 1, 10, 10))


class _RingChart(QWidget):
    """Donut chart for the live collection mix."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.values = []
        self.setMinimumSize(190, 190)

    def set_values(self, values):
        self.values = [max(int(value or 0), 0) for value in values]
        self.update()

    def paintEvent(self, event):
        palette = colors.CURRENT
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        thickness = 18
        rect_size = min(self.width(), self.height()) - 36
        rect = QRectF(
            (self.width() - rect_size) / 2,
            (self.height() - rect_size) / 2,
            rect_size,
            rect_size,
        )

        painter.setPen(QPen(QColor(palette["TRACK"]), thickness, Qt.SolidLine, Qt.FlatCap))
        painter.drawArc(rect, 0, 360 * 16)

        total = sum(self.values)
        if total:
            start_angle = 90 * 16
            gap = 4 * 16 if sum(1 for v in self.values if v) > 1 else 0
            for index, value in enumerate(self.values):
                if not value:
                    continue
                span = int(-(value / total) * 360 * 16)
                color = QColor(palette[SEGMENT_KEYS[index % len(SEGMENT_KEYS)]])
                painter.setPen(QPen(color, thickness, Qt.SolidLine, Qt.RoundCap))
                painter.drawArc(rect, start_angle - gap // 2, span + gap)
                start_angle += span

        painter.setPen(QColor(palette["TEXT"]))
        painter.setFont(QFont(colors.FONT_FAMILY, 20, QFont.Bold))
        painter.drawText(self.rect().adjusted(0, -8, 0, 0), Qt.AlignCenter, f"{total:,}")

        painter.setPen(QColor(palette["TEXT_LIGHT"]))
        painter.setFont(QFont(colors.FONT_FAMILY, 10, QFont.DemiBold))
        painter.drawText(self.rect().adjusted(0, 40, 0, 0), Qt.AlignCenter, "records")


class AnalyticsPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

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

        header = PageHeader(
            "Analytics",
            "Live Cartify metrics arranged for quick operational insight.",
            "analytics",
        )
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("SecondaryButton")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        icons.bind(refresh_btn, "refresh", 18, "muted", "primary")
        refresh_btn.clicked.connect(self.refresh)
        header.add_action(refresh_btn)
        layout.addWidget(header)

        grid = QGridLayout()
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(18)
        grid.setColumnStretch(0, 2)
        grid.setColumnStretch(1, 2)
        grid.setColumnStretch(2, 2)

        self.mix_ring = _RingChart()
        self.mix_labels = {}
        grid.addWidget(self._build_mix_card(), 0, 0, 2, 1)

        self.progress_bars = {}
        grid.addWidget(self._build_progress_card(), 0, 1, 1, 1)

        self.support_labels = {}
        grid.addWidget(self._build_support_card(), 1, 1, 1, 1)

        self.sparkline = AreaChart(on_gradient=True, caption="records", min_height=150)
        self.flow_total = QLabel("0")
        self.flow_total.setObjectName("HeroKpiValue")
        grid.addWidget(self._build_flow_card(), 0, 2, 1, 1)

        self.highlight_title = QLabel("Largest Dataset")
        self.highlight_title.setObjectName("AccentTitle")
        self.highlight_value = QLabel("0")
        self.highlight_value.setObjectName("AccentValue")
        self.highlight_note = QLabel("Waiting for live data.")
        self.highlight_note.setObjectName("AccentSub")
        grid.addWidget(
            self._build_text_card(
                self.highlight_title, self.highlight_value, self.highlight_note,
                frame_name="AccentCardPink",
            ),
            1, 2, 1, 1,
        )

        self.stat_tiles = {}
        grid.addWidget(self._build_tile_grid(), 2, 0, 1, 2)

        self.balance_title = QLabel("Data Balance")
        self.balance_title.setObjectName("ChartTitle")
        self.balance_value = QLabel("0%")
        self.balance_value.setObjectName("StatValue")
        self.balance_note = QLabel("Compares reviews against products.")
        self.balance_note.setObjectName("PageSubtitle")
        grid.addWidget(
            self._build_text_card(
                self.balance_title, self.balance_value, self.balance_note
            ),
            2, 2, 1, 1,
        )

        layout.addLayout(grid, stretch=1)
        self.refresh()

    # ---------------- Builders ----------------

    def _card(self, title, subtitle=None):
        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(12)

        title_label = QLabel(title)
        title_label.setObjectName("ChartTitle")
        layout.addWidget(title_label)
        if subtitle:
            sub = QLabel(subtitle)
            sub.setObjectName("ChartSub")
            layout.addWidget(sub)
        return card, layout

    def _value_row(self, text, dot_key=None):
        row = QHBoxLayout()
        row.setSpacing(10)
        if dot_key:
            row.addWidget(_Dot(dot_key))
        label = QLabel(text)
        label.setObjectName("PanelLabel")
        value = QLabel("0")
        value.setObjectName("PanelValue")
        row.addWidget(label)
        row.addStretch()
        row.addWidget(value)
        return row, value

    def _build_mix_card(self):
        card, layout = self._card("Collection Mix", "Core records by collection")
        layout.addWidget(self.mix_ring, alignment=Qt.AlignCenter)

        for index, name in enumerate(CORE_COLLECTIONS):
            row, value = self._value_row(name, SEGMENT_KEYS[index])
            layout.addLayout(row)
            self.mix_labels[name] = value

        layout.addStretch()
        return card

    def _build_progress_card(self):
        card, layout = self._card("Operational Pulse")
        progress_items = [
            ("Order Depth", "Orders", "Products"),
            ("Customer Activity", "Orders", "Users"),
            ("Review Coverage", "Reviews", "Products"),
        ]

        for title, numerator, denominator in progress_items:
            label_row = QHBoxLayout()
            label = QLabel(title)
            label.setObjectName("PanelLabel")
            value = QLabel("0%")
            value.setObjectName("PanelValue")
            label_row.addWidget(label)
            label_row.addStretch()
            label_row.addWidget(value)

            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setTextVisible(False)

            layout.addLayout(label_row)
            layout.addWidget(bar)
            self.progress_bars[title] = (bar, value, numerator, denominator)

        layout.addStretch()
        return card

    def _build_support_card(self):
        card, layout = self._card("Support Collections")

        for name in SUPPORT_COLLECTIONS:
            row, value = self._value_row(name)
            layout.addLayout(row)
            self.support_labels[name] = value

        layout.addStretch()
        return card

    def _build_flow_card(self):
        card = QFrame()
        card.setObjectName("HeroCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(6)

        title = QLabel("Cartify Flow")
        title.setObjectName("HeroTitle")
        sub = QLabel("Core records at a glance")
        sub.setObjectName("HeroSub")
        layout.addWidget(title)
        layout.addWidget(sub)
        layout.addWidget(self.sparkline, stretch=1)

        row = QHBoxLayout()
        row.addWidget(self.flow_total)
        row.addStretch()
        note = QLabel("total core records")
        note.setObjectName("HeroSub")
        row.addWidget(note, alignment=Qt.AlignBottom)
        layout.addLayout(row)
        return card

    def _build_text_card(self, title, value, note, frame_name="Card"):
        card = QFrame()
        card.setObjectName(frame_name)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(6)
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(value)
        note.setWordWrap(True)
        layout.addWidget(note)
        return card

    def _build_tile_grid(self):
        card, layout = self._card("Core Metrics", "Live totals from the database")

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)

        glyphs = {"Products": "products", "Users": "users",
                  "Orders": "orders", "Reviews": "reviews"}

        for index, name in enumerate(CORE_COLLECTIONS):
            tile = QFrame()
            tile.setObjectName("MetricTile")
            tile_layout = QHBoxLayout(tile)
            tile_layout.setContentsMargins(16, 14, 16, 14)
            tile_layout.setSpacing(14)
            tile.setMinimumHeight(92)

            tile_layout.addWidget(icons.IconBadge(glyphs[name], 46, "violet"))

            col = QVBoxLayout()
            col.setSpacing(0)
            label = QLabel(name)
            label.setObjectName("PanelLabel")
            value = QLabel("0")
            value.setObjectName("TileValue")
            col.addStretch()
            col.addWidget(label)
            col.addWidget(value)
            col.addStretch()
            tile_layout.addLayout(col)
            tile_layout.addStretch()

            row, column = divmod(index, 2)
            grid.addWidget(tile, row, column)
            self.stat_tiles[name] = value

        layout.addLayout(grid)
        return card

    # ---------------- Data ----------------

    def refresh(self):
        try:
            core_counts = {
                "Products": total_products(),
                "Users": total_users(),
                "Orders": total_orders(),
                "Reviews": total_reviews(),
            }
            support_counts = {
                name: db[name].count_documents({})
                for name in SUPPORT_COLLECTIONS
            }
        except Exception as e:
            show_notification(self, f"Could not load analytics: {e}", "error")
            return

        self._update_core_counts(core_counts)
        self._update_support_counts(support_counts)
        self._update_progress(core_counts)
        self._update_highlights(core_counts)

    def _update_core_counts(self, counts):
        values = [counts[name] for name in CORE_COLLECTIONS]
        self.mix_ring.set_values(values)
        self.sparkline.set_data([(name, counts[name]) for name in CORE_COLLECTIONS])
        self.flow_total.setText(f"{sum(values):,}")

        for name, value in counts.items():
            formatted = f"{value:,}"
            self.mix_labels[name].setText(formatted)
            self.stat_tiles[name].setText(formatted)

    def _update_support_counts(self, counts):
        for name, value in counts.items():
            self.support_labels[name].setText(f"{value:,}")

    def _update_progress(self, counts):
        for bar, label, numerator_name, denominator_name in self.progress_bars.values():
            numerator = counts.get(numerator_name, 0)
            denominator = counts.get(denominator_name, 0)
            percent = int(min((numerator / denominator) * 100, 100)) if denominator else 0
            bar.setValue(percent)
            label.setText(f"{percent}%")

    def _update_highlights(self, counts):
        largest_name, largest_value = max(counts.items(), key=lambda item: item[1])
        self.highlight_title.setText("Largest Dataset")
        self.highlight_value.setText(f"{largest_value:,}")
        self.highlight_note.setText(f"{largest_name} currently has the highest record count.")

        products = counts.get("Products", 0)
        reviews = counts.get("Reviews", 0)
        coverage = int(min((reviews / products) * 100, 100)) if products else 0
        self.balance_value.setText(f"{coverage}%")
        self.balance_note.setText("Review coverage compared with the live product catalog.")

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()
