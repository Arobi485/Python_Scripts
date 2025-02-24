import customtkinter as ctk
import requests
from PIL import Image, ImageTk
import threading
from datetime import datetime, timedelta
import json
from io import BytesIO

# First, expand the UK_CITIES dictionary with some additional data
UK_CITIES = {
    "London": {"lat": 51.5074, "lon": -0.1278, "population": "8.9M"},
    "Birmingham": {"lat": 52.4862, "lon": -1.8904, "population": "2.6M"},
    "Manchester": {"lat": 53.4808, "lon": -2.2426, "population": "2.5M"},
    "Leeds": {"lat": 53.8008, "lon": -1.5491, "population": "1.8M"},
    "Sheffield": {"lat": 53.3811, "lon": -1.4701, "population": "1.4M"},
    "Liverpool": {"lat": 53.4084, "lon": -2.9916, "population": "1.4M"},
    "Bristol": {"lat": 51.4545, "lon": -2.5879, "population": "463K"},
    "Newcastle": {"lat": 54.9783, "lon": -1.6178, "population": "300K"},
    "Nottingham": {"lat": 52.9548, "lon": -1.1581, "population": "321K"},
    "Glasgow": {"lat": 55.8642, "lon": -4.2518, "population": "1.6M"},
    "Preston": {"lat": 53.7632, "lon": 2.7031, "population": "1.6M"}
}

class WeatherApp:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("UK Weather App")
        self.window.geometry("1000x800")  # Increased size to accommodate new features
        self.window.resizable(False, False)

        # Weather icons dictionary
        self.weather_icons = {
            'Clear': '☀️',
            'Clouds': '☁️',
            'Rain': '🌧️',
            'Snow': '❄️',
            'Thunderstorm': '⛈️',
            'Drizzle': '🌦️',
            'Mist': '🌫️'
        }

        # Initialize the UI
        self.setup_ui()
        
        # Initial weather fetch
        self.search_weather()

    def setup_ui(self):
        # Main layout configuration
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        # Main frame
        self.main_frame = ctk.CTkFrame(self.window, corner_radius=15)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Title
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="UK Weather Dashboard",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20,10))

        # Search frame
        self.create_search_frame()
        
        # Current weather frame
        self.create_weather_frame()
        
        # Forecast frame
        self.create_forecast_frame()
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=ctk.CTkFont(size=14),
            text_color="red"
        )
        self.status_label.grid(row=4, column=0, padx=20, pady=10)

    def create_search_frame(self):
        self.search_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.search_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.search_frame.grid_columnconfigure(0, weight=1)

        # City dropdown
        self.city_var = ctk.StringVar(value="London")
        self.city_dropdown = ctk.CTkOptionMenu(
            self.search_frame,
            values=list(UK_CITIES.keys()),
            variable=self.city_var,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.city_dropdown.grid(row=0, column=0, padx=(20,10), pady=10)

        # Search button
        self.search_button = ctk.CTkButton(
            self.search_frame,
            text="Get Weather",
            width=100,
            height=40,
            command=self.search_weather,
            font=ctk.CTkFont(size=14)
        )
        self.search_button.grid(row=0, column=1, padx=(0,20), pady=10)

    def create_weather_frame(self):
        self.weather_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.weather_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.weather_frame.grid_columnconfigure(0, weight=1)

        # City info
        self.city_label = ctk.CTkLabel(
            self.weather_frame,
            text="",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        self.city_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20,10))

        # Weather icon
        self.weather_icon_label = ctk.CTkLabel(
            self.weather_frame,
            text="",
            font=ctk.CTkFont(size=48)
        )
        self.weather_icon_label.grid(row=1, column=0, padx=20, pady=10)

        # Temperature
        self.temp_label = ctk.CTkLabel(
            self.weather_frame,
            text="",
            font=ctk.CTkFont(size=48)
        )
        self.temp_label.grid(row=1, column=1, padx=20, pady=10)

        # Description
        self.desc_label = ctk.CTkLabel(
            self.weather_frame,
            text="",
            font=ctk.CTkFont(size=18)
        )
        self.desc_label.grid(row=2, column=0, columnspan=2, padx=20, pady=10)

        # Details frame
        self.create_details_frame()

    def create_details_frame(self):
        self.details_frame = ctk.CTkFrame(self.weather_frame, corner_radius=10)
        self.details_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        # Humidity
        self.humidity_label = ctk.CTkLabel(
            self.details_frame,
            text="",
            font=ctk.CTkFont(size=14)
        )
        self.humidity_label.grid(row=0, column=0, padx=20, pady=10)

        # Wind speed
        self.wind_label = ctk.CTkLabel(
            self.details_frame,
            text="",
            font=ctk.CTkFont(size=14)
        )
        self.wind_label.grid(row=0, column=1, padx=20, pady=10)

        # Air Quality
        self.aqi_label = ctk.CTkLabel(
            self.details_frame,
            text="",
            font=ctk.CTkFont(size=14)
        )
        self.aqi_label.grid(row=0, column=2, padx=20, pady=10)

    def create_forecast_frame(self):
        self.forecast_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.forecast_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        # Title for forecast
        self.forecast_title = ctk.CTkLabel(
            self.forecast_frame,
            text="5-Day Forecast",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.forecast_title.grid(row=0, column=0, columnspan=5, pady=(10,5))

        # Create frames for each day
        self.forecast_days = []
        for i in range(5):
            day_frame = ctk.CTkFrame(self.forecast_frame, corner_radius=5)
            day_frame.grid(row=1, column=i, padx=5, pady=5, sticky="nsew")
            
            date_label = ctk.CTkLabel(day_frame, text="", font=ctk.CTkFont(size=12))
            date_label.pack(pady=2)
            
            icon_label = ctk.CTkLabel(day_frame, text="", font=ctk.CTkFont(size=24))
            icon_label.pack(pady=2)
            
            temp_label = ctk.CTkLabel(day_frame, text="", font=ctk.CTkFont(size=14))
            temp_label.pack(pady=2)
            
            self.forecast_days.append({
                'date': date_label,
                'icon': icon_label,
                'temp': temp_label
            })

    def search_weather(self):
        self.status_label.configure(text="Loading...", text_color="white")
        threading.Thread(target=self.fetch_weather_data, daemon=True).start()

    def fetch_weather_data(self):
        try:
            city = self.city_var.get()
            api_key = '1ad433e880dbb2cc42b658e772fef8f9'  # Replace with your API key
            lat = UK_CITIES[city]["lat"]
            lon = UK_CITIES[city]["lon"]

            # Current weather
            weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
            weather_response = requests.get(weather_url)

            # Forecast
            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
            forecast_response = requests.get(forecast_url)

            # Air quality
            aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
            aqi_response = requests.get(aqi_url)

            if all(r.status_code == 200 for r in [weather_response, forecast_response, aqi_response]):
                weather_data = weather_response.json()
                forecast_data = forecast_response.json()
                aqi_data = aqi_response.json()
                
                self.update_weather_info(weather_data, forecast_data, aqi_data)
            else:
                self.window.after(0, lambda: self.status_label.configure(
                    text="Error fetching weather data",
                    text_color="red"
                ))

        except Exception as e:
            self.window.after(0, lambda: self.status_label.configure(
                text=f"Error: {str(e)}",
                text_color="red"
            ))

    def update_weather_info(self, weather_data, forecast_data, aqi_data):
        def update():
            # Clear status
            self.status_label.configure(text="")
            
            # Update current weather
            city = self.city_var.get()
            self.city_label.configure(text=f"{city}, UK")
            self.temp_label.configure(text=f"{round(weather_data['main']['temp'])}°C")
            
            weather_main = weather_data['weather'][0]['main']
            self.weather_icon_label.configure(
                text=self.weather_icons.get(weather_main, '❓')
            )
            
            self.desc_label.configure(
                text=weather_data['weather'][0]['description'].capitalize()
            )
            
            self.humidity_label.configure(
                text=f"Humidity: {weather_data['main']['humidity']}%"
            )
            
            self.wind_label.configure(
                text=f"Wind: {round(weather_data['wind']['speed'] * 3.6, 1)} km/h"
            )

            # Update air quality
            aqi = aqi_data['list'][0]['main']['aqi']
            aqi_levels = {
                1: ("Good", "green"),
                2: ("Fair", "yellow"),
                3: ("Moderate", "orange"),
                4: ("Poor", "red"),
                5: ("Very Poor", "purple")
            }
            level, color = aqi_levels[aqi]
            self.aqi_label.configure(
                text=f"Air Quality: {level}",
                text_color=color
            )

            # Update forecast
            for i, day_data in enumerate(forecast_data['list'][::8][:5]):
                date = datetime.fromtimestamp(day_data['dt']).strftime('%a')
                temp = round(day_data['main']['temp'])
                weather_main = day_data['weather'][0]['main']
                
                self.forecast_days[i]['date'].configure(text=date)
                self.forecast_days[i]['icon'].configure(
                    text=self.weather_icons.get(weather_main, '❓')
                )
                self.forecast_days[i]['temp'].configure(text=f"{temp}°C")

        self.window.after(0, update)

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = WeatherApp()
    app.run()