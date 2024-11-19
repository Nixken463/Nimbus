
import requests
from datetime import datetime
import customtkinter as ctk
import pytz
from io import BytesIO
from PIL import Image, ImageTk


API_KEY = "4df1ee20234521fe81b2178076612157"

TIMEZONE = pytz.timezone("Asia/Tokyo")
TIME = datetime.now(TIMEZONE)
DAY = TIME.strftime("%A")
CITY = "Tokyo"
COUNTRY = "De"
url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}"
response = requests.get(url).json()

print(response
      )