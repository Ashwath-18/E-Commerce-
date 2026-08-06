from gui.windows.main_window import CartifyWindow

from PySide6.QtWidgets import QApplication

import sys

app = QApplication(sys.argv)

window = CartifyWindow()

window.show()

sys.exit(app.exec())