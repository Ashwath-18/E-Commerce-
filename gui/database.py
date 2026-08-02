import customtkinter as ctk
from gui.theme import *

class DatabasePage(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(
            master,
            fg_color="transparent"
        )

        title = ctk.CTkLabel(
            self,
            text="Database",
            font=("Segoe UI", 28, "bold"),
            text_color=ACCENT
        )

        title.pack(
            pady=(30, 10)
        )

        subtitle = ctk.CTkLabel(
            self,
            text="Manage all database here.",
            font=("Segoe UI", 16),
            text_color=TEXT_LIGHT
        )

        subtitle.pack()