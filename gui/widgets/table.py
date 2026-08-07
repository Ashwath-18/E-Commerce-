"""
Table Widget
Reusable QTableWidget wrapper that renders a list of dicts,
given a list of (key, header_label) column definitions.
"""

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView
from PySide6.QtCore import Qt, Signal


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
        self.verticalHeader().setVisible(False)
        self.setShowGrid(True)

        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.itemSelectionChanged.connect(self._on_selection_changed)

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
                self.setItem(row_index, col_index, item)

    def get_selected_row(self):
        selected_rows = self.selectionModel().selectedRows()
        if not selected_rows:
            return None
        index = selected_rows[0].row()
        if 0 <= index < len(self._rows_data):
            return self._rows_data[index]
        return None

    def _on_selection_changed(self):
        row = self.get_selected_row()
        if row is not None:
            self.row_selected.emit(row)
