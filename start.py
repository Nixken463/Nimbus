import customtkinter as ctk
from pagemanager import PageManager

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")


    app = PageManager()
    app.mainloop()