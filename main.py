import requests
from datetime import datetime
import customtkinter as ctk
import pytz
from io import BytesIO
from PIL import Image, ImageTk
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.interpolate import make_interp_spline
import json
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import locale


class main(ctk.CTkFrame):  
    
    def __init__(self, parent):
        super().__init__(parent)
        with open("settings.json", "r") as file:
            self.settings = json.load(file)
        with open("language.json", "r") as file:
            language = json.load(file)


                # Initialize geolocator and TimezoneFinder
        geolocator = Nominatim(user_agent="arch_test_agent")
        self.tf = TimezoneFinder()

        # Get location for the city
        city = self.settings['city']
        location = geolocator.geocode(city)
        self.lat, self.lng = location.latitude, location.longitude  # Ensure order: lat, lng

      

        #Since it's a free API Code and I dont have ressources for a API server 
        #I decided to keep the key in plain code although this is a bad practice
        self.API_KEY = "4df1ee20234521fe81b2178076612157"
        self.TIMEZONE_Name = self.tf.timezone_at(lat=self.lat, lng=self.lng)
        self.TIMEZONE = pytz.timezone(self.TIMEZONE_Name)
        self.TIME = datetime.now(self.TIMEZONE)
        locale.setlocale(locale.LC_TIME, self.settings['lang_key'])
        self.DAY = self.TIME.strftime("%A")
        self.CITY = self.settings["city"]
        self.language = self.settings['language']
        self.lang = language[f'{self.language}']["lang"]
        self.text_high = language[f'{self.language}']['high']
        self.text_low = language[f'{self.language}']['low']
        self.text_humidity = language[f'{self.language}']['humidity']
        self.text_precipitation = language[f'{self.language}']['precipitation']
        self.text_windspeed = language[f'{self.language}']['windspeed']


        self.url = f"https://api.openweathermap.org/data/2.5/weather?q={self.CITY}&lang={self.lang}&units=metric&appid={self.API_KEY}"

        self.forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={self.CITY}&units=metric&appid={self.API_KEY}"

        self.bg_color_conf = "#2b2b2b"
        
        #Getting the data from the api
        self.get_stats()
        self.get_future_weather_data(self.forecast_response)
        self.COUNTRY = self.response['sys']['country']
        #getting and resizing the main image
        self.icon_url = f"http://openweathermap.org/img/wn/{self.icon}.png"
        self.icon_data = requests.get(self.icon_url).content
        self.icon_img = Image.open(BytesIO(self.icon_data))
        self.icon_img_resized = self.icon_img.resize((165, 165))
        self.icon_img_tk = ImageTk.PhotoImage(self.icon_img_resized)


        #Button images
        
        self.switch_img_base_C = Image.open("images/Celsius.png")
        self.switch_img_resized_C = self.switch_img_base_C.resize((50, 30))  
        self.switch_img_tk_C = ImageTk.PhotoImage(self.switch_img_resized_C)

        self.switch_img_base_F = Image.open("images/Fahrenheit.png")
        self.switch_img_resized_F = self.switch_img_base_F.resize((50, 30))  
        self.switch_img_tk_F = ImageTk.PhotoImage(self.switch_img_resized_F)

        #sets celsius as standard

        if self.settings['unit'] == "Metric":
            self.current_button = self.switch_img_tk_C
        else:
            self.current_button = self.switch_img_tk_F

        #frame for holding the button to change to the settings
        self.settings_frame = ctk.CTkFrame(self, fg_color=self.bg_color_conf, height=40, width=10)
        self.settings_frame.pack(side="right", anchor="n", pady=5, padx=5)

        self.settings_img_base = Image.open("images/Settings.png")
        self.settings_img_resize = self.settings_img_base.resize((30,30))
        self.settings_img_final = ImageTk.PhotoImage(self.settings_img_resize)

        self.settings_button = ctk.CTkButton(self.settings_frame, width=20,image=self.settings_img_final, command=lambda: parent.show_page("settings"), text="", fg_color=self.bg_color_conf, hover_color=self.bg_color_conf )
        self.settings_button.pack()


        #Frame for City Name and Country
        self.top_left_frame = ctk.CTkFrame(self, bg_color=self.bg_color_conf , height=20, width=100)
        self.top_left_frame.pack(side="top", anchor="w", pady=6, padx=6)
        self.city_country = ctk.CTkLabel(master=self.top_left_frame, text=f"{self.CITY}, {self.COUNTRY}", bg_color=self.bg_color_conf, text_color="white", font=("Arial", 35))
        self.city_country.pack()

       


        #Frame for short description like cloudy, Day and current time
        self.middle_left_frame = ctk.CTkFrame(self, bg_color=self.bg_color_conf, height=20, width=100)
        self.middle_left_frame.pack(side="top", anchor="w", pady=6, padx=6)
        

        self.status_date_time_ctk = ctk.CTkLabel(master=self.middle_left_frame, text=f"{self.weather}  {self.DAY}, {self.TIME.strftime("%d.%m, %H:%M")}", bg_color=self.bg_color_conf, text_color="white", font=("Arial", 20))
        self.status_date_time_ctk.pack()
        
        self.update_time()
        

        #frame for holding all stats + the graph 
        self.main_frame = ctk.CTkFrame(self, fg_color=self.bg_color_conf,)
        self.main_frame.pack(side="top", anchor="w")
        


        #frame that holds the graph
        self.graph_frame = ctk.CTkFrame(self.main_frame, height=100, width=200)
        self.graph_frame.pack(side="right", anchor="e")
        self.graph_data(self.forecast_response)
        self.temperatures = [float(temp.rstrip('C')) for temp in self.temps_celsius]
        self.make_graph()

        #main frame for stats
        self.main_stats = ctk.CTkFrame(self.main_frame, fg_color=self.bg_color_conf, height=20, width=40)
        self.main_stats.pack(side="top", anchor="w")
        
        #Frame for Weather icon image
        self.main_icon_frame = ctk.CTkFrame(master=self.main_stats, fg_color=self.bg_color_conf, height=20, width=20)
        self.main_icon_frame.pack(side="top", anchor="w", pady=2, padx=2)
        
        self.main_icon = ctk.CTkLabel(master=self.main_stats,image=self.icon_img_tk, bg_color=self.bg_color_conf, text="")
        self.main_icon.pack(side="left")

        #Frame for Temperature and button
        self.temp_frame = ctk.CTkFrame(master=self.main_stats, fg_color=self.bg_color_conf, height=5, width=10)
        self.temp_frame.pack()
        
        self.temp = ctk.CTkLabel(master=self.temp_frame, text=f"{self.temp_celsius:.0F}°C", bg_color=self.bg_color_conf, text_color="white", font=("Arial", 20))
        self.temp.pack(pady=2, side="left")

        
        #Creates Switch besides Temperature to change celsius to Fahrenheit
        self.Unit_Button = ctk.CTkButton(self.temp_frame, anchor="e", fg_color=self.bg_color_conf,hover_color=self.bg_color_conf, image=self.current_button, text="", width=15, command=self.button_change_unit)
        self.Unit_Button.pack(padx= 2, side="right")

        #Frame for Bar, high/low and humidity
        self.stats = ctk.CTkFrame(self.main_stats, fg_color=self.bg_color_conf, height=10, width=15)
        self.stats.pack()
        
        self.stats_max_min_temps = ctk.CTkLabel(self.stats, fg_color=self.bg_color_conf, text=f"{self.text_high} {self.max_celsius:.0F}°C    {self.text_low} {self.min_celsius:.0F}°C", anchor="w")
        self.stats_max_min_temps.pack()
        
        self.bar = ctk.CTkLabel(master=self.stats, anchor="n", text="------------------------------------------", bg_color=self.bg_color_conf, text_color="gray")
        self.bar.pack()
                
        self.stats_humidtiy = ctk.CTkLabel(self.stats, fg_color=self.bg_color_conf, text=f"{self.humidty} {self.humidty}%")
        self.stats_humidtiy.pack()
       
        self.stats_precipitation = ctk.CTkLabel(self.stats, fg_color=self.bg_color_conf, text=f"{self.text_precipitation} {self.precipitation}%")
        self.stats_precipitation.pack()

        self.stats_windspeed = ctk.CTkLabel(self.stats, fg_color=self.bg_color_conf, text=f"{self.windspeed} {self.windspeed}KpH")
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
        
        self.day1_temp = ctk.CTkLabel(self.day1_frame, text=f"{self.text_high} {self.temp_max_day1:.0F}°C  {self.text_low} {self.temp_min_day1:.0F}°C")
        self.day1_temp.pack()
        

        self.day2_frame = ctk.CTkFrame(self.next_days_frame, fg_color=self.bg_color_conf)
        self.day2_frame.pack(anchor="n", side="left", padx=20)

        self.day2_day = ctk.CTkLabel(self.day2_frame, text=f"{self.day_of_day2}")
        self.day2_day.pack()

        self.day2_icon = ctk.CTkLabel(self.day2_frame, image=f"{self.icon2}", text="")
        self.day2_icon.pack()
        
        self.day2_temp = ctk.CTkLabel(self.day2_frame, text=f"{self.text_high} {self.temp_max_day2:.0F}°C  {self.text_low} {self.temp_min_day2:.0F}°C")
        self.day2_temp.pack()


        self.day3_frame = ctk.CTkFrame(self.next_days_frame, fg_color=self.bg_color_conf)
        self.day3_frame.pack(anchor="n", side="left", padx=5)

        self.day3_day = ctk.CTkLabel(self.day3_frame, text=f"{self.day_of_day3}")
        self.day3_day.pack()

        self.day3_icon = ctk.CTkLabel(self.day3_frame, image=f"{self.icon3}", text="")
        self.day3_icon.pack()
        
        self.day3_temp = ctk.CTkLabel(self.day3_frame, text=f"{self.text_high} {self.temp_max_day3:.0F}°C  {self.text_low} {self.temp_min_day3:.0F}°C")
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
        self.temp_celsius = self.response['main']['temp']
        self.max_celsius = self.response['main']['temp_max']
        self.min_celsius = self.response['main']['temp_min']
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
        self.celsius_to_fahrenheit()
        updates = {
            self.status_date_time_ctk: f"{self.weather}  {self.DAY}",
            self.main_icon: self.icon_img_tk,
            self.temp: f"{self.temp_celsius:.0F}°C",
            self.stats_max_min_temps: f"{self.text_high} {self.max_celsius:.0F}°C    {self.text_low} {self.min_celsius:.0F}°C",
            self.stats_humidtiy: f"{self.text_humidity} {self.humidty}%",
            self.stats_precipitation: f"{self.text_precipitation} {self.precipitation}%",
            self.stats_windspeed: f"{self.text_windspeed} {self.windspeed} KpH",
            self.day1_day: f"{self.day_of_day1}",
            self.day1_icon: self.icon1,
            self.day1_temp: f"{self.text_high} {self.temp_max_day1:.0F}°C  {self.text_low} {self.temp_min_day1:.0F}°C",
            self.day2_day: f"{self.day_of_day2}",
            self.day2_icon: self.icon2,
            self.day2_temp: f"{self.text_high} {self.temp_max_day2:.0F}°C  {self.text_low} {self.temp_min_day2:.0F}°C",
            self.day3_day: f"{self.day_of_day3}",
            self.day3_icon: self.icon3,
            self.day3_temp: f"{self.text_high} {self.temp_max_day3:.0F}°C  {self.text_low} {self.temp_min_day3:.0F}°C"
            
            
        }

        for widget, value in updates.items():
            if isinstance(value, str):  # For text updates
                widget.configure(text=value)
            else:  # For image updates
                widget.configure(image=value)
        
        # Updates every 2 minutes
        self.after(120000, self.update_stats)
        

        if self.current_button == self.switch_img_tk_F:
            self.current_button = self.switch_img_tk_F
            self.temp.configure(text=f"{self.temp_fahrenheit:.0F}°F")
            self.stats_max_min_temps.configure(text=f"{self.text_high} {self.max_fahrenheit:.0F}°F    {self.text_low} {self.min_fahrenheit:.0F}°F")
            self.day1_temp.configure(text= f"{self.text_high} {self.temp_max_day1_F:.0F}°F  {self.text_low} {self.temp_min_day1_F:.0F}°F")
            self.day2_temp.configure(text= f"{self.text_high} {self.temp_max_day2_F:.0F}°F  {self.text_low} {self.temp_min_day2_F:.0F}°F")
            self.day3_temp.configure(text= f"{self.text_high} {self.temp_max_day3_F:.0F}°F  {self.text_low} {self.temp_min_day3_F:.0F}°F")
            self.temperatures = [float(temp.rstrip('F')) for temp in self.temps_fahrenheit]
            self.make_graph()
        #changes the Units of the image and temperature
    def button_change_unit(self):
        if self.current_button == self.switch_img_tk_C:
            self.current_button = self.switch_img_tk_F
            self.temp.configure(text=f"{self.temp_fahrenheit:.0F}°F")
            self.stats_max_min_temps.configure(text=f"{self.text_high} {self.max_fahrenheit:.0F}°F    {self.text_low} {self.min_fahrenheit:.0F}°F")
            self.day1_temp.configure(text= f"{self.text_high} {self.temp_max_day1_F:.0F}°F  {self.text_low} {self.temp_min_day1_F:.0F}°F")
            self.day2_temp.configure(text= f"{self.text_high} {self.temp_max_day2_F:.0F}°F  {self.text_low} {self.temp_min_day2_F:.0F}°F")
            self.day3_temp.configure(text= f"{self.text_high} {self.temp_max_day3_F:.0F}°F  {self.text_low} {self.temp_min_day3_F:.0F}°F")
            self.temperatures = [float(temp.rstrip('F')) for temp in self.temps_fahrenheit]
            self.make_graph()
        else:
            self.current_button = self.switch_img_tk_C
            self.temp.configure(text=f"{self.temp_celsius:.0F}°C")
            self.stats_max_min_temps.configure(text=f"{self.text_high} {self.max_celsius:.0F}°C    {self.text_low} {self.min_celsius:.0F}°C")
            self.day1_temp.configure(text= f"{self.text_high} {self.temp_max_day1:.0F}°C  {self.text_low} {self.temp_min_day1:.0F}°C")
            self.day2_temp.configure(text= f"{self.text_high} {self.temp_max_day2:.0F}°C  {self.text_low} {self.temp_min_day2:.0F}°C")
            self.day3_temp.configure(text= f"{self.text_high} {self.temp_max_day3:.0F}°C  {self.text_low} {self.temp_min_day3:.0F}°C")
            self.temperatures = [float(temp.rstrip('C')) for temp in self.temps_celsius]
            self.make_graph()
        self.Unit_Button.configure(image=self.current_button)

        

    #Formats to celsius and Fahrenheit
    def celsius_to_fahrenheit(self):
        
        def convert(temp_c):
            return temp_c * (9/5) + 32

        # Convert current temperature
        self.temp_fahrenheit = convert(self.temp_celsius)

        # Convert max temperatures
        self.max_fahrenheit = convert(self.max_celsius)
        for i in range(1, 4):
            setattr(self, f'temp_max_day{i}_F', convert(getattr(self, f'temp_max_day{i}')))

        # Convert min temperatures
        self.min_fahrenheit = convert(self.min_celsius)
        for i in range(1, 4):
            setattr(self, f'temp_min_day{i}_F', convert(getattr(self, f'temp_min_day{i}')))

    
  


    #Updates the Time show in self.status_data_time_ctk every second
    def update_time(self):
        self.TIMEZONE_Name = self.tf.timezone_at(lat=self.lat, lng=self.lng)
        self.TIMEZONE = pytz.timezone(self.TIMEZONE_Name)
        self.TIME = datetime.now(self.TIMEZONE)
        locale.setlocale(locale.LC_TIME, self.settings['lang_key'])
        self.DAY = self.TIME.strftime("%A")
        self.status_date_time_ctk.configure(text=f"{self.weather}  {self.DAY}, {self.TIME.strftime("%d.%m, %H:%M")}") 
        self.after(1000, self.update_time)

    
    

    #creates the graph and draws it on the window
    def make_graph(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy() 
        

            
        # Create time indices
        time_indices = np.arange(len(self.times))

        # Create a smooth line using interpolation
        time_smooth = np.linspace(0, len(self.times) - 1, 300)
        temperature_smooth = make_interp_spline(time_indices, self.temperatures)(time_smooth)

        # Generate the Matplotlib figure and plot
        fig, ax = plt.subplots()
        fig.set_size_inches(4, 2)

        # Plot the temperature line
        ax.plot(time_smooth, temperature_smooth, color='gold', linewidth=2)

        # Positive region fill 
        ax.fill_between(
            time_smooth, temperature_smooth, min(self.temperatures),
            where=(temperature_smooth >= 0),
            interpolate=True,
            color='gold', alpha=0.3
)

        # Negative region fill 
        ax.fill_between(
            time_smooth, temperature_smooth, min(self.temperatures),
            where=(temperature_smooth < 0),
            interpolate=True,
            color='gold', 
            alpha=0.3
)



        # Customize the axes
        ax.set_xticks(time_indices)
        ax.set_xticklabels(self.times, rotation=45, ha='right')
        
        # Set y-axis ticks and labels with all unique integer temperatures
        min_temp = int(np.floor(min(self.temperatures)))
        max_temp = int(np.ceil(max(self.temperatures)))
        
        if (max_temp - min_temp) >= 12:
            y_ticks = range(min_temp, max_temp + 1, 3)  
        elif (max_temp - min_temp) >= 6:
            y_ticks = range(min_temp, max_temp + 1, 2) 
        else:
            y_ticks = range(min_temp, max_temp + 1)    
        
        
        ax.set_yticks(y_ticks)
        ax.set_yticklabels([f"{t}°" for t in y_ticks])

        ax.grid(False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.xticks(rotation=0)
    
        ax.set_facecolor(self.bg_color_conf)
        fig.patch.set_facecolor(self.bg_color_conf)
        
        # Remove extra space around the plot
        fig.tight_layout()
        ax.title.set_color('white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.tick_params(axis='both', colors='white')

        # Attach the Matplotlib figure to the CTk window using FigureCanvasTkAgg
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)



    def graph_data(self, forecast_data):
        self.times = []
        self.temps_celsius = []
        self.temps_fahrenheit = []

        for entry in forecast_data['list'][:8]:  # Get the first 8 entries (24 hours)
            forecast_time = datetime.fromtimestamp(entry['dt'])  # Convert timestamp to datetime
            temp_celsius = entry['main']['temp']  # Temperature in Celsius
            temp_fahrenheit = temp_celsius * 9/5 + 32  # Convert to Fahrenheit

            # Adjust time format based on the locale
            if self.settings['language'] == 'Deutsch' or self.settings['language'] == 'Español' :  # German locale (24-hour format)
                formatted_time = forecast_time.strftime("%H")  # 24-hour clock
            else:  # Default to 12-hour clock with AM/PM
                formatted_time = forecast_time.strftime("%I %p").lstrip('0')

            # Format temperatures
            formatted_temp_c = f"{temp_celsius:.0f}C"  # Celsius temperature
            formatted_temp_f = f"{temp_fahrenheit:.0f}F"  # Fahrenheit temperature

            self.times.append(formatted_time)
            self.temps_celsius.append(formatted_temp_c)
            self.temps_fahrenheit.append(formatted_temp_f)




