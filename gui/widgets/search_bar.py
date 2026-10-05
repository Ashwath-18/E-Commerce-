"""
Search Bar Widget
A rounded search pill with a leading search icon that emits a signal on
Enter / button click.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton
from PySide6.QtCore import Signal, Qt

from gui.widgets import icons


class SearchBar(QWidget):

    search_triggered = Signal(str)

    def __init__(self, placeholder="Search...", parent=None):
        super().__init__(parent)

        self.setObjectName("SearchBarContainer")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.input = QLineEdit()
        self.input.setObjectName("SearchBar")
        self.input.setPlaceholderText(placeholder)
        self.input.setFixedHeight(46)
        self.input.returnPressed.connect(self._trigger)

        search_action = self.input.addAction(
            icons.icon("search", 18, "muted"), QLineEdit.LeadingPosition
        )
        icons.bind(search_action, "search", 18, "muted")

        self.button = QPushButton("Search")
        self.button.setObjectName("PrimaryButton")
        self.button.setCursor(Qt.PointingHandCursor)
        self.button.setFixedHeight(46)
        self.button.clicked.connect(self._trigger)

        layout.addWidget(self.input, stretch=1)
        layout.addWidget(self.button)

    def _trigger(self):
        self.search_triggered.emit(self.input.text().strip())

    def text(self):
        return self.input.text().strip()

    def clear(self):
        self.input.clear()
