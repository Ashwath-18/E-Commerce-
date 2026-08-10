"""
Analytics Page
Premium dashboard-style analytics layout using live Cartify
collection counts. The layout borrows the reference dashboard's
card rhythm while keeping Cartify's existing theme and data model.
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
from gui.widgets.notification import show_notification


CORE_COLLECTIONS = ["Products", "Users", "Orders", "Reviews"]
SUPPORT_COLLECTIONS = ["Shipping", "Payments", "Inventory", "Sellers"]


class _RingChart(QWidget):
    """Small donut chart for the live collection mix."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.values = []
        self.setMinimumSize(176, 176)

    def set_values(self, values):
        self.values = [max(int(value or 0), 0) for value in values]
        self.update()

    def paintEvent(self, event):
        palette = colors.CURRENT
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect_size = min(self.width(), self.height()) - 34
        rect = QRectF(
            (self.width() - rect_size) / 2,
            (self.height() - rect_size) / 2,
            rect_size,
            rect_size,
        )

        base_pen = QPen(QColor(palette["BORDER"]), 18, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(base_pen)
        painter.drawArc(rect, 0, 360 * 16)

        total = sum(self.values)
        if total:
            segment_colors = [
                QColor(palette["PRIMARY"]),
                QColor(palette["SECONDARY"]),
                QColor(palette["ACCENT"]),
                QColor(palette["SUCCESS"]),
            ]
            start_angle = 90 * 16
            for index, value in enumerate(self.values):
                span = int(-(value / total) * 360 * 16)
                painter.setPen(QPen(segment_colors[index % len(segment_colors)], 18, Qt.SolidLine, Qt.RoundCap))
                painter.drawArc(rect, start_angle, span)
                start_angle += span

        painter.setPen(QColor(palette["TEXT"]))
        painter.setFont(QFont("Segoe UI", 20, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, f"{total:,}")

        painter.setPen(QColor(palette["TEXT_LIGHT"]))
        painter.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
        painter.drawText(self.rect().adjusted(0, 48, 0, 0), Qt.AlignCenter, "records")


class _Sparkline(QWidget):
    """Compact line chart for count distribution across collections."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = []
        self.setMinimumHeight(150)

    def set_data(self, data):
        self.data = list(data or [])
        self.update()

    def paintEvent(self, event):
        palette = colors.CURRENT
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if not self.data:
            painter.setPen(QColor(palette["TEXT_LIGHT"]))
            painter.drawText(self.rect(), Qt.AlignCenter, "No data")
            return

        left, top, right, bottom = 22, 26, 22, 40
        chart_w = max(self.width() - left - right, 1)
        chart_h = max(self.height() - top - bottom, 1)
        max_value = max((value for _, value in self.data), default=1) or 1

        grid_pen = QPen(QColor(palette["BORDER"]), 1)
        painter.setPen(grid_pen)
        for step in range(4):
            y = top + (chart_h / 3) * step
            painter.drawLine(left, int(y), self.width() - right, int(y))

        points = []
        denominator = max(len(self.data) - 1, 1)
        for index, (_, value) in enumerate(self.data):
            x = left + (chart_w / denominator) * index
            y = top + chart_h - ((value / max_value) * chart_h)
            points.append((x, y))

        line_pen = QPen(QColor(palette["PRIMARY"]), 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(line_pen)
        for index in range(len(points) - 1):
            x1, y1 = points[index]
            x2, y2 = points[index + 1]
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        painter.setBrush(QColor(palette["PRIMARY"]))
        painter.setPen(Qt.NoPen)
        for x, y in points:
            painter.drawEllipse(QRectF(x - 4, y - 4, 8, 8))

        painter.setPen(QColor(palette["TEXT_LIGHT"]))
        painter.setFont(QFont("Segoe UI", 9))
        for index, (label, _) in enumerate(self.data):
            x = left + (chart_w / denominator) * index
            painter.drawText(int(x - 36), self.height() - 24, 72, 18, Qt.AlignCenter, label)


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
        outer_layout.addWidget(scroll_area)

        content = QWidget()
        scroll_area.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 8)
        layout.setSpacing(14)

        header_row = QHBoxLayout()

        title_block = QVBoxLayout()
        title_block.setSpacing(4)
        title = QLabel("Analytics")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Live Cartify metrics arranged for quick operational insight.")
        subtitle.setObjectName("PageSubtitle")
        title_block.addWidget(title)
        title_block.addWidget(subtitle)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("SecondaryButton")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setFixedWidth(140)
        refresh_btn.clicked.connect(self.refresh)

        header_row.addLayout(title_block)
        header_row.addStretch()
        header_row.addWidget(refresh_btn, alignment=Qt.AlignTop)
        layout.addLayout(header_row)

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(14)
        grid.setColumnStretch(0, 2)
        grid.setColumnStretch(1, 2)
        grid.setColumnStretch(2, 2)
        grid.setRowStretch(0, 0)
        grid.setRowStretch(1, 0)
        grid.setRowStretch(2, 1)

        self.mix_ring = _RingChart()
        self.mix_labels = {}
        grid.addWidget(self._build_mix_card(), 0, 0, 2, 1)

        self.progress_bars = {}
        grid.addWidget(self._build_progress_card(), 0, 1, 1, 1)

        self.support_labels = {}
        grid.addWidget(self._build_support_card(), 1, 1, 1, 1)

        self.sparkline = _Sparkline()
        self.flow_total = QLabel("0")
        self.flow_total.setObjectName("StatValue")
        grid.addWidget(self._build_flow_card(), 0, 2, 1, 1)

        self.highlight_title = QLabel("Largest Dataset")
        self.highlight_title.setObjectName("ChartTitle")
        self.highlight_value = QLabel("0")
        self.highlight_value.setObjectName("StatValue")
        self.highlight_note = QLabel("Waiting for live data.")
        self.highlight_note.setObjectName("PageSubtitle")
        grid.addWidget(
            self._build_text_card(self.highlight_title, self.highlight_value, self.highlight_note),
            1,
            2,
            1,
            1,
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
            self._build_text_card(self.balance_title, self.balance_value, self.balance_note),
            2,
            2,
            1,
            1,
        )

        layout.addLayout(grid, stretch=1)
        self.refresh()

    def _card(self, title):
        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setObjectName("ChartTitle")
        layout.addWidget(title_label)
        return card, layout

    def _build_mix_card(self):
        card, layout = self._card("Collection Mix")
        layout.addWidget(self.mix_ring, alignment=Qt.AlignCenter)

        for name in CORE_COLLECTIONS:
            row = QHBoxLayout()
            label = QLabel(name)
            label.setObjectName("PanelLabel")
            value = QLabel("0")
            value.setObjectName("NavbarAdmin")
            row.addWidget(label)
            row.addStretch()
            row.addWidget(value)
            layout.addLayout(row)
            self.mix_labels[name] = value

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
            value.setObjectName("NavbarAdmin")
            label_row.addWidget(label)
            label_row.addStretch()
            label_row.addWidget(value)

            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setTextVisible(False)
            bar.setFixedHeight(14)

            layout.addLayout(label_row)
            layout.addWidget(bar)
            self.progress_bars[title] = (bar, value, numerator, denominator)

        layout.addStretch()
        return card

    def _build_support_card(self):
        card, layout = self._card("Support Collections")

        for name in SUPPORT_COLLECTIONS:
            row = QHBoxLayout()
            label = QLabel(name)
            label.setObjectName("PanelLabel")
            value = QLabel("0")
            value.setObjectName("NavbarAdmin")
            row.addWidget(label)
            row.addStretch()
            row.addWidget(value)
            layout.addLayout(row)
            self.support_labels[name] = value

        layout.addStretch()
        return card

    def _build_flow_card(self):
        card, layout = self._card("Cartify Flow")
        layout.addWidget(self.sparkline)

        row = QHBoxLayout()
        row.addWidget(self.flow_total)
        row.addStretch()
        note = QLabel("total core records")
        note.setObjectName("PageSubtitle")
        row.addWidget(note, alignment=Qt.AlignBottom)
        layout.addLayout(row)
        return card

    def _build_text_card(self, title, value, note):
        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(8)
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(value)
        note.setWordWrap(True)
        layout.addWidget(note)
        return card

    def _build_tile_grid(self):
        card, layout = self._card("Core Metrics")

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)

        for index, name in enumerate(CORE_COLLECTIONS):
            tile = QFrame()
            tile.setObjectName("MetricTile")
            tile_layout = QVBoxLayout(tile)
            tile_layout.setContentsMargins(16, 12, 16, 12)
            tile_layout.setSpacing(4)
            tile.setMinimumHeight(92)

            label = QLabel(name)
            label.setObjectName("PanelLabel")
            value = QLabel("0")
            value.setObjectName("TileValue")

            tile_layout.addWidget(label)
            tile_layout.addWidget(value)
            tile_layout.addStretch()

            row, col = divmod(index, 2)
            grid.addWidget(tile, row, col)
            self.stat_tiles[name] = value

        layout.addLayout(grid)
        return card

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
