"""
DetailPanel
Card that shows grouped key/value details as a grid of tiles
(used by the Search page for product and user overviews).
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout


class DetailPanel(QFrame):

    def __init__(self, columns=4, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self._columns = columns

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(22, 20, 22, 22)
        self._layout.setSpacing(12)

    def clear(self):
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self._delete_layout(item.layout())

    def _delete_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def set_sections(self, sections):
        """sections: list of (section_title, [(label, value), ...])"""
        self.clear()

        for index, (section_title, fields) in enumerate(sections):
            heading = QLabel(section_title)
            heading.setObjectName("DetailSection")
            if index:
                heading.setContentsMargins(0, 8, 0, 0)
            self._layout.addWidget(heading)

            grid = QGridLayout()
            grid.setHorizontalSpacing(12)
            grid.setVerticalSpacing(12)

            for i, (label, value) in enumerate(fields):
                tile = QFrame()
                tile.setObjectName("MetricTile")
                tile_layout = QVBoxLayout(tile)
                tile_layout.setContentsMargins(16, 12, 16, 12)
                tile_layout.setSpacing(3)

                name = QLabel(label)
                name.setObjectName("PanelLabel")
                val = QLabel(str(value))
                val.setObjectName("DetailValue")
                val.setWordWrap(True)
                val.setTextInteractionFlags(Qt.TextSelectableByMouse)

                tile_layout.addWidget(name)
                tile_layout.addWidget(val)

                grid.addWidget(tile, i // self._columns, i % self._columns)

            for c in range(self._columns):
                grid.setColumnStretch(c, 1)

            self._layout.addLayout(grid)
