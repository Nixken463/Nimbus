import customtkinter as ctk

class settings(ctk.CTkFrame):
    def __init__(self, parent):

        super().__init__(parent)
        ctk.CTkLabel(self, text="Settings").pack()
        ctk.CTkButton(self, text="Back to main", command=lambda: parent.show_page("main")).pack()

