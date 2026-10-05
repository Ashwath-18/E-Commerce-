"""
Table Widget
Reusable QTableWidget wrapper that renders a list of dicts,
given a list of (key, header_label) column definitions.

Visual extras (no change to the data the table receives):
  * status / payment / returned columns are drawn as colored pills
  * an empty state (icon + message) appears when there are no rows
"""

from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QColor, QFontMetrics, QPainter
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QFrame,
    QHeaderView,
    QLabel,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from gui.styles import colors
from gui.widgets.icons import IconBadge


def _badge_kind(key, text):
    """Decide which pill (if any) a cell should be drawn as."""
    value = (text or "").strip().lower()
    if not value:
        return None

    if key == "delivery_status":
        if "delay" in value:
            return "warning"
        if "return" in value or "cancel" in value or "fail" in value:
            return "danger"
        if "deliver" in value and "not" not in value:
            return "success"
        return "info"

    if key == "is_returned":
        return "danger" if value in ("true", "yes", "1") else "neutral"

    if key == "payment_method":
        return "neutral"

    return None


class _CellDelegate(QStyledItemDelegate):
    """Draws status-like columns as rounded pills; others are untouched."""

    def __init__(self, table):
        super().__init__(table)
        self._table = table

    def paint(self, painter, option, index):
        key = self._table.column_key(index.column())
        text = index.data(Qt.DisplayRole)
        kind = _badge_kind(key, str(text) if text is not None else "")

        if kind is None:
            super().paint(painter, option, index)
            return

        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        label = opt.text
        opt.text = ""

        widget = opt.widget
        style = widget.style() if widget else QApplication.style()
        style.drawControl(QStyle.CE_ItemViewItem, opt, painter, widget)

        palette = colors.CURRENT
        dark = colors.is_dark()
        base = {
            "success": palette["SUCCESS"],
            "warning": palette["WARNING"],
            "danger": palette["DANGER"],
            "info": palette["PRIMARY"],
            "neutral": palette["TEXT_LIGHT"],
        }[kind]

        bg = QColor(base)
        bg.setAlpha(58 if dark else 36)
        fg = QColor(base).lighter(118) if dark else QColor(base).darker(125)
        if kind == "neutral":
            fg = QColor(palette["TEXT"]) if not dark else QColor(palette["TEXT_LIGHT"])
            bg = QColor(palette["SOFT"]) if not dark else QColor(palette["SURFACE_ALT"])

        font = opt.font
        font.setPixelSize(11)
        font.setBold(True)
        metrics = QFontMetrics(font)

        pad_x = 12
        max_w = max(opt.rect.width() - 28, 30)
        shown = metrics.elidedText(label, Qt.ElideRight, max_w - pad_x * 2)
        width = min(metrics.horizontalAdvance(shown) + pad_x * 2, max_w)
        height = 24

        pill = QRectF(
            opt.rect.left() + 14,
            opt.rect.center().y() - height / 2 + 0.5,
            width,
            height,
        )

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(bg)
        painter.drawRoundedRect(pill, height / 2, height / 2)
        painter.setPen(fg)
        painter.setFont(font)
        painter.drawText(pill, Qt.AlignCenter, shown)
        painter.restore()


class DataTable(QTableWidget):

    row_selected = Signal(dict)

    def __init__(self, columns, parent=None):
        """
        columns: list of tuples [(data_key, header_label), ...]
        """
        super().__init__(parent)

        self.columns = columns
        self._rows_data = []

        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels([label for _, label in columns])

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setAlternatingRowColors(False)
        self.setFrameShape(QFrame.NoFrame)
        self.setFocusPolicy(Qt.NoFocus)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setMouseTracking(True)
        self.setWordWrap(False)
        self.setTextElideMode(Qt.ElideRight)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.viewport().setAutoFillBackground(False)

        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header.setMinimumHeight(48)
        header.setHighlightSections(False)

        self.verticalHeader().setDefaultSectionSize(50)

        self.setItemDelegate(_CellDelegate(self))
        self.itemSelectionChanged.connect(self._on_selection_changed)

        self._build_empty_state()
        self.set_empty_message()

    # ---------------- Empty state ----------------

    def _build_empty_state(self):
        self._empty = QWidget(self.viewport())
        self._empty.setObjectName("EmptyState")
        self._empty.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        layout = QVBoxLayout(self._empty)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(6)

        badge = IconBadge("empty", 68, "soft", glyph=0.52, radius=0.34)
        layout.addWidget(badge, alignment=Qt.AlignCenter)
        layout.addSpacing(8)

        self._empty_title = QLabel()
        self._empty_title.setObjectName("EmptyTitle")
        self._empty_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._empty_title)

        self._empty_hint = QLabel()
        self._empty_hint.setObjectName("EmptyHint")
        self._empty_hint.setAlignment(Qt.AlignCenter)
        self._empty_hint.setWordWrap(True)
        layout.addWidget(self._empty_hint)

        self._empty.hide()

    def set_empty_message(
        self,
        title="No records found",
        hint="Try a different search, or clear your filters.",
    ):
        """Customize what is shown when the table has no rows."""
        self._empty_title.setText(title)
        self._empty_hint.setText(hint)

    def _update_empty_state(self):
        self._empty.setGeometry(self.viewport().rect())
        self._empty.setVisible(self.rowCount() == 0)
        if self.rowCount() == 0:
            self._empty.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_empty_state()

    # ---------------- Data ----------------

    def column_key(self, column):
        if 0 <= column < len(self.columns):
            return self.columns[column][0]
        return None

    def load_data(self, rows):
        """
        rows: list of dicts
        """
        self._rows_data = rows or []
        self.setRowCount(len(self._rows_data))

        for row_index, row in enumerate(self._rows_data):
            for col_index, (key, _) in enumerate(self.columns):
                value = row.get(key, "")
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.setItem(row_index, col_index, item)

        self._update_empty_state()

    def get_selected_row(self):
        selected_rows = self.selectionModel().selectedRows()
        if not selected_rows:
            return None
        index = selected_rows[0].row()
        if 0 <= index < len(self._rows_data):
            return self._rows_data[index]
        return None

    def sort_data(self, field, descending=False, numeric=False):
        """Sort currently displayed rows without changing the active search."""
        def sort_key(row):
            value = row.get(field)
            if value is None:
                return (1, 0)

            if numeric:
                try:
                    return (0, float(value))
                except (TypeError, ValueError):
                    return (1, 0)

            return (0, str(value).casefold())

        self.load_data(sorted(self._rows_data, key=sort_key, reverse=descending))

    def _on_selection_changed(self):
        row = self.get_selected_row()
        if row is not None:
            self.row_selected.emit(row)
