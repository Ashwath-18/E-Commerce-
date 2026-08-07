"""
Add Product Dialog
Form for creating a new Product document, wired to
crud.create.create_product().
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDoubleSpinBox,
    QSpinBox, QHBoxLayout, QPushButton, QLabel, QMessageBox
)
from PySide6.QtCore import Qt

from crud.create import create_product


class AddProductDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Add Product")
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Add New Product")
        title.setObjectName("PageTitle")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)

        self.product_id_input = QLineEdit()
        self.category_input = QLineEdit()
        self.subcategory_input = QLineEdit()
        self.brand_input = QLineEdit()

        self.price_input = QDoubleSpinBox()
        self.price_input.setMaximum(1_000_000)
        self.price_input.setPrefix("₹ ")

        self.discount_input = QDoubleSpinBox()
        self.discount_input.setMaximum(100)
        self.discount_input.setSuffix(" %")

        self.final_price_input = QDoubleSpinBox()
        self.final_price_input.setMaximum(1_000_000)
        self.final_price_input.setPrefix("₹ ")

        self.stock_input = QSpinBox()
        self.stock_input.setMaximum(1_000_000)

        self.rating_input = QDoubleSpinBox()
        self.rating_input.setMaximum(5)
        self.rating_input.setSingleStep(0.1)

        self.review_count_input = QSpinBox()
        self.review_count_input.setMaximum(1_000_000)

        form.addRow("Product ID *", self.product_id_input)
        form.addRow("Category *", self.category_input)
        form.addRow("Subcategory", self.subcategory_input)
        form.addRow("Brand", self.brand_input)
        form.addRow("Price", self.price_input)
        form.addRow("Discount", self.discount_input)
        form.addRow("Final Price", self.final_price_input)
        form.addRow("Stock", self.stock_input)
        form.addRow("Rating", self.rating_input)
        form.addRow("Review Count", self.review_count_input)

        layout.addLayout(form)

        # ---------------- Buttons ----------------

        button_row = QHBoxLayout()
        button_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("SecondaryButton")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save Product")
        save_btn.setObjectName("PrimaryButton")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self._save)

        button_row.addWidget(cancel_btn)
        button_row.addWidget(save_btn)

        layout.addLayout(button_row)

    def _save(self):
        product_id = self.product_id_input.text().strip()
        category = self.category_input.text().strip()

        if not product_id or not category:
            QMessageBox.warning(
                self, "Missing Fields",
                "Product ID and Category are required."
            )
            return

        try:
            create_product(
                product_id,
                category,
                self.subcategory_input.text().strip(),
                self.brand_input.text().strip(),
                self.price_input.value(),
                self.discount_input.value(),
                self.final_price_input.value(),
                self.stock_input.value(),
                self.rating_input.value(),
                self.review_count_input.value(),
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save product:\n{e}")
