# utils/weather_utils.py
import os
from datetime import datetime, timedelta
from pyowm.owm import OWM
from dotenv import load_dotenv

load_dotenv()
OPENWEATHERMAP_API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY")

def get_weekend_weather(latitude, longitude):
    """
    Gets the weather forecast for the upcoming Saturday and Sunday.

    Args:
        latitude: The latitude of the location.
        longitude: The longitude of the location.

    Returns:
        A dictionary containing the weather information, or None on error.
        Example:
        {
            'Saturday': {'date': '2024-02-17', 'temperature': 65, 'description': 'Clear sky'},
            'Sunday': {'date': '2024-02-18', 'temperature': 62, 'description': 'Partly cloudy'}
        }
    """
    if not OPENWEATHERMAP_API_KEY:
        print("Error: OPENWEATHERMAP_API_KEY not set in environment variables.")
        return None

    try:
        owm = OWM(OPENWEATHERMAP_API_KEY)
        mgr = owm.weather_manager()

        # --- 1. Find the next Saturday and Sunday ---
        today = datetime.now()
        days_until_saturday = (5 - today.weekday()) % 7  # Saturday is 5 (Monday is 0)
        days_until_sunday = (6 - today.weekday()) % 7

        saturday = today + timedelta(days=days_until_saturday)
        sunday = today + timedelta(days=days_until_sunday)
        saturday_str = saturday.strftime('%Y-%m-%d')  # Format as YYYY-MM-DD
        sunday_str = sunday.strftime('%Y-%m-%d')

        # --- 2. Get the forecast ---
        # Use one_call for daily forecast (more reliable for specific dates)
        one_call = mgr.one_call(lat=latitude, lon=longitude)
        daily_forecast = one_call.forecast_daily

        # --- 3. Extract Relevant Data ---
        weather_data = {}
        for forecast in daily_forecast:
            forecast_date = datetime.fromtimestamp(forecast.reference_time('unix')).strftime('%Y-%m-%d')

            if forecast_date == saturday_str:
                weather_data['Saturday'] = {
                    'date': saturday_str,
                    'temperature': int(round(forecast.temperature('fahrenheit')['day'])),  # Daily temp
                    'description': forecast.detailed_status
                }
            elif forecast_date == sunday_str:
                weather_data['Sunday'] = {
                    'date': sunday_str,
                    'temperature': int(round(forecast.temperature('fahrenheit')['day'])),  # Daily temp
                    'description': forecast.detailed_status
                }

        return weather_data

    except Exception as e:
        print(f"Error getting weather: {type(e).__name__}: {e}")
        return None


if __name__ == '__main__':
    # Example Usage (San Francisco)
    latitude = 37.7749
    longitude = -122.4194
    weather = get_weekend_weather(latitude, longitude)
    if weather:
        print(f"Weekend Weather for lat={latitude}, lon={longitude}:")
        for day, data in weather.items():
            print(f"  {day}: {data['date']}, {data['temperature']}°F, {data['description']}")
    else:
        print("Could not retrieve weather information.")