import customtkinter as ctk
from settings import settings
from main import main
import os

class PageManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Nimbus")
        self.geometry("750x480")
        self.minsize(750, 480)
        self.maxsize(750, 480)
        self.pages = {}
        self.current_page = None
        file_path = "./settings.json"


        
        if os.path.exists(file_path):
            self.pages["settings"] = settings(self)
            self.pages["main"] = main(self)
            self.show_page("main")
        else:
            self.pages["settings"] = settings(self)
            self.show_page("settings")


    def load_page(self, page_name, page):
        self.pages[page_name] = page
    
    def show_page(self, page_name):
        #switches the page

        if self.current_page:
            self.current_page.pack_forget()

        page = self.pages[page_name]
        page.pack(fill="both", expand=True)
        self.current_page = page

    


