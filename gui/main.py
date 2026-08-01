import os
import customtkinter as ctk
from PIL import Image

from gui.theme import *
from gui.sidebar import Sidebar
from database.dashboard_stats import (
    total_products,
    total_users,
    total_orders,
    total_reviews
)


class EcommerceApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # --------------------------------------------------
        # Window
        # --------------------------------------------------

        self.title("E-Com Admin")

        self.geometry("1500x850")

        self.minsize(1300, 750)

        self.configure(fg_color=BACKGROUND)

        self.asset_path = os.path.join(
            os.path.dirname(__file__),
            "assets"
        )

        # --------------------------------------------------
        # Grid
        # --------------------------------------------------

        self.grid_columnconfigure(1, weight=1)

        self.grid_rowconfigure(0, weight=1)

        # --------------------------------------------------
        # Sidebar
        # --------------------------------------------------

        self.sidebar = Sidebar(self)

        # --------------------------------------------------
        # Main Area
        # --------------------------------------------------

        self.main_frame = ctk.CTkFrame(
            self,
            fg_color=BACKGROUND,
            corner_radius=0
        )

        self.main_frame.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        self.main_frame.grid_rowconfigure(1, weight=1)

        self.main_frame.grid_columnconfigure(0, weight=1)

        # --------------------------------------------------
        # Header
        # --------------------------------------------------

        self.header = ctk.CTkFrame(
            self.main_frame,
            height=80,
            fg_color=CARD,
            corner_radius=15
        )

        self.header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=20,
            pady=20
        )

        self.header.grid_columnconfigure(0, weight=1)

        # --------------------------------------------------
        # Header Title
        # --------------------------------------------------

        logo = ctk.CTkImage(
            Image.open(
                os.path.join(
                    self.asset_path,
                    "logo.png"
                )
            ),
            size=(56, 56)
        )

        logo_label = ctk.CTkLabel(
            self.header,
            image=logo,
            text=""
        )

        logo_label.grid(
            row=0,
            column=0,
            padx=(20, 10),
            pady=12,
            sticky="w"
        )

        title_frame = ctk.CTkFrame(
            self.header,
            fg_color="transparent"
        )

        title_frame.grid(
            row=0,
            column=0,
            padx=(90, 0),
            sticky="w"
        )

        title = ctk.CTkLabel(
            title_frame,
            text="E-Com Admin",
            font=("Segoe UI", 26, "bold"),
            text_color=ACCENT
        )

        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            title_frame,
            text="Smart Commerce Platform",
            font=("Segoe UI", 13),
            text_color=TEXT_LIGHT
        )

        subtitle.pack(anchor="w")

        # --------------------------------------------------
        # Admin Label
        # --------------------------------------------------

        self.admin = ctk.CTkLabel(
            self.header,
            text="Administrator",
            font=BUTTON_FONT,
            text_color=TEXT_LIGHT
        )

        self.admin.grid(
            row=0,
            column=1,
            padx=25
        )

        # --------------------------------------------------
        # Content Area
        # --------------------------------------------------

        self.content = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        self.content.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=20,
            pady=(0, 20)
        )

        # --------------------------------------------------
        # Welcome Card
        # --------------------------------------------------

        self.welcome = ctk.CTkFrame(
            self.content,
            fg_color=CARD,
            corner_radius=20
        )

        self.welcome.pack(
            fill="both",
            expand=True
        )

        # ---------------- Top Statistics ----------------

        stats = ctk.CTkFrame(
            self.welcome,
            fg_color="transparent"
        )

        stats.pack(
            fill="x",
            padx=30,
            pady=(30, 20)
        )


        def create_card(parent, title, value):

            card = ctk.CTkFrame(
                parent,
                width=220,
                height=110,
                fg_color="#FFF8F1",
                corner_radius=18
            )

            card.pack(
                side="left",
                padx=12,
                expand=True,
                fill="both"
            )

            card.pack_propagate(False)

            value_label = ctk.CTkLabel(
                card,
                text=value,
                font=("Segoe UI", 26, "bold"),
                text_color=ACCENT
            )

            value_label.pack(
                pady=(18, 5)
            )

            title_label = ctk.CTkLabel(
                card,
                text=title,
                font=("Segoe UI", 14),
                text_color=TEXT_LIGHT
            )

            title_label.pack()


        create_card(
            stats,
            "Products",
            str(total_products())
        )

        create_card(
            stats,
            "Users",
            str(total_users())
        )

        create_card(
            stats,
            "Orders",
            str(total_orders())
        )

        create_card(
            stats,
            "Reviews",
            str(total_reviews())
        )

        welcome_title = ctk.CTkLabel(
            self.welcome,
            text="Welcome to E-Com Admin",
            font=("Segoe UI", 28, "bold"),
            text_color=ACCENT
        )

        welcome_title.pack(
            pady=(120, 10)
        )

        welcome_subtitle = ctk.CTkLabel(
            self.welcome,
            text="Professional E-Commerce Management Dashboard",
            font=("Segoe UI", 18),
            text_color=TEXT_LIGHT
        )

        welcome_subtitle.pack()


if __name__ == "__main__":

    app = EcommerceApp()

    app.mainloop()