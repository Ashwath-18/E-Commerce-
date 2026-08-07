"""
AI Assistant Page
Placeholder chat-style UI. There's no AI backend wired into this
project yet — this just gives you a working chat shell to plug a
real model/API into later.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QLineEdit, QPushButton, QFrame
)
from PySide6.QtCore import Qt


class AIAssistantPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        title = QLabel("AI Assistant")
        title.setObjectName("PageTitle")
        subtitle = QLabel(
            "Chat shell only — connect this to an LLM API to make it live."
        )
        subtitle.setObjectName("PageSubtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        chat_card = QFrame()
        chat_card.setObjectName("Card")
        chat_layout = QVBoxLayout(chat_card)
        chat_layout.setContentsMargins(16, 16, 16, 16)

        self.chat_log = QTextEdit()
        self.chat_log.setReadOnly(True)
        self.chat_log.setPlaceholderText("Conversation will appear here...")
        chat_layout.addWidget(self.chat_log, stretch=1)

        input_row = QHBoxLayout()

        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Ask something about your store...")
        self.input_box.returnPressed.connect(self._send)

        send_btn = QPushButton("Send")
        send_btn.setObjectName("PrimaryButton")
        send_btn.setCursor(Qt.PointingHandCursor)
        send_btn.clicked.connect(self._send)

        input_row.addWidget(self.input_box, stretch=1)
        input_row.addWidget(send_btn)

        chat_layout.addLayout(input_row)

        layout.addWidget(chat_card, stretch=1)

    def _send(self):
        message = self.input_box.text().strip()
        if not message:
            return

        self.chat_log.append(f"<b>You:</b> {message}")
        self.chat_log.append(
            "<b>Cartify AI:</b> This assistant isn't connected to a model yet — "
            "wire an API call here to make it respond for real."
        )
        self.input_box.clear()
