import customtkinter as ctk
from gui.theme import *
from database.dashboard_stats import (
    total_products,
    total_users,
    total_orders,
    total_reviews
)


class DashboardPage(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(
            master,
            fg_color=CARD,
            corner_radius=20
        )

        # ---------------- Top Statistics ----------------

        stats = ctk.CTkFrame(
            self,
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
            self,
            text="Welcome to E-Com Admin",
            font=("Segoe UI", 28, "bold"),
            text_color=ACCENT
        )

        welcome_title.pack(
            pady=(60, 10)
        )

        welcome_subtitle = ctk.CTkLabel(
            self,
            text="Professional E-Commerce Management Dashboard",
            font=("Segoe UI", 18),
            text_color=TEXT_LIGHT
        )

        welcome_subtitle.pack()