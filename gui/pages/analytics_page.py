"""Separate chart-driven business reports for Cartify analytics."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QStackedWidget, QVBoxLayout, QWidget,
)

from database.analytics_service import AnalyticsService
from gui.widgets.report_charts import (
    ChartPanel, DonutChart, HorizontalBarChart, RatingGauge, VerticalBarChart,
)


REPORTS = [
    ("sales", "Sales Report", "Track sales performance, order value, and fulfilment results."),
    ("inventory", "Inventory Report", "Monitor product availability and stock health."),
    ("customer", "Customer Report", "Understand customer activity and purchasing behaviour."),
    ("seller", "Seller Report", "Compare seller performance and ratings."),
    ("review", "Review Report", "Summarize category ratings and customer feedback quality."),
    ("payment", "Payment Report", "Review how customers choose to pay for orders."),
]


class ReportKpiCard(QFrame):
    def __init__(self, title, value, parent=None):
        super().__init__(parent)
        self.setObjectName("ReportKpiCard")
        self.setMinimumHeight(118)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(7)
        label = QLabel(title.upper())
        label.setObjectName("ReportKpiLabel")
        number = QLabel(str(value))
        number.setObjectName("ReportKpiValue")
        number.setWordWrap(True)
        layout.addWidget(label)
        layout.addWidget(number)
        layout.addStretch()


class AnalyticsPage(QWidget):
    """A report chooser with isolated, refreshable report pages."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.service = AnalyticsService()
        self.report_pages = {}
        self.report_layouts = {}
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        self.stack = QStackedWidget()
        root.addWidget(self.stack)

        self.hub_page = self._create_hub_page()
        self.stack.addWidget(self.hub_page)
        for report in REPORTS:
            page = self._create_report_page(report)
            self.report_pages[report[0]] = page
            self.stack.addWidget(page)

    def _create_hub_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        title = QLabel("Analytics Reports")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Choose a report to view its live database metrics and charts.")
        subtitle.setObjectName("PageSubtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        selector_row = QHBoxLayout()
        selector_label = QLabel("Report Section")
        selector_label.setObjectName("PanelLabel")
        self.report_picker = QComboBox()
        self.report_picker.setMinimumWidth(270)
        self.report_picker.addItem("Choose a report…", None)
        for key, title_text, _ in REPORTS:
            self.report_picker.addItem(title_text, key)
        open_button = QPushButton("Open Report")
        open_button.setObjectName("PrimaryButton")
        open_button.setCursor(Qt.PointingHandCursor)
        open_button.clicked.connect(self._open_selected_report)
        selector_row.addWidget(selector_label)
        selector_row.addWidget(self.report_picker)
        selector_row.addWidget(open_button)
        selector_row.addStretch()
        layout.addLayout(selector_row)

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(16)
        for index, report in enumerate(REPORTS):
            grid.addWidget(self._create_report_card(report), index // 2, index % 2)
        layout.addLayout(grid)
        layout.addStretch()
        return page

    def _create_report_card(self, report):
        key, title_text, description = report
        card = QFrame()
        card.setObjectName("Card")
        card.setMinimumHeight(150)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 20)
        title = QLabel(title_text)
        title.setObjectName("ChartTitle")
        text = QLabel(description)
        text.setObjectName("PageSubtitle")
        text.setWordWrap(True)
        button = QPushButton("View Report")
        button.setObjectName("SecondaryButton")
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(lambda checked=False, report_key=key: self.open_report(report_key))
        layout.addWidget(title)
        layout.addWidget(text)
        layout.addStretch()
        layout.addWidget(button, alignment=Qt.AlignLeft)
        return card

    def _create_report_page(self, report):
        key, title_text, description = report
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title_block = QVBoxLayout()
        title = QLabel(title_text)
        title.setObjectName("PageTitle")
        subtitle = QLabel(description)
        subtitle.setObjectName("PageSubtitle")
        title_block.addWidget(title)
        title_block.addWidget(subtitle)
        refresh_button = QPushButton("Refresh Report")
        refresh_button.setObjectName("SecondaryButton")
        refresh_button.setCursor(Qt.PointingHandCursor)
        refresh_button.clicked.connect(lambda checked=False, report_key=key: self.refresh_report(report_key))
        back_button = QPushButton("← All Reports")
        back_button.setObjectName("SecondaryButton")
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.clicked.connect(self.show_report_hub)
        header.addLayout(title_block)
        header.addStretch()
        header.addWidget(refresh_button)
        header.addWidget(back_button)
        layout.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)
        scroll.setWidget(content)
        layout.addWidget(scroll)
        self.report_layouts[key] = content_layout
        return page

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    @staticmethod
    def _currency(value):
        return f"₹{value:,.2f}"

    @staticmethod
    def _kpi_row(*cards):
        row = QHBoxLayout()
        row.setSpacing(16)
        for card in cards:
            row.addWidget(card)
        return row

    def _add_error(self, layout, error):
        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        label = QLabel(f"Could not load this report: {error}")
        label.setObjectName("PageSubtitle")
        label.setWordWrap(True)
        card_layout.addWidget(label)
        layout.addWidget(card)

    def refresh_report(self, key):
        layout = self.report_layouts[key]
        self._clear_layout(layout)
        try:
            getattr(self, f"_build_{key}_report")(layout)
        except Exception as error:
            self._add_error(layout, error)
        layout.addStretch()

    def _build_sales_report(self, layout):
        data = self.service.get_sales_report()
        layout.addLayout(self._kpi_row(
            ReportKpiCard("Total Orders", f"{data['total_orders']:,}"),
            ReportKpiCard("Total Revenue", self._currency(data["total_revenue"])),
            ReportKpiCard("Average Order Value", self._currency(data["average_order_value"])),
            ReportKpiCard("Top Selling Category", data["top_category"]),
        ))
        charts = QHBoxLayout()
        charts.setSpacing(16)
        charts.addWidget(ChartPanel("Top Selling Categories", HorizontalBarChart(data["categories"])))
        charts.addWidget(ChartPanel("Returned vs Delivered Orders", DonutChart(data["status"])))
        layout.addLayout(charts)

    def _build_inventory_report(self, layout):
        data = self.service.get_inventory_report()
        layout.addLayout(self._kpi_row(
            ReportKpiCard("Products", f"{data['products']:,}"),
            ReportKpiCard("Out of Stock", f"{data['out_of_stock']:,}"),
            ReportKpiCard("Low Stock", f"{data['low_stock']:,}"),
            ReportKpiCard("Average Stock", f"{data['average_stock']:.1f}"),
        ))
        inventory_colors = ["#DC2626", "#F59E0B", "#16A34A"]  # out, low, healthy
        layout.addWidget(ChartPanel(
            "Inventory Status Overview",
            DonutChart(data["status"], chart_colors=inventory_colors),
        ))

    def _build_customer_report(self, layout):
        data = self.service.get_customer_report()
        layout.addLayout(self._kpi_row(
            ReportKpiCard("Total Users", f"{data['total_users']:,}"),
            ReportKpiCard("Most Active User", data["most_active_user"]),
            ReportKpiCard("Top Buyer", data["top_buyer"]),
        ))
        charts = QHBoxLayout()
        charts.setSpacing(16)
        charts.addWidget(ChartPanel("Most Active Users by Orders", HorizontalBarChart(data["activity"])))
        charts.addWidget(ChartPanel("Top Buyers by Spend", HorizontalBarChart(data["buyers"], currency=True)))
        layout.addLayout(charts)

    def _build_seller_report(self, layout):
        data = self.service.get_seller_report()
        layout.addLayout(self._kpi_row(ReportKpiCard("Average Seller Rating", f"{data['average_rating']:.2f} / 5")))
        charts = QHBoxLayout()
        charts.setSpacing(16)
        charts.addWidget(ChartPanel("Random Sellers", HorizontalBarChart(data["sellers"])))
        charts.addWidget(ChartPanel("Seller Rating Comparison", VerticalBarChart(data["sellers"], max_value=5)))
        layout.addLayout(charts)

    def _build_review_report(self, layout):
        data = self.service.get_review_report()
        highest_product = data["highest"][0][0] if data["highest"] else "N/A"
        lowest_product = data["lowest"][0][0] if data["lowest"] else "N/A"
        layout.addLayout(self._kpi_row(
            ReportKpiCard("Highest Rated Category", highest_product),
            ReportKpiCard("Lowest Rated Category", lowest_product),
            ReportKpiCard("Average Rating", f"{data['average_rating']:.2f} / 5"),
        ))
        charts = QHBoxLayout()
        charts.setSpacing(16)
        charts.addWidget(ChartPanel("Highest Rated Categories", HorizontalBarChart(data["highest"])))
        charts.addWidget(ChartPanel("Lowest Rated Categories", HorizontalBarChart(data["lowest"])))
        layout.addLayout(charts)
        layout.addWidget(ChartPanel("Average Rating", RatingGauge(data["average_rating"])))

    def _build_payment_report(self, layout):
        data = self.service.get_payment_report()
        layout.addLayout(self._kpi_row(*[ReportKpiCard(name, f"{value:,}") for name, value in data]))
        layout.addWidget(ChartPanel("Payment Method Distribution", DonutChart(data)))

    def _open_selected_report(self):
        key = self.report_picker.currentData()
        if key:
            self.open_report(key)

    def open_report(self, key):
        self.refresh_report(key)
        self.stack.setCurrentWidget(self.report_pages[key])

    def show_report_hub(self):
        self.report_picker.setCurrentIndex(0)
        self.stack.setCurrentWidget(self.hub_page)
