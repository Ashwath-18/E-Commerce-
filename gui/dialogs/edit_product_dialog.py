"""
Edit Product Dialog
Pre-filled form to update an existing product's price, stock,
and rating — the only fields the backend (crud/update.py) supports
updating for a Product.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLabel, QDoubleSpinBox,
    QSpinBox, QHBoxLayout, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt

from crud.update import (
    update_product_price,
    update_product_stock,
    update_product_rating,
)


class EditProductDialog(QDialog):

    def __init__(self, product, parent=None):
        """
        product: dict with at least product_id, price, stock, rating
        """
        super().__init__(parent)

        self.product = product

        self.setWindowTitle(f"Edit Product — {product.get('product_id', '')}")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel(f"Edit Product: {product.get('product_id', '')}")
        title.setObjectName("PageTitle")
        layout.addWidget(title)

        info = QLabel(
            f"Brand: {product.get('brand', '—')}   |   "
            f"Category: {product.get('category', '—')}"
        )
        info.setObjectName("PageSubtitle")
        layout.addWidget(info)

        form = QFormLayout()
        form.setSpacing(12)

        self.price_input = QDoubleSpinBox()
        self.price_input.setMaximum(1_000_000)
        self.price_input.setPrefix("₹ ")
        self.price_input.setValue(float(product.get("price", 0) or 0))

        self.stock_input = QSpinBox()
        self.stock_input.setMaximum(1_000_000)
        self.stock_input.setValue(int(product.get("stock", 0) or 0))

        self.rating_input = QDoubleSpinBox()
        self.rating_input.setMaximum(5)
        self.rating_input.setSingleStep(0.1)
        self.rating_input.setValue(float(product.get("rating", 0) or 0))

        form.addRow("Price", self.price_input)
        form.addRow("Stock", self.stock_input)
        form.addRow("Rating", self.rating_input)

        layout.addLayout(form)

        # ---------------- Buttons ----------------

        button_row = QHBoxLayout()
        button_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("SecondaryButton")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save Changes")
        save_btn.setObjectName("PrimaryButton")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self._save)

        button_row.addWidget(cancel_btn)
        button_row.addWidget(save_btn)

        layout.addLayout(button_row)

    def _save(self):
        product_id = self.product.get("product_id")

        try:
            update_product_price(product_id, self.price_input.value())
            update_product_stock(product_id, self.stock_input.value())
            update_product_rating(product_id, self.rating_input.value())
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not update product:\n{e}")
