
import requests
from datetime import datetime
import customtkinter as ctk
import pytz
from io import BytesIO
from PIL import Image, ImageTk



class main(ctk.CTkFrame):  
    
    def __init__(self, parent):
        super().__init__(parent)

        #Add your own api key here
        self.API_KEY = "4df1ee20234521fe81b2178076612157"

        self.TIMEZONE = pytz.timezone("Europe/Berlin")
        self.TIME = datetime.now(self.TIMEZONE)
        self.DAY = self.TIME.strftime("%A")
        self.CITY = "Frankfurt"
        self.COUNTRY = "De"
        self.url = f"https://api.openweathermap.org/data/2.5/weather?q={self.CITY}&appid={self.API_KEY}"

        self.bg_color_conf = "#2b2b2b"

        #Getting the data from the api
        self.get_stats()
      

        #getting and resizing the main image
        self.icon_url = f"http://openweathermap.org/img/wn/{self.icon}.png"
        self.icon_data = requests.get(self.icon_url).content
        self.icon_img = Image.open(BytesIO(self.icon_data))
        self.icon_img_resized = self.icon_img.resize((165, 165))
        self.icon_img_tk = ImageTk.PhotoImage(self.icon_img_resized)


        #Button images
        
        self.switch_img_base_C = Image.open("images/Celcius.png")
        self.switch_img_resized_C = self.switch_img_base_C.resize((50, 30))  
        self.switch_img_tk_C = ImageTk.PhotoImage(self.switch_img_resized_C)

        self.switch_img_base_F = Image.open("images/Fahrenheit.png")
        self.switch_img_resized_F = self.switch_img_base_F.resize((50, 30))  
        self.switch_img_tk_F = ImageTk.PhotoImage(self.switch_img_resized_F)

        #sets Celcius as standard
        self.current_button = self.switch_img_tk_C

        #Frame for City Name and Coutny
        self.top_left_frame = ctk.CTkFrame(self, bg_color=self.bg_color_conf , height=20, width=100)
        self.top_left_frame.pack(side="top", anchor="w", pady=6, padx=6)
        self.city_country = ctk.CTkLabel(master=self.top_left_frame, text=f"{self.CITY}, {self.COUNTRY}", bg_color=self.bg_color_conf, text_color="white", font=("Arial", 35))
        self.city_country.pack()

        #Frame for short desroption like clouds, Day and current time
        self.middle_left_frame = ctk.CTkFrame(self, bg_color=self.bg_color_conf, height=20, width=100)
        self.middle_left_frame.pack(side="top", anchor="w", pady=6, padx=6)
        
        self.status_date_time_ctk = ctk.CTkLabel(master=self.middle_left_frame, text=f"{self.weather}  {self.DAY}, {self.TIME.strftime("%d.%m, %H:%M")}", bg_color=self.bg_color_conf, text_color="white", font=("Arial", 20))
        self.status_date_time_ctk.pack()
        
        self.update_time()    

        #main frame for stats
        self.main_stats = ctk.CTkFrame(self, fg_color=self.bg_color_conf, height=20, width=40)
        self.main_stats.pack(side="top", anchor="w")

        #Frame for Weather icon image
        self.main_icon_frame = ctk.CTkFrame(master=self.main_stats, fg_color=self.bg_color_conf, height=20, width=20)
        self.main_icon_frame.pack(side="top", anchor="w", pady=2, padx=2)
        
        self.main_icon = ctk.CTkLabel(master=self.main_stats,image=self.icon_img_tk, bg_color=self.bg_color_conf, text="")
        self.main_icon.pack(side="left")

        #Frame for Temperature and button
        self.temp_frame = ctk.CTkFrame(master=self.main_stats, fg_color=self.bg_color_conf, height=5, width=10)
        self.temp_frame.pack()
        
        self.temp = ctk.CTkLabel(master=self.temp_frame, text=f"{self.temp_celcius:.0F}°C", bg_color=self.bg_color_conf, text_color="white", font=("Arial", 20))
        self.temp.pack(pady=2, side="left")

        
        #Creates Switch besides Temperature to change Celcius to Fahrenheit
        self.Unit_Button = ctk.CTkButton(self.temp_frame, anchor="e", fg_color=self.bg_color_conf,hover_color=self.bg_color_conf, image=self.current_button, text="", width=15, command=self.button_change_unit)
        self.Unit_Button.pack(padx= 2, side="right")

        #Frame for Bar, high/low and humidity
        self.stats = ctk.CTkFrame(self.main_stats, fg_color=self.bg_color_conf, height=10, width=10)
        self.stats.pack()
        
        self.stats_max_min_temps = ctk.CTkLabel(self.stats, fg_color=self.bg_color_conf, text=f"High {self.max_celcius:.0F}°C    Low {self.min_celcius:.0F}°C", anchor="w")
        self.stats_max_min_temps.pack()
        
        self.bar = ctk.CTkLabel(master=self.stats, anchor="n", text="------------------------------------------", bg_color=self.bg_color_conf, text_color="gray")
        self.bar.pack()
        
        
        
        self.stats_humidtiy = ctk.CTkLabel(self.stats, fg_color=self.bg_color_conf, text=f"Humidity {self.humidty}%")
        self.stats_humidtiy.pack()
       
        self.stats_precipitation = ctk.CTkLabel(self.stats, fg_color=self.bg_color_conf, text=f"Precipitation {self.precipitation}%")
        self.stats_precipitation.pack()

        self.stats_windspeed = ctk.CTkLabel(self.stats, fg_color=self.bg_color_conf, text=f"Windspeed {self.windspeed}KpH")
        self.stats_windspeed.pack()



    def get_stats(self):
        self.response = requests.get(self.url).json()

        temp_kelvin = self.response['main']['temp']
        self.temp_celcius, self.temp_fahrenheit = self.kelvin_to_celcius_fahrenheit(temp_kelvin)
        max_temp = self.response['main']['temp_max']
        min_temp = self.response['main']['temp_min']
        self.max_celcius, self.max_fahrenheit = self.kelvin_high_to_celcius_fahrenheit(max_temp)
        self.min_celcius, self.min_fahrenheit = self.kelvin_high_to_celcius_fahrenheit(min_temp)
        self.weather = self.response['weather'][0]["description"]
        self.icon = self.response['weather'][0]['icon']
        self.humidty = self.response['main']['humidity']
        self.precipitation = self.response['clouds']['all']
        self.windspeed = self.response['wind']['speed'] 
        self.after(1000000, self.update_stats)

    def update_stats(self):
        self.status_date_time_ctk.configure(text=f"{self.weather}  {self.DAY}, {self.TIME.strftime("%d.%m, %H:%M")}")
        self.main_icon.configure(image=self.icon_img_tk)
        self.temp.configure(text=f"{self.temp_celcius:.0F}°C")
        self.stats_max_min_temps.configure(text=f"High {self.max_celcius:.0F}°C    Low {self.min_celcius:.0F}°C")
        self.stats_humidtiy.configure(text=f"Humidity {self.humidty}%")
        self.stats_precipitation.configure(text=f"Precipitation {self.precipitation}%")
        self.stats_windspeed.configure(text=f"Windspeed {self.windspeed}KpH")
        self.get_stats()
        


        #changes the Units of the image and temperature
    def button_change_unit(self):
        if self.current_button == self.switch_img_tk_C:
            self.current_button = self.switch_img_tk_F
            self.temp.configure(text=f"{self.temp_fahrenheit:.0F}°F")
            self.stats_max_min_temps.configure(text=f"High {self.max_fahrenheit:.0F}°F    Low {self.min_fahrenheit:.0F}°F")

        else:
            self.current_button = self.switch_img_tk_C
            self.temp.configure(text=f"{self.temp_celcius:.0F}°C")
            self.stats_max_min_temps.configure(text=f"High {self.max_celcius:.0F}°C    Low {self.min_celcius:.0F}°C")
        self.Unit_Button.configure(image=self.current_button)

        

    #Formats Kelvin to Celcius and Fahrenheit
    def kelvin_to_celcius_fahrenheit(self, kelvin):
        celcius = kelvin - 273.14
        fahrenheit = celcius * (9/5) + 32
        return celcius, fahrenheit
    
    #Formats max. Temp (Kelvin) to Fahrenheit and celcius
    def kelvin_high_to_celcius_fahrenheit(self, max_temp):
        max_celcius = max_temp - 273.14
        max_fahrenheit = max_celcius * (9/5) + 32
        return max_celcius, max_fahrenheit

     #Formats min. Temp (Kelvin) to Fahrenheit and celcius
    def kelvin_min_to_celcius_fahrenheit(self, min_temp):
        min_celcius = min_temp - 273.14
        min_fahrenheit = min_celcius * (9/5) + 32
        return min_celcius, min_fahrenheit



    #Updates the Time show in self.status_data_time_ctk every second
    def update_time(self):
        self.status_date_time_ctk.configure(text=f"{self.weather}  {self.DAY}, {self.TIME.strftime("%d.%m, %H:%M")}") 
        self.after(1000, self.update_time)

