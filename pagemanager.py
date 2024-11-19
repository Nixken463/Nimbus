import customtkinter as ctk
from settings import settings
from main import main


class PageManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Weather")
        self.geometry("720x480")


        self.pages = {}
        self.current_page = None

        self.setup_pages()
        self.show_page("settings")


    def setup_pages(self):
        #Creates and Stores the Page
        self.pages["main"] = main(self)
        self.pages["settings"] = settings(self)

    
    def show_page(self, page_name):
        #switches the page

        if self.current_page:
            self.current_page.pack_forget()

        page = self.pages[page_name]
        page.pack(fill="both", expand=True)
        self.current_page = page

    


