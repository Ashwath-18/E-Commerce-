import os
import customtkinter as ctk
from PIL import Image

from gui.theme import *


class Sidebar(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(
            master,
            width=280,
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
            font=("Segoe UI", 26, "bold"),
            text_color=ACCENT
        )

        self.title.pack(
            pady=(0, 10)
        )

        line = ctk.CTkFrame(
            self,
            height=1,
            fg_color="#D8C8B8"
        )

        line.pack(
            fill="x",
            padx=18,
            pady=(0, 12)
        )

        # ---------------- Scrollable Menu ----------------

        self.nav = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color="#C6A27A",
            scrollbar_button_hover_color="#B89369"
        )

        self.nav.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 10)
        )

        # ---------------- Button Function ----------------

        def add_button(text, icon_file, color="transparent"):

            icon = ctk.CTkImage(
                Image.open(
                    os.path.join(
                        self.asset_path,
                        icon_file
                    )
                ),
                size=(38, 38)
            )

            button = ctk.CTkButton(
                self.nav,
                text="   " + text,
                image=icon,
                anchor="w",
                height=50,
                corner_radius=14,
                fg_color=color,
                hover_color=HOVER,
                text_color=ACCENT,
                font=("Segoe UI", 15, "bold")
            )

            button.pack(
                fill="x",
                pady=3
            )

            self.buttons[text] = button
            return button

        add_button(
            "Products",
            "products.png"
        )

        add_button(
            "Database",
            "database.png"
        )

        add_button(
            "Orders",
            "orders.png"
        )

        add_button(
            "Shipping",
            "shipping.png"
        )

        add_button(
            "Users",
            "users.png"
        )

        add_button(
            "Reviews",
            "reviews.png"
        )

        add_button(
            "Search",
            "search.png"
        )

        add_button(
            "AI Assistant",
            "ai.png"
        )

        add_button(
            "Analytics",
            "analytics.png"
        )

        add_button(
            "Settings",
            "settings.png"
        )

        # ---------------- Logout ----------------

        logout_icon = ctk.CTkImage(
            Image.open(
                os.path.join(
                    self.asset_path,
                    "logout.png"
                )
            ),
            size=(38, 38)
        )

        self.logout_button = ctk.CTkButton(
            self.nav,
            text="   Logout",
            image=logout_icon,
            anchor="w",
            height=50,
            corner_radius=14,
            fg_color="transparent",
            hover_color=HOVER,
            text_color=ACCENT,
            font=("Segoe UI", 15, "bold"),
            command=self.logout
        )

        self.logout_button.pack(
            fill="x",
            pady=(3, 8)
        )

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