import requests
from datetime import datetime
import customtkinter as ctk
import pytz
from io import BytesIO
from PIL import Image, ImageTk
from collections import defaultdict


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
        self.url = f"https://api.openweathermap.org/data/2.5/weather?q={self.CITY}&units=metric&appid={self.API_KEY}"

        self.forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={self.CITY}&units=metric&appid={self.API_KEY}"

        self.bg_color_conf = "#2b2b2b"

        #Getting the data from the api
        self.get_stats()
        self.get_future_weather_data(self.forecast_response)

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
      


        

        #creates the frame to hold the stats andd icon for the next few days
        self.next_days_frame = ctk.CTkFrame(self, fg_color=self.bg_color_conf, height=10, width=200)  
        self.next_days_frame.pack(anchor="s", pady=25, fill="x")

        self.day1_frame = ctk.CTkFrame(self.next_days_frame, fg_color=self.bg_color_conf)
        self.day1_frame.pack(anchor="n", side="left", padx=5) 
        
        self.day1_day = ctk.CTkLabel(self.day1_frame, text=f"{self.day_of_day1}")
        self.day1_day.pack()

        self.day1_icon = ctk.CTkLabel(self.day1_frame, image=f"{self.icon1}", text="")
        self.day1_icon.pack()
        
        self.day1_temp = ctk.CTkLabel(self.day1_frame, text=f"High {self.temp_max_day1:.0F}°C  Low {self.temp_min_day1:.0F}°C")
        self.day1_temp.pack()
        

        self.day2_frame = ctk.CTkFrame(self.next_days_frame, fg_color=self.bg_color_conf)
        self.day2_frame.pack(anchor="n", side="left", padx=20)

        self.day2_day = ctk.CTkLabel(self.day2_frame, text=f"{self.day_of_day2}")
        self.day2_day.pack()

        self.day2_icon = ctk.CTkLabel(self.day2_frame, image=f"{self.icon2}", text="")
        self.day2_icon.pack()
        
        self.day2_temp = ctk.CTkLabel(self.day2_frame, text=f"High {self.temp_max_day2:.0F}°C  Low {self.temp_min_day2:.0F}°C")
        self.day2_temp.pack()


        self.day3_frame = ctk.CTkFrame(self.next_days_frame, fg_color=self.bg_color_conf)
        self.day3_frame.pack(anchor="n", side="left", padx=5)

        self.day3_day = ctk.CTkLabel(self.day3_frame, text=f"{self.day_of_day3}")
        self.day3_day.pack()

        self.day3_icon = ctk.CTkLabel(self.day3_frame, image=f"{self.icon3}", text="")
        self.day3_icon.pack()
        
        self.day3_temp = ctk.CTkLabel(self.day3_frame, text=f"High {self.temp_max_day3:.0F}°C  Low {self.temp_min_day3:.0F}°C")
        self.day3_temp.pack()

        
        self.update_stats()
    def get_future_weather_data(self, forecasts, num_days=3):
        today = datetime.now().date()
        weather_data = defaultdict(lambda: {'max': float('-inf'), 'min': float('inf'), 'icons': []})
        
        for forecast in self.forecast_response['list']:
            forecast_date = datetime.fromtimestamp(forecast['dt']).date()
            day_diff = (forecast_date - today).days
            
            if 1 <= day_diff <= num_days:
                #gets the min/max temp and all icons
                temp_max = forecast['main']['temp_max']
                temp_min = forecast['main']['temp_min']
                icon = forecast['weather'][0]['icon']
                weather_data[day_diff]['max'] = max(weather_data[day_diff]['max'], temp_max)
                weather_data[day_diff]['min'] = min(weather_data[day_diff]['min'], temp_min)
                weather_data[day_diff]['icons'].append(icon)
                weather_data[day_diff]['day_of_week'] = forecast_date.strftime('%A')

        # Determines the most common icon for each day
        for day in weather_data:
            icons = weather_data[day]['icons']
            weather_data[day]['main_icon'] = max(set(icons), key=icons.count)
            del weather_data[day]['icons']  # Remove the list of icons
        
        return weather_data

    
    def get_stats(self):
        self.response = requests.get(self.url).json()
        self.forecast_response = requests.get(self.forecast_url).json()

        #current weather stats
        self.temp_celcius = self.response['main']['temp']
        self.max_celcius = self.response['main']['temp_max']
        self.min_celcius = self.response['main']['temp_min']
        self.weather = self.response['weather'][0]["description"]
        self.icon = self.response['weather'][0]['icon']
        self.humidty = self.response['main']['humidity']
        self.precipitation = self.response['clouds']['all']
        self.windspeed = self.response['wind']['speed'] 

        #gets the data from the get_future_weather_data function
        weather_data = self.get_future_weather_data(self.forecast_response['list'])
       

        #stats for forecast
        self.temp_max_day1 = weather_data[1]['max']
        self.temp_min_day1 = weather_data[1]['min']
        self.day_of_day1 = weather_data[1]['day_of_week']
        self.icon_day1 = weather_data[1]['main_icon']

        self.temp_max_day2 = weather_data[2]['max']
        self.temp_min_day2 = weather_data[2]['min']
        self.day_of_day2 = weather_data[2]['day_of_week']
        self.icon_day2 = weather_data[2]['main_icon']

        self.temp_max_day3 = weather_data[3]['max']
        self.temp_min_day3 = weather_data[3]['min']
        self.day_of_day3 = weather_data[3]['day_of_week']
        self.icon_day3 = weather_data[3]['main_icon']

        for i in range(1, 4):
            icon = weather_data[i]['main_icon']
            setattr(self, f'icon_day{i}', icon)

            # Getting and resizing the image
            icon_url = f"http://openweathermap.org/img/wn/{icon}.png"
            icon_data = requests.get(icon_url).content
            icon_img = Image.open(BytesIO(icon_data))
            icon_img_resized = icon_img.resize((90, 90))
            icon_img_tk = ImageTk.PhotoImage(icon_img_resized)

            # Store the PhotoImage object as icon1, icon2, icon3
            setattr(self, f'icon{i}', icon_img_tk)


    def update_stats(self):
        self.get_stats()
        self.get_future_weather_data(self.forecast_response)
        self.celcius_to_fahrenheit()
        updates = {
            self.status_date_time_ctk: f"{self.weather}  {self.DAY}",
            self.main_icon: self.icon_img_tk,
            self.temp: f"{self.temp_celcius:.0F}°C",
            self.stats_max_min_temps: f"High {self.max_celcius:.0F}°C    Low {self.min_celcius:.0F}°C",
            self.stats_humidtiy: f"Humidity {self.humidty}%",
            self.stats_precipitation: f"Precipitation {self.precipitation}%",
            self.stats_windspeed: f"Windspeed {self.windspeed} KpH",
            self.day1_day: f"{self.day_of_day1}",
            self.day1_icon: self.icon1,
            self.day1_temp: f"High {self.temp_max_day1:.0F}°C  Low {self.temp_min_day1:.0F}°C",
            self.day2_day: f"{self.day_of_day2}",
            self.day2_icon: self.icon2,
            self.day2_temp: f"High {self.temp_max_day2:.0F}°C  Low {self.temp_min_day2:.0F}°C",
            self.day3_day: f"{self.day_of_day3}",
            self.day3_icon: self.icon3,
            self.day3_temp: f"High {self.temp_max_day3:.0F}°C  Low {self.temp_min_day3:.0F}°C"
            
            
        }

        for widget, value in updates.items():
            if isinstance(value, str):  # For text updates
                widget.configure(text=value)
            else:  # For image updates
                widget.configure(image=value)

        # Updates every 2 minutes
        self.after(120000, self.update_stats)
        


        #changes the Units of the image and temperature
    def button_change_unit(self):
        if self.current_button == self.switch_img_tk_C:
            self.current_button = self.switch_img_tk_F
            self.temp.configure(text=f"{self.temp_fahrenheit:.0F}°F")
            self.stats_max_min_temps.configure(text=f"High {self.max_fahrenheit:.0F}°F    Low {self.min_fahrenheit:.0F}°F")
            self.day1_temp.configure(text= f"High {self.temp_max_day1_F:.0F}°F  Low {self.temp_min_day1_F:.0F}°F")
            self.day2_temp.configure(text= f"High {self.temp_max_day2_F:.0F}°F  Low {self.temp_min_day2_F:.0F}°F")
            self.day3_temp.configure(text= f"High {self.temp_max_day3_F:.0F}°F  Low {self.temp_min_day3_F:.0F}°F")
        else:
            self.current_button = self.switch_img_tk_C
            self.temp.configure(text=f"{self.temp_celcius:.0F}°C")
            self.stats_max_min_temps.configure(text=f"High {self.max_celcius:.0F}°C    Low {self.min_celcius:.0F}°C")
            self.day1_temp.configure(text= f"High {self.temp_max_day1:.0F}°C  Low {self.temp_min_day1:.0F}°C")
            self.day2_temp.configure(text= f"High {self.temp_max_day2:.0F}°C  Low {self.temp_min_day2:.0F}°C")
            self.day3_temp.configure(text= f"High {self.temp_max_day3:.0F}°C  Low {self.temp_min_day3:.0F}°C")
        self.Unit_Button.configure(image=self.current_button)

        

    #Formats to Celcius and Fahrenheit
    def celcius_to_fahrenheit(self):
        
        self.temp_fahrenheit = self.temp_celcius * (9/5) + 32

        self.max_fahrenheit = self.max_celcius * (9/5) + 32
        self.temp_max_day1_F = self.temp_max_day1 * (9/5) + 32
        self.temp_max_day2_F = self.temp_max_day2 * (9/5) + 32
        self.temp_max_day3_F = self.temp_max_day3 * (9/5) + 32


        self.min_fahrenheit = self.min_celcius * (9/5) + 32
        self.temp_min_day1_F = self.temp_min_day1 * (9/5) + 32
        self.temp_min_day2_F = self.temp_min_day2 * (9/5) + 32
        self.temp_min_day3_F = self.temp_min_day3 * (9/5) + 32

    
  


    #Updates the Time show in self.status_data_time_ctk every second
    def update_time(self):
        self.TIMEZONE = pytz.timezone("Europe/Berlin")
        self.TIME = datetime.now(self.TIMEZONE)
        self.DAY = self.TIME.strftime("%A")
        self.status_date_time_ctk.configure(text=f"{self.weather}  {self.DAY}, {self.TIME.strftime("%d.%m, %H:%M")}") 
        self.after(1000, self.update_time)


