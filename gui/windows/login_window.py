"""
Login Window
Admin gate before the main app opens: a split card with a violet brand
panel on the left and the sign-in form on the right. Credentials are
hardcoded for now (admin / admin) — swap _check_credentials() for
a real auth check whenever you're ready.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from gui.styles import colors
from gui.widgets import icons

DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin"


class LoginWindow(QWidget):

    login_success = Signal(str)  # emits admin display name

    def __init__(self, asset_path):
        super().__init__()

        self.asset_path = asset_path
        self.setWindowTitle("Cartify — Login")
        self.setFixedSize(1010, 620)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        root = QFrame()
        root.setObjectName("LoginRoot")
        outer.addWidget(root)

        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(30, 30, 30, 30)

        shell = QFrame()
        shell.setObjectName("LoginShell")
        shadow = QGraphicsDropShadowEffect(shell)
        shadow.setBlurRadius(46)
        shadow.setOffset(0, 14)
        shadow.setColor(QColor(*colors.CURRENT["SHADOW_HERO"]))
        shell.setGraphicsEffect(shadow)
        root_layout.addWidget(shell)

        shell_layout = QHBoxLayout(shell)
        shell_layout.setContentsMargins(14, 14, 14, 14)
        shell_layout.setSpacing(0)

        shell_layout.addWidget(self._build_hero())
        shell_layout.addWidget(self._build_form(), stretch=1)

    # ---------------- Brand panel ----------------

    def _build_hero(self):
        hero = QFrame()
        hero.setObjectName("LoginHero")
        hero.setFixedWidth(430)

        layout = QVBoxLayout(hero)
        layout.setContentsMargins(32, 34, 32, 34)
        layout.setSpacing(0)

        brand = QHBoxLayout()
        brand.setSpacing(12)
        logo = QLabel()
        pix = icons.logo_pixmap(self.asset_path, "dark", 44)
        if pix is not None:
            logo.setPixmap(pix)
        brand.addWidget(logo)
        name = QLabel("Cartify")
        name.setObjectName("SidebarTitle")
        brand.addWidget(name)
        brand.addStretch()
        layout.addLayout(brand)

        layout.addStretch(1)

        title = QLabel("Run your store with clarity.")
        title.setObjectName("LoginHeroTitle")
        title.setWordWrap(True)
        layout.addWidget(title)
        layout.addSpacing(10)

        text = QLabel(
            "Products, orders, shipping and an AI shopping assistant "
            "in one calm workspace."
        )
        text.setObjectName("LoginHeroText")
        text.setWordWrap(True)
        layout.addWidget(text)
        layout.addSpacing(26)

        features = [
            ("products", "Catalog", "Stock & prices"),
            ("orders", "Orders", "Dates & status"),
            ("shipping", "Shipping", "Delivery status"),
            ("ai", "AI assistant", "Ask the catalog"),
        ]
        grid = QGridLayout()
        grid.setSpacing(12)
        for i, (glyph, label, note) in enumerate(features):
            chip = QFrame()
            chip.setObjectName("HeroGlass")
            chip_layout = QHBoxLayout(chip)
            chip_layout.setContentsMargins(12, 10, 12, 10)
            chip_layout.setSpacing(10)
            chip_layout.addWidget(icons.IconBadge(glyph, 34, "glass", glyph=0.56))
            col = QVBoxLayout()
            col.setSpacing(0)
            t = QLabel(label)
            t.setObjectName("LoginFeatureTitle")
            n = QLabel(note)
            n.setObjectName("LoginFeatureText")
            col.addWidget(t)
            col.addWidget(n)
            chip_layout.addLayout(col)
            grid.addWidget(chip, i // 2, i % 2)
        layout.addLayout(grid)

        return hero

    # ---------------- Form ----------------

    def _build_form(self):
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(64, 40, 64, 40)
        layout.setSpacing(0)
        layout.addStretch(1)

        badge = icons.IconBadge("lock", 56, "violet")
        layout.addWidget(badge)
        layout.addSpacing(18)

        title = QLabel("Welcome back")
        title.setObjectName("LoginTitle")
        layout.addWidget(title)
        layout.addSpacing(4)

        subtitle = QLabel("Sign in to manage Cartify")
        subtitle.setObjectName("PageSubtitle")
        layout.addWidget(subtitle)
        layout.addSpacing(28)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setText(DEFAULT_USERNAME)
        self.username_input.setFixedHeight(50)
        user_action = self.username_input.addAction(
            icons.icon("user", 18, "muted"), QLineEdit.LeadingPosition
        )
        icons.bind(user_action, "user", 18, "muted")
        self.username_input.returnPressed.connect(
            lambda: self.password_input.setFocus()
        )

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(50)
        self.password_input.returnPressed.connect(self._attempt_login)
        lock_action = self.password_input.addAction(
            icons.icon("lock", 18, "muted"), QLineEdit.LeadingPosition
        )
        icons.bind(lock_action, "lock", 18, "muted")
        self._eye_action = self.password_input.addAction(
            icons.icon("eye", 18, "muted"), QLineEdit.TrailingPosition
        )
        icons.bind(self._eye_action, "eye", 18, "muted")
        self._eye_action.setToolTip("Show password")
        self._eye_action.triggered.connect(self._toggle_password)

        layout.addWidget(self.username_input)
        layout.addSpacing(14)
        layout.addWidget(self.password_input)
        layout.addSpacing(14)

        self.error_label = QLabel("")
        self.error_label.setObjectName("LoginError")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.hide()
        layout.addWidget(self.error_label)

        layout.addSpacing(6)

        login_btn = QPushButton("Login")
        login_btn.setObjectName("PrimaryButton")
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.setFixedHeight(50)
        login_btn.clicked.connect(self._attempt_login)
        layout.addWidget(login_btn)
        layout.addSpacing(16)

        hint = QLabel("Default: admin / admin")
        hint.setObjectName("PageSubtitle")
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)

        layout.addStretch(1)
        return wrapper

    def _toggle_password(self):
        showing = self.password_input.echoMode() == QLineEdit.Normal
        self.password_input.setEchoMode(
            QLineEdit.Password if showing else QLineEdit.Normal
        )
        icons.rebind(self._eye_action, "eye" if showing else "eye_off")
        self._eye_action.setToolTip("Show password" if showing else "Hide password")

    def _set_error(self, message):
        self.error_label.setText(message)
        self.error_label.setVisible(bool(message))

    def showEvent(self, event):
        super().showEvent(event)
        self._center()

    def _center(self):
        screen = self.screen()
        if screen:
            geo = screen.availableGeometry()
            x = geo.center().x() - self.width() // 2
            y = geo.center().y() - self.height() // 2
            self.move(x, y)

    def _attempt_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if self._check_credentials(username, password):
            self._set_error("")
            self.close()
            self.login_success.emit(username.capitalize() or "Administrator")
        else:
            self._set_error("Invalid username or password.")

    def _check_credentials(self, username, password):
        return username == DEFAULT_USERNAME and password == DEFAULT_PASSWORD
