"""Cartify AI assistant page: streaming chat backed by the live catalog."""

from html import escape

from PySide6.QtCore import QThread, QTimer, Qt, Signal
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

SUGGESTIONS = [
    "Cheapest headphones",
    "Top rated Electronics",
    "Which brand has the most products?",
    "Delivery status summary",
]


class _AssistantWorker(QThread):
    chunk = Signal(str)
    reset = Signal()
    status = Signal(str)
    completed = Signal(dict)
    failed = Signal(str)

    def __init__(self, assistant, message, parent=None):
        super().__init__(parent)
        self.assistant = assistant
        self.message = message

    def cancel(self):
        self.assistant.cancel()

    def run(self):
        try:
            result = self.assistant.ask(
                self.message,
                on_text=self.chunk.emit,
                on_reset=self.reset.emit,
                on_status=self.status.emit,
            )
            self.completed.emit(result)
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
    """ChatGPT-style assistant: streams answers, renders Markdown, uses live data."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.assistant = ShoppingAssistant()
        self._workers = []
        self._stream = None        # state of the bubble currently being streamed
        self._buffer = ""
        self._render_pending = False

        outer = QVBoxLayout(self)
        outer.setContentsMargins(4, 4, 8, 8)
        outer.setSpacing(16)

        header = PageHeader(
            "AI Shopping Assistant",
            "Ask about products, prices, stock and sales in English, தமிழ் or Tanglish.",
            "ai",
        )

        self.mode_pill = QLabel()
        self.mode_pill.setObjectName("Pill")
        self._refresh_mode_pill()
        header.add_action(self.mode_pill)

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

        self.typing = QLabel("")
        self.typing.setObjectName("AITyping")
        self.typing.hide()
        card_layout.addWidget(self.typing)

        # ---------------- Suggestion chips ----------------

        self.chip_row = QWidget()
        chip_layout = QHBoxLayout(self.chip_row)
        chip_layout.setContentsMargins(0, 0, 0, 0)
        chip_layout.setSpacing(8)
        for text in SUGGESTIONS:
            chip = QPushButton(text)
            chip.setObjectName("AIChip")
            chip.setCursor(Qt.PointingHandCursor)
            chip.clicked.connect(lambda checked=False, t=text: self._send(t))
            chip_layout.addWidget(chip)
        chip_layout.addStretch()
        card_layout.addWidget(self.chip_row)

        # ---------------- Input row ----------------

        input_row = QHBoxLayout()
        input_row.setSpacing(10)
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Ask anything… e.g. cheapest Sony headphones under ₹5000")
        self.input_box.setObjectName("SearchBar")
        self.input_box.setFixedHeight(46)
        self.input_box.returnPressed.connect(self._send)

        self.send_button = QPushButton()
        self.send_button.setObjectName("SendButton")
        self.send_button.setToolTip("Send")
        self.send_button.setCursor(Qt.PointingHandCursor)
        icons.bind(self.send_button, "send", 20, "white")
        self.send_button.clicked.connect(self._send_or_stop)

        input_row.addWidget(self.input_box, stretch=1)
        input_row.addWidget(self.send_button)
        card_layout.addLayout(input_row)
        outer.addWidget(card, stretch=1)

        self._add_welcome()

    # ------------------------------------------------------------------
    # header badge / welcome
    # ------------------------------------------------------------------

    def _refresh_mode_pill(self):
        if self.assistant.ai_enabled:
            self.mode_pill.setText(f"AI · {self.assistant.provider.label}")
            self.mode_pill.setProperty("tone", "green")
            self.mode_pill.setToolTip("Connected to the AI service")
        else:
            self.mode_pill.setText("Basic mode")
            self.mode_pill.setProperty("tone", "amber")
            self.mode_pill.setToolTip("Add AI_API_KEY to your .env file to enable the full AI")
        self.mode_pill.style().unpolish(self.mode_pill)
        self.mode_pill.style().polish(self.mode_pill)

    def _add_welcome(self):
        if self.assistant.ai_enabled:
            text = (
                "Hi! I'm **Cartify AI**. I read your live catalog and orders, so I can:\n\n"
                "- find and **compare products** (price, rating, stock, discounts)\n"
                "- answer **counts and averages** — *which brand has the most products?*\n"
                "- summarise **delivery, returns and payments**\n\n"
                "Ask in English, தமிழ் or Tanglish. I never make up data — everything comes from your database."
            )
        else:
            text = (
                "Hi! I'm **Cartify AI** (basic mode). I can search products, look up IDs, "
                "count and average things, and summarise deliveries.\n\n"
                "To unlock full conversations, add `AI_API_KEY` to your `.env` file."
            )
        self._add_message("assistant", text, copy_button=False)

    # ------------------------------------------------------------------
    # sending / streaming
    # ------------------------------------------------------------------

    def _send_or_stop(self):
        if self._workers:
            self._stop()
        else:
            self._send()

    def _stop(self):
        for worker in self._workers:
            worker.cancel()
        self.typing.setText("Stopping…")

    def _send(self, text=None):
        message = (text if isinstance(text, str) else self.input_box.text()).strip()
        if not message or self._workers:
            return

        self.chip_row.hide()
        self._add_message("user", message)
        self.input_box.clear()
        self.input_box.setEnabled(False)
        self._set_busy(True)
        self.typing.setText("Thinking…")
        self.typing.show()
        self._stream = None
        self._buffer = ""

        worker = _AssistantWorker(self.assistant, message, self)
        worker.chunk.connect(self._on_chunk)
        worker.reset.connect(self._on_reset)
        worker.status.connect(self._on_status)
        worker.completed.connect(self._handle_result)
        worker.failed.connect(self._handle_failure)
        worker.finished.connect(lambda: self._worker_finished(worker))
        self._workers.append(worker)
        worker.start()

    def _set_busy(self, busy):
        if busy:
            icons.rebind(self.send_button, "close")
            self.send_button.setToolTip("Stop generating")
        else:
            icons.rebind(self.send_button, "send")
            self.send_button.setToolTip("Send")

    def _on_status(self, text):
        if self._stream is None:
            self.typing.setText(text)
            self.typing.show()

    def _on_chunk(self, delta):
        if self._stream is None:
            self.typing.hide()
            self._stream = self._create_bubble("assistant")
            self._buffer = ""
        self._buffer += delta
        if not self._render_pending:
            self._render_pending = True
            QTimer.singleShot(45, self._render_stream)

    def _on_reset(self):
        self._buffer = ""
        if self._stream is not None:
            self._stream["body"].setText("")

    def _render_stream(self):
        self._render_pending = False
        if self._stream is not None:
            self._stream["body"].setText(self._buffer)
            self._scroll_to_bottom()

    def _worker_finished(self, worker):
        if worker in self._workers:
            self._workers.remove(worker)
        worker.deleteLater()
        self.input_box.setEnabled(True)
        self._set_busy(False)
        self.input_box.setFocus()
        self.typing.hide()
        self._scroll_to_bottom()

    def _handle_result(self, result):
        text = result.get("message", "I couldn't generate a response.")
        products = result.get("products", [])

        if self._stream is not None:
            self._stream["body"].setText(text)
            self._finish_bubble(self._stream, text, products)
            self._stream = None
        else:
            self._add_message("assistant", text, products)
        self._buffer = ""

    def _handle_failure(self, message):
        if self._stream is not None:
            self._stream = None
        self._add_message("assistant", message, copy_button=False)

    # ------------------------------------------------------------------
    # bubbles
    # ------------------------------------------------------------------

    def _create_bubble(self, role):
        row = QHBoxLayout()
        row.setContentsMargins(4, 0, 4, 0)
        bubble = QFrame()
        bubble.setObjectName("AIUserBubble" if role == "user" else "AIAssistantBubble")
        bubble.setMaximumWidth(860)
        if role != "user":
            bubble.setMinimumWidth(360)

        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(18, 14, 18, 14)
        bubble_layout.setSpacing(8)

        label = QLabel("You" if role == "user" else "Cartify AI")
        label.setObjectName("AIMessageRoleUser" if role == "user" else "AIMessageRole")
        bubble_layout.addWidget(label)

        body = QLabel()
        body.setObjectName("AIMessageTextUser" if role == "user" else "AIMessageText")
        body.setTextFormat(Qt.PlainText if role == "user" else Qt.MarkdownText)
        body.setWordWrap(True)
        body.setTextInteractionFlags(Qt.TextSelectableByMouse)
        bubble_layout.addWidget(body)

        if role == "user":
            row.addStretch()
            row.addWidget(bubble)
        else:
            row.addWidget(bubble)
            row.addStretch()

        self.message_layout.insertLayout(self.message_layout.count() - 1, row)
        self._scroll_to_bottom()
        return {"bubble": bubble, "layout": bubble_layout, "body": body}

    def _finish_bubble(self, state, text, products=None, copy_button=True):
        layout = state["layout"]

        if products:
            product_label = QLabel("Catalog matches")
            product_label.setObjectName("AISectionLabel")
            layout.addWidget(product_label)
            for product in products[:8]:
                layout.addWidget(ProductCard(product))

        if copy_button:
            row = QHBoxLayout()
            row.addStretch()
            copy = QPushButton("Copy")
            copy.setObjectName("AICopy")
            copy.setCursor(Qt.PointingHandCursor)
            copy.clicked.connect(lambda checked=False, b=copy, t=text: self._copy(b, t))
            row.addWidget(copy)
            layout.addLayout(row)

        self._scroll_to_bottom()

    def _copy(self, button, text):
        QApplication.clipboard().setText(text)
        button.setText("Copied ✓")
        QTimer.singleShot(1300, lambda: button.setText("Copy"))

    def _add_message(self, role, text, products=None, copy_button=True):
        state = self._create_bubble(role)
        state["body"].setText(text)

        if role == "user":
            longest = max(
                (self.fontMetrics().horizontalAdvance(line) for line in text.split("\n")), default=0
            )
            state["body"].setMinimumWidth(min(int(longest * 1.2) + 12, 560))
        else:
            self._finish_bubble(state, text, products, copy_button=copy_button)
        return state

    # ------------------------------------------------------------------
    # misc
    # ------------------------------------------------------------------

    def _clear_chat(self):
        if self._workers:
            return
        self.assistant.reset()
        self._stream = None
        while self.message_layout.count() > 1:
            item = self.message_layout.takeAt(0)
            self._delete_layout_item(item)
        self._refresh_mode_pill()
        self.chip_row.show()
        self._add_message("assistant", "New conversation started. What are you looking for?", copy_button=False)

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
        def go():
            bar = self.scroll.verticalScrollBar()
            bar.setValue(bar.maximum())

        QTimer.singleShot(30, go)
