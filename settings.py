import customtkinter as ctk
import requests
from tkinter import messagebox
import json
from main import main
import pytz

class settings(ctk.CTkFrame):
    
    def __init__(self, parent):
        super().__init__(parent)
        with open("language.json", "r") as file:
            self.language = json.load(file)

        
        
        try: 
            with open("settings.json", "r") as file:
                self.settings = json.load(file)
            self.select_lang = self.settings['language']
            self.text_city = self.settings['city']
        except FileNotFoundError:
            self.select_lang = "English"
            self.text_city = ""

      
        self.key_standard = self.language[f"{self.select_lang}"]['Key']['standard']
        self.key_own = self.language[f"{self.select_lang}"]['Key']['own']
        self.save_text = self.language[f"{self.select_lang}"]['Save']
        self.city_placeholder = self.language[f"{self.select_lang}"]["City"]
        self.api_placeholder = self.language[f"{self.select_lang}"]['Key']['placeholder']
        self.city_error = self.language[f"{self.select_lang}"]['save_error']['wrong_city']
        self.api_error = self.language[f"{self.select_lang}"]['save_error']['api_key']
        self.blank_error = self.language[f"{self.select_lang}"]['save_error']['blank']
        self.timezones = list(pytz.common_timezones)
       

        self.lang_select = None
        self.lang_select_type()

        self.unit_selected = None
        self.unit_select()

        self.key_type_selected = None
        self.own_api_insert()

        self.parent = parent
        self.bg_color_conf = "#2b2b2b"
        self.settings_main_frame = ctk.CTkFrame(self)
        self.settings_main_frame.pack()

        self.name_frame = ctk.CTkFrame(self.settings_main_frame)
        self.name_frame.pack()
        
        self.name = ctk.CTkLabel(self.name_frame, text="Nimbus",font=("Arial", 50) )
        self.name.pack()

        self.select_frame = ctk.CTkFrame(self, fg_color=self.bg_color_conf)
        self.select_frame.pack(pady=30)

        self.lang_select = ctk.CTkOptionMenu(self.select_frame, values=self.lang_select, bg_color=self.bg_color_conf, command=self.update_lang)
        self.lang_select.pack()

        self.api_menu = ctk.CTkOptionMenu(self.select_frame, values=self.key_type_selected, bg_color=self.bg_color_conf, command=self.api_field)
        self.api_menu.pack(pady=10)

        self.api_entry = ctk.CTkEntry(self.select_frame, placeholder_text_color="gray", placeholder_text=f"{self.api_placeholder}" )
       
        self.city_frame= ctk.CTkFrame(self)
        self.city_frame.pack()
        
        self.unit_menu = ctk.CTkOptionMenu(self.city_frame, values=self.unit_selected,bg_color=self.bg_color_conf)
        self.unit_menu.pack(pady=5)

        self.city_entry = ctk.CTkEntry(self.city_frame, placeholder_text=f"{self.city_placeholder}", placeholder_text_color="gray")
        self.city_entry.pack()
        self.city_entry.insert(0, self.text_city)

        self.save_button = ctk.CTkButton(self, text=f"{self.save_text}", command=self.check_api_key_city )
        self.save_button.pack(pady=5)
        self.api_field(self.api_menu.get())


    def check_api_key_city(self):
        if self.api_menu.get() == self.key_own:
            self.API_KEY = self.api_entry.get()
            self.key_type = "own"
        else:
            self.API_KEY = "4df1ee20234521fe81b2178076612157"
            self.key_type = "standard"
        self.CITY = self.city_entry.get().strip() 
        
        self.url = f"https://api.openweathermap.org/data/2.5/weather?q={self.CITY}&units=metric&appid={self.API_KEY}"
        
        try:
            response = requests.get(self.url)
            data = response.json()  # Parse JSON response
            
            # Check for HTTP errors
            if response.status_code != 200:
                if "message" in data:
                    error_message = data['message']
                    if "city not found" in error_message.lower():
                        messagebox.showerror("Error", f"{self.city_error}")
                    elif "invalid api key" in error_message.lower():
                        messagebox.showerror("Error",f"{self.api_error}")
                    else:
                        messagebox.showerror("Error", f"{self.blank_error}")
                else:
                    messagebox.showerror("Error", "An unexpected error occurred while fetching data.")
                return
            
            # If successful, process the data
            self.save_settings()
            
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Request Failed", f"Request failed: {e}")



    def save_settings(self):
        if self.lang_select.get() == "English":
            self.lang_key = "en_US.UTF-8"
        if self.lang_select.get() == "Deutsch":
            self.lang_key = "de_DE.UTF-8"
        if self.lang_select.get() == "Español":
            self.lang_key = "es_ES.UTF-8"
        settings = {
            "language": self.lang_select.get(),
            "api_key": self.API_KEY,
            "city": self.city_entry.get(),
            "key_type": self.key_type,
            "unit": self.unit_menu.get(),
            "lang_key": self.lang_key

        }
        with open("settings.json", "w") as f:
            json.dump(settings, f, indent=4)
        self.parent.load_page("main", main(self.parent))
        self.parent.show_page("main")
        


    def api_field(self, choice):
        """Callback function to handle API key selection."""
        if choice == f"{self.key_standard}":
            self.api_entry.delete(0, 'end')  # Clear the entry field
            self.api_entry.pack_forget()  # Hide the entry field if using standard key
        else:
            self.api_entry.pack()
            try:   # Show the entry field if using own key
                with open("settings.json", "r") as file:
                    self.settings = json.load(file)
                    if self.settings['key_type'] == "own":
                        self.api_entry.insert(0, self.settings['api_key'])
                    else:
                        pass
            except FileNotFoundError:
                pass


    def switch_lang(self, language):
        if language == "English":
            self.lang = "English"
            self.lang_key = "en_EN.UTF-8"
        if language == "Deutsch":
            self.lang = "Deutsch"
            self.lang_key = "de_DE.UTF-8"
        if language == "Español":
            self.lang = "Español"
            self.lang_key = "es_ES.UTF-8"

    def update_translations(self):
        lang = self.language[self.select_lang]
        
        # Update attributes and UI elements
        updates = {
            'key_standard': lang['Key']['standard'],
            'key_own': lang['Key']['own'],
            'save_text': lang['Save'],
            'city_placeholder': lang['City'],
            'api_placeholder': lang['Key']['placeholder'],
            'city_error': lang['save_error']['wrong_city'],
            'api_error': lang['save_error']['api_key'],
            'blank_error': lang['save_error']['blank']
    }
    
        [setattr(self, attr, value) for attr, value in updates.items()]
        
        # Update UI elements
        self.save_button.configure(text=self.save_text)
        self.city_entry.configure(placeholder_text=self.city_placeholder)
        self.api_menu.configure(values=[self.key_standard, self.key_own])
        

    def lang_select_type(self):
        try: 
            with open("settings.json", "r") as file:
                self.settings = json.load(file)
            self.select_lang = self.settings['language']

            if self.select_lang == "Deutsch":
                self.lang_select = ["Deutsch", "English", "Español"]

            elif self.select_lang == "English":
                self.lang_select = ["English", "Deutsch", "Español"]

            else:
                self.lang_select = ["Español", "English", "Deutsch"]

        except FileNotFoundError:
            self.lang_select = ["English", "Deutsch", "Español"]

    def unit_select(self):
        try:
            with open("settings.json", "r") as file:
                self.settings = json.load(file)
            self.select_unit = self.settings['unit']
            if self.select_unit == "Metric":
                self.unit_selected = ["Metric", "Imperial"]
            else:
                self.unit_selected = ["Imperial", "Metric"]
        except FileNotFoundError:
            self.unit_selected = ["Metric", "Imperial"]
    
    def own_api_insert(self):
        try:
            with open("settings.json", "r") as file:
                self.settings = json.load(file)
            self.key_select_type = self.settings['key_type']
            if self.key_select_type == "own":
                self.key_type_selected = [self.language[f"{self.select_lang}"]['Key']['own'], self.language[f"{self.select_lang}"]['Key']['standard']]
                
            else:
                self.key_type_selected = [self.language[f"{self.select_lang}"]['Key']['standard'], self.language[f"{self.select_lang}"]['Key']['own']]
        except FileNotFoundError:
            self.key_type_selected = ["Use standard Key", "Use your own Key"]

    def update_lang(self, selected_language):
       
        self.select_lang = selected_language  # Update the selected language
        self.update_translations()  # Update translations for all UI elements

        # Refresh UI elements that depend on language
        self.lang_select.configure(self.lang_select)  # Update dropdown options
        self.lang_select.set(self.select_lang)  # Set the current selection
        self.api_entry.configure(placeholder_text=self.api_placeholder) 
        self.city_entry.configure(placeholder_text=self.city_placeholder)  # Update city placeholder text
        self.save_button.configure(text=self.save_text)  # Update save button text
         # Update API menu options and reset its selected value
        self.api_menu.configure(values=[self.key_standard, self.key_own])
        self.api_menu.set(self.key_standard)  # Set to default (or any desired value)
