import requests

class WeatherAPI:
    """
    Handles communication with the Open-Meteo weather API.
    Fetches weather data for a given latitude and longitude.
    Includes error handling for API requests.
    """

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def fetch_weather_data(self):
        """
        Fetches weather data from the Open-Meteo API.

        Raises:
            Exception: If the API request fails or the response is invalid.

        Returns:
            dict: The parsed JSON weather data.
        """
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,showers,snowfall,weather_code,wind_speed_10m",
            "hourly": "temperature_2m,precipitation_probability,weather_code",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset,precipitation_sum,wind_speed_10m_max",
            "timezone": "auto"
        }
        try:
            response = requests.get(WeatherAPI.BASE_URL, params=params)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch weather data: {e}")
        except ValueError as e:
            raise Exception(f"Failed to decode weather data: {e}. Response was {response.text}")



class WeatherReport:
    """
    Interprets raw weather data from the WeatherAPI and presents it
    in a user-friendly format.
    """

    def __init__(self, latitude, longitude):
        self.api = WeatherAPI(latitude, longitude)
        self.weather_data = None

    def _get_weather_data(self):
        """Fetches weather data if not already loaded."""
        if self.weather_data is None:
            try:
                self.weather_data = self.api.fetch_weather_data()
            except Exception as e:
                print(f"Error: {e}") #Consistent error output
                self.weather_data = {} #prevent further errors.
        return self.weather_data

    def _get_weather_description(self, weather_code):
        """Translates the WMO weather code into a human-readable description."""
        weather_codes = {
              0: "Clear sky",
              1: "Mainly clear",
              2: "Partly cloudy",
              3: "Overcast",
              45: "Fog",
              48: "Depositing rime fog",
              51: "Drizzle: Light intensity",
              53: "Drizzle: Moderate intensity",
              55: "Drizzle: Dense intensity",
              56: "Freezing Drizzle: Light intensity",
              57: "Freezing Drizzle: Dense intensity",
              61: "Rain: Slight intensity",
              63: "Rain: Moderate intensity",
              65: "Rain: Heavy intensity",
              66: "Freezing Rain: Light intensity",
              67: "Freezing Rain: Heavy intensity",
              71: "Snow fall: Slight intensity",
              73: "Snow fall: Moderate intensity",
              75: "Snow fall: Heavy intensity",
              77: "Snow grains",
              80: "Rain showers: Slight intensity",
              81: "Rain showers: Moderate intensity",
              82: "Rain showers: Violent intensity",
              85: "Snow showers slight",
              86: "Snow showers heavy",
              95: "Thunderstorm: Slight or moderate",
              96: "Thunderstorm with slight hail",
              99: "Thunderstorm with heavy hail",
          }
        return weather_codes.get(weather_code, "Unknown weather code")

    def current_conditions(self):
        """Prints the current weather conditions."""
        data = self._get_weather_data()
        if not data: #Check if data is valid
            return

        current = data.get("current")
        daily = data.get("daily")
        if not current or not daily: #Check existence
            print("Error: Could not retrieve current or daily weather data.")
            return

        description = self._get_weather_description(current.get("weather_code"))

        print("Current Weather Conditions:")
        print(f"  Temperature: {current.get('temperature_2m', 'N/A')}°C")
        print(f"  Feels Like: {current.get('apparent_temperature', 'N/A')}°C")
        print(f"  Humidity: {current.get('relative_humidity_2m', 'N/A')}%")
        print(f"  Wind Speed: {current.get('wind_speed_10m', 'N/A')} km/h")
        print(f"  Condition: {description}")
        print(f"  Daily Max Temp: {daily.get('temperature_2m_max', ['N/A'])[0]}°C")
        print(f"  Daily Min Temp: {daily.get('temperature_2m_min', ['N/A'])[0]}°C")
        print(f"  Sunrise: {daily.get('sunrise', ['N/A'])[0]}")
        print(f"  Sunset: {daily.get('sunset', ['N/A'])[0]}")
        print(f"  Total Daily Precipitation: {daily.get('precipitation_sum', ['N/A'])[0]}")


    def hourly_forecast(self, hours=12):
        """Prints an hourly forecast."""
        data = self._get_weather_data()
        if not data:  # Check if data is valid
            return
        hourly_data = data.get("hourly")

        if not hourly_data:
             print("Error: Could not retrieve hourly weather data.")
             return


        print(f"\nHourly Forecast (next {hours} hours):")
        for i in range(hours):
            try:
                time = hourly_data["time"][i]
                temp = hourly_data["temperature_2m"][i]
                precip_prob = hourly_data["precipitation_probability"][i]
                weather_desc = self._get_weather_description(hourly_data["weather_code"][i])
                print(f"  {time}: Temp: {temp}°C,  Precipitation Chance: {precip_prob}%, Condition: {weather_desc}")
            except (KeyError, IndexError) as e:
                print(f"Error parsing hourly data at index {i}: {e}")
                break #Stop printing on error


    def daily_forecast(self, days=7):
      """Prints a daily forecast."""
      data = self._get_weather_data()
      if not data:  # Check if data is valid
        return

      daily_data = data.get("daily")

      if not daily_data:
          print("Error: Could not retrieve daily weather data")
          return

      print(f"\nDaily Forecast (next {days} days):")

      for i in range(days):
        try:
            date_str = daily_data["time"][i]
            max_temp = daily_data["temperature_2m_max"][i]
            min_temp = daily_data["temperature_2m_min"][i]
            weather_desc = self._get_weather_description(daily_data["weather_code"][i])
            print(f"  {date_str}: High: {max_temp}°C, Low: {min_temp}°C, Condition: {weather_desc}")
        except (KeyError, IndexError) as e:
            print(f"Error parsing daily data at index {i}: {e}")
            break


def main():
    latitude = 	53.792366  # Example: New York City
    longitude = -3.055482
    report = WeatherReport(latitude, longitude)
    report.current_conditions()
    report.hourly_forecast(6)
    report.daily_forecast(3)

if __name__ == "__main__":
    main()