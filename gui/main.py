import os
import customtkinter as ctk
from PIL import Image

from gui.theme import *
from gui.sidebar import Sidebar

from gui.dashboard import DashboardPage
from gui.products import ProductsPage
from gui.database import DatabasePage
from gui.orders import OrdersPage
from gui.shipping import ShippingPage
from gui.users import UsersPage
from gui.reviews import ReviewsPage
from gui.search import SearchPage
from gui.ai_assistant import AIAssistantPage
from gui.analytics import AnalyticsPage
from gui.settings import SettingsPage


class EcommerceApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # --------------------------------------------------
        # Window
        # --------------------------------------------------

        self.title("Cartify")

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
            height=90,
            fg_color=CARD,
            corner_radius=CARD_RADIUS,
            border_width=1,
            border_color=BORDER
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
            text="CARTIFY",
            font=("Segoe UI", 26, "bold"),
            text_color=ACCENT
        )

        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            title_frame,
            text="Smart E-Commerce Platform",
            font=("Segoe UI", 13),
            text_color=TEXT_LIGHT
        )

        subtitle.pack(anchor="w")

        # --------------------------------------------------
        # Admin Label (icon-circle removed, clean text only)
        # --------------------------------------------------

        self.admin = ctk.CTkLabel(
            self.header,
            text="Administrator",
            font=BUTTON_FONT,
            text_color=ACCENT
        )

        self.admin.grid(
            row=0,
            column=1,
            padx=30
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

        self.pages = {}

        # --------------------------------------------------
        # Register Pages
        # --------------------------------------------------

        self.pages["dashboard"] = DashboardPage(self.content)
        self.pages["products"] = ProductsPage(self.content)
        self.pages["database"] = DatabasePage(self.content)
        self.pages["orders"] = OrdersPage(self.content)
        self.pages["shipping"] = ShippingPage(self.content)
        self.pages["users"] = UsersPage(self.content)
        self.pages["reviews"] = ReviewsPage(self.content)
        self.pages["search"] = SearchPage(self.content)
        self.pages["ai"] = AIAssistantPage(self.content)
        self.pages["analytics"] = AnalyticsPage(self.content)
        self.pages["settings"] = SettingsPage(self.content)

        self.show_page("dashboard")

    def show_page(self, page_name):

        # Hide all pages
        for page in self.pages.values():
            page.pack_forget()

        # Show selected page
        page = self.pages[page_name]

        page.pack(
            fill="both",
            expand=True
        )


if __name__ == "__main__":

    app = EcommerceApp()

    app.mainloop()