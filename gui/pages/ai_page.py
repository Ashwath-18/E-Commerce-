"""Production AI shopping assistant page for Cartify."""

from html import escape

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from gui.widgets import icons
from gui.widgets.page_header import PageHeader
from ai.service import ShoppingAssistant


class _AssistantWorker(QThread):
    completed = Signal(dict)
    failed = Signal(str)

    def __init__(self, assistant, message, parent=None):
        super().__init__(parent)
        self.assistant = assistant
        self.message = message

    def run(self):
        try:
            self.completed.emit(self.assistant.ask(self.message))
        except Exception:
            self.failed.emit("Something went wrong while processing that request. Please try again.")


class ProductCard(QFrame):
    def __init__(self, product, parent=None):
        super().__init__(parent)
        self.setObjectName("AIProductCard")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(7)

        title_row = QHBoxLayout()
        title = QLabel(f"{escape(str(product.get('brand') or 'Product'))} · {escape(str(product.get('product_id') or ''))}")
        title.setObjectName("AIProductTitle")
        title_row.addWidget(title, stretch=1)

        price = QLabel(self._money(product.get("final_price")))
        price.setObjectName("AIProductPrice")
        title_row.addWidget(price)
        layout.addLayout(title_row)

        subtitle = QLabel(
            f"{escape(str(product.get('category') or ''))} · {escape(str(product.get('subcategory') or ''))}"
        )
        subtitle.setObjectName("AIProductMeta")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        details = QLabel(
            f"★ {product.get('rating', '—')}  ·  {product.get('review_count', 0)} reviews  ·  "
            f"Stock: {product.get('stock', 0)}  ·  Discount: {product.get('discount', 0)}%"
        )
        details.setObjectName("AIProductMeta")
        details.setWordWrap(True)
        layout.addWidget(details)

        if product.get("seller_id"):
            seller = QLabel(
                f"Seller rating: {product.get('seller_rating', '—')}  ·  "
                f"Seller: {escape(str(product['seller_id']))}"
            )
            seller.setObjectName("AIProductMeta")
            layout.addWidget(seller)

    @staticmethod
    def _money(value):
        try:
            return f"₹{float(value):,.2f}"
        except (TypeError, ValueError):
            return "₹—"


class AIAssistantPage(QWidget):
    """ChatGPT-style UI backed by the real Cartify MongoDB catalog and an optional LLM."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.assistant = ShoppingAssistant()
        self._workers = []

        outer = QVBoxLayout(self)
        outer.setContentsMargins(4, 4, 8, 8)
        outer.setSpacing(16)

        header = PageHeader(
            "AI Shopping Assistant",
            "Ask about products, prices, ratings, stock, and comparisons using the live catalog.",
            "ai",
        )

        clear_btn = QPushButton("New Chat")
        clear_btn.setObjectName("SecondaryButton")
        clear_btn.setCursor(Qt.PointingHandCursor)
        icons.bind(clear_btn, "plus", 18, "muted", "primary")
        clear_btn.clicked.connect(self._clear_chat)
        header.add_action(clear_btn)
        outer.addWidget(header)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(12)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.viewport().setAutoFillBackground(False)

        self.message_container = QWidget()
        self.message_layout = QVBoxLayout(self.message_container)
        self.message_layout.setContentsMargins(8, 8, 8, 8)
        self.message_layout.setSpacing(12)
        self.message_layout.addStretch()
        self.scroll.setWidget(self.message_container)
        card_layout.addWidget(self.scroll, stretch=1)

        self.typing = QLabel("Cartify AI is thinking…")
        self.typing.setObjectName("AITyping")
        self.typing.hide()
        card_layout.addWidget(self.typing)

        input_row = QHBoxLayout()
        input_row.setSpacing(10)
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Try: Show me headphones under ₹5000")
        self.input_box.setObjectName("SearchBar")
        self.input_box.setFixedHeight(46)
        self.input_box.returnPressed.connect(self._send)

        self.send_button = QPushButton()
        self.send_button.setObjectName("SendButton")
        self.send_button.setToolTip("Send")
        self.send_button.setCursor(Qt.PointingHandCursor)
        icons.bind(self.send_button, "send", 20, "white")
        self.send_button.clicked.connect(self._send)

        input_row.addWidget(self.input_box, stretch=1)
        input_row.addWidget(self.send_button)
        card_layout.addLayout(input_row)
        outer.addWidget(card, stretch=1)

        self._add_message(
            "assistant",
            "Hi! I can search the live Cartify catalog, filter by price/rating/category/brand, compare products, and keep track of the products we are discussing.\n\n"
            "The current catalog does not contain detailed specs such as RAM, camera, CPU or battery, so I’ll never invent those details.",
        )

    def _send(self):
        message = self.input_box.text().strip()
        if not message or self._workers:
            return

        self._add_message("user", message)
        self.input_box.clear()
        self.input_box.setEnabled(False)
        self.send_button.setEnabled(False)
        self.typing.show()
        self._scroll_to_bottom()

        worker = _AssistantWorker(self.assistant, message, self)
        worker.completed.connect(self._handle_result)
        worker.failed.connect(self._handle_failure)
        worker.finished.connect(lambda: self._worker_finished(worker))
        self._workers.append(worker)
        worker.start()

    def _worker_finished(self, worker):
        if worker in self._workers:
            self._workers.remove(worker)
        worker.deleteLater()
        self.input_box.setEnabled(True)
        self.send_button.setEnabled(True)
        self.input_box.setFocus()
        self.typing.hide()
        self._scroll_to_bottom()

    def _handle_result(self, result):
        self._add_message("assistant", result.get("message", "I couldn't generate a response."), result.get("products", []))

    def _handle_failure(self, message):
        self._add_message("assistant", message)

    def _add_message(self, role, text, products=None):
        row = QHBoxLayout()
        row.setContentsMargins(4, 0, 4, 0)
        bubble = QFrame()
        bubble.setObjectName("AIUserBubble" if role == "user" else "AIAssistantBubble")
        bubble.setMaximumWidth(860)

        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(18, 14, 18, 14)
        bubble_layout.setSpacing(8)

        label = QLabel("You" if role == "user" else "Cartify AI")
        label.setObjectName("AIMessageRoleUser" if role == "user" else "AIMessageRole")
        bubble_layout.addWidget(label)

        body = QLabel(escape(text).replace("\n", "<br>"))
        body.setObjectName("AIMessageTextUser" if role == "user" else "AIMessageText")
        body.setTextFormat(Qt.RichText)
        body.setWordWrap(True)
        longest = max((self.fontMetrics().horizontalAdvance(line) for line in text.split("\n")), default=0)
        body.setMinimumWidth(min(int(longest * 1.2) + 12, 560))
        bubble_layout.addWidget(body)

        if products:
            product_label = QLabel("Catalog matches")
            product_label.setObjectName("AISectionLabel")
            bubble_layout.addWidget(product_label)
            for product in products[:8]:
                bubble_layout.addWidget(ProductCard(product))

        if role == "user":
            row.addStretch()
            row.addWidget(bubble)
        else:
            row.addWidget(bubble)
            row.addStretch()

        self.message_layout.insertLayout(self.message_layout.count() - 1, row)
        self._scroll_to_bottom()

    def _clear_chat(self):
        if self._workers:
            return
        self.assistant.reset()
        while self.message_layout.count() > 1:
            item = self.message_layout.takeAt(0)
            self._delete_layout_item(item)
        self._add_message("assistant", "New conversation started. What are you looking for?")

    @staticmethod
    def _delete_layout_item(item):
        widget = item.widget()
        child_layout = item.layout()
        if widget:
            widget.deleteLater()
        elif child_layout:
            while child_layout.count():
                AIAssistantPage._delete_layout_item(child_layout.takeAt(0))

    def _scroll_to_bottom(self):
        QApplication.processEvents()
        bar = self.scroll.verticalScrollBar()
        bar.setValue(bar.maximum())