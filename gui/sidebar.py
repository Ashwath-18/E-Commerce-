import os
import customtkinter as ctk
from PIL import Image

from gui.theme import *


class Sidebar(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(
            master,
            width=SIDEBAR_WIDTH,
            fg_color=SIDEBAR,
            corner_radius=0
        )

        self.master = master

        self.grid(
            row=0,
            column=0,
            sticky="ns"
        )

        self.grid_propagate(False)

        self.asset_path = os.path.join(
            os.path.dirname(__file__),
            "assets"
        )

        self.buttons = {}
        self.active_page = None

        # ---------------- Logo ----------------

        logo = ctk.CTkImage(
            Image.open(
                os.path.join(
                    self.asset_path,
                    "logo.png"
                )
            ),
            size=(100, 100)
        )

        self.logo = ctk.CTkLabel(
            self,
            image=logo,
            text=""
        )

        self.logo.pack(
            pady=(18, 8)
        )

        # ---------------- Dashboard Heading ----------------

        self.title = ctk.CTkLabel(
            self,
            text="Dashboard",
            font=("Segoe UI", 24, "bold"),
            text_color=SIDEBAR_TEXT
        )

        self.title.pack(
            pady=(0, 10)
        )

        line = ctk.CTkFrame(
            self,
            height=1,
            fg_color=BORDER
        )

        line.pack(
            fill="x",
            padx=18,
            pady=(0, 16)
        )

        # ---------------- Scrollable Menu ----------------

        self.nav = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=BORDER,
            scrollbar_button_hover_color=PRIMARY
        )

        self.nav.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 10)
        )

        # ---------------- Button Function ----------------

        def add_button(text, icon_file, page_key, command=None):

            icon = ctk.CTkImage(
                Image.open(
                    os.path.join(
                        self.asset_path,
                        icon_file
                    )
                ),
                size=ICON_SIZE
            )

            button = ctk.CTkButton(
                self.nav,
                text="   " + text,
                image=icon,
                anchor="w",
                height=BUTTON_HEIGHT,
                corner_radius=14,
                fg_color="transparent",
                hover_color=HOVER,
                text_color=SIDEBAR_TEXT_MUTED,
                font=("Segoe UI", 14, "bold"),
                command=lambda: self.select(page_key, command)
            )

            button.pack(
                fill="x",
                pady=4,
                padx=6
            )

            self.buttons[page_key] = button

            return button

        add_button(
            "Products", "products.png", "products",
            command=lambda: self.master.show_page("products")
        )

        add_button(
            "Database", "database.png", "database",
            command=lambda: self.master.show_page("database")
        )

        add_button(
            "Orders", "orders.png", "orders",
            command=lambda: self.master.show_page("orders")
        )

        add_button(
            "Shipping", "shipping.png", "shipping",
            command=lambda: self.master.show_page("shipping")
        )

        add_button(
            "Users", "users.png", "users",
            command=lambda: self.master.show_page("users")
        )

        add_button(
            "Reviews", "reviews.png", "reviews",
            command=lambda: self.master.show_page("reviews")
        )

        add_button(
            "Search", "search.png", "search",
            command=lambda: self.master.show_page("search")
        )

        add_button(
            "AI Assistant", "ai.png", "ai",
            command=lambda: self.master.show_page("ai")
        )

        add_button(
            "Analytics", "analytics.png", "analytics",
            command=lambda: self.master.show_page("analytics")
        )

        add_button(
            "Settings", "settings.png", "settings",
            command=lambda: self.master.show_page("settings")
        )

        # ---------------- Logout ----------------

        logout_icon = ctk.CTkImage(
            Image.open(
                os.path.join(
                    self.asset_path,
                    "logout.png"
                )
            ),
            size=ICON_SIZE
        )

        self.logout_button = ctk.CTkButton(
            self.nav,
            text="   Logout",
            image=logout_icon,
            anchor="w",
            height=BUTTON_HEIGHT,
            corner_radius=14,
            fg_color="transparent",
            hover_color=HOVER,
            text_color=SIDEBAR_TEXT_MUTED,
            font=("Segoe UI", 14, "bold"),
            command=self.logout
        )

        self.logout_button.pack(
            fill="x",
            pady=(3, 8),
            padx=6
        )

        # Default active page on launch
        self.select("dashboard", None)
        self.active_page = "dashboard"

    # ---------------- Active State Handler ----------------

    def select(self, page_key, command):

        for key, btn in self.buttons.items():
            btn.configure(
                fg_color="transparent",
                text_color=SIDEBAR_TEXT_MUTED
            )

        if page_key in self.buttons:
            self.buttons[page_key].configure(
                fg_color=SIDEBAR_ACTIVE_BG,
                text_color=SIDEBAR_ACTIVE_TEXT
            )

        self.active_page = page_key

        if command:
            command()

    # ---------------- Logout Handler ----------------

    def logout(self):
        """
        Handles the logout action.
        Delegates to the master window's own logout() method if it
        defines one (e.g. to clear session state and show the login
        screen). Falls back to closing the app if not.
        """

        if hasattr(self.master, "logout") and callable(self.master.logout):
            self.master.logout()
        else:
            self.master.destroy()