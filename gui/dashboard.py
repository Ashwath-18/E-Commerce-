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
        super().__init__(master, fg_color="transparent")

        # -------- Stat Cards Row --------
        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.pack(fill="x", padx=0, pady=(0, 20))

        stats.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="stat")

        def create_card(col, icon_char, title, value):

            card = ctk.CTkFrame(
                stats,
                fg_color=CARD,
                corner_radius=CARD_RADIUS,
                border_width=1,
                border_color=BORDER
            )
            card.grid(
                row=0, column=col,
                padx=8, pady=0,
                sticky="nsew"
            )

            icon_badge = ctk.CTkLabel(
                card,
                text=icon_char,
                font=("Segoe UI", 22),
                text_color=CARD,
                fg_color=ACCENT,
                corner_radius=14,
                width=48, height=48
            )
            icon_badge.pack(anchor="w", padx=24, pady=(24, 16))

            value_label = ctk.CTkLabel(
                card, text=value, font=STAT_FONT, text_color=ACCENT
            )
            value_label.pack(anchor="w", padx=24)

            title_label = ctk.CTkLabel(
                card, text=title, font=LABEL_FONT, text_color=TEXT_LIGHT
            )
            title_label.pack(anchor="w", padx=24, pady=(2, 24))

        create_card(0, "📦", "Products", str(total_products()))
        create_card(1, "👥", "Users", str(total_users()))
        create_card(2, "🛒", "Orders", str(total_orders()))
        create_card(3, "⭐", "Reviews", str(total_reviews()))

        # -------- Welcome Panel --------
        hero = ctk.CTkFrame(
            self,
            fg_color=CARD,
            corner_radius=CARD_RADIUS,
            border_width=1,
            border_color=BORDER
        )
        hero.pack(fill="both", expand=True, padx=0, pady=(0, 0))

        ctk.CTkLabel(
            hero, text="Welcome to Cartify",
            font=("Segoe UI", 30, "bold"), text_color=ACCENT
        ).pack(pady=(70, 8))

        ctk.CTkLabel(
            hero, text="Smart E-Commerce Management Dashboard",
            font=("Segoe UI", 15), text_color=TEXT_LIGHT
        ).pack()

        divider = ctk.CTkFrame(hero, height=3, width=60, fg_color=PRIMARY, corner_radius=2)
        divider.pack(pady=20)