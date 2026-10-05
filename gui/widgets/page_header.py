"""
Shared page building blocks
PageHeader  - icon badge + title/subtitle on the left, actions on the right.
FilterBar   - rounded toolbar card that holds search / filter controls.
make_table_card - white card wrapping a DataTable.
"""

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from gui.widgets.icons import IconBadge


class PageHeader(QWidget):

    def __init__(self, title, subtitle, icon="dashboard", parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        self.badge = IconBadge(icon, 54, "violet")
        layout.addWidget(self.badge)

        text_block = QVBoxLayout()
        text_block.setSpacing(2)
        text_block.setContentsMargins(0, 0, 0, 0)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("PageTitle")
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setObjectName("PageSubtitle")
        self.subtitle_label.setWordWrap(True)

        text_block.addWidget(self.title_label)
        text_block.addWidget(self.subtitle_label)
        layout.addLayout(text_block, stretch=1)

        self.actions = QHBoxLayout()
        self.actions.setSpacing(10)
        layout.addLayout(self.actions)

    def add_action(self, widget):
        self.actions.addWidget(widget)


class FilterBar(QFrame):
    """Card-style toolbar. Add controls through `bar.row`."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("FilterBar")
        self.row = QHBoxLayout(self)
        self.row.setContentsMargins(14, 12, 14, 12)
        self.row.setSpacing(10)


def make_table_card(table, margins=(10, 6, 10, 10)):
    card = QFrame()
    card.setObjectName("Card")
    layout = QVBoxLayout(card)
    layout.setContentsMargins(*margins)
    layout.addWidget(table)
    return card


def dialog_header(title, subtitle="", icon="info", tone="violet"):
    """Icon badge + title/subtitle block used at the top of every dialog."""
    wrapper = QWidget()
    layout = QHBoxLayout(wrapper)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(14)

    layout.addWidget(IconBadge(icon, 50, tone))

    text = QVBoxLayout()
    text.setSpacing(2)
    title_label = QLabel(title)
    title_label.setObjectName("DialogTitle")
    text.addWidget(title_label)
    if subtitle:
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("DialogSubtitle")
        subtitle_label.setWordWrap(True)
        text.addWidget(subtitle_label)
    layout.addLayout(text, stretch=1)
    return wrapper
