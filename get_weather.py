# get_weather.py
import requests
from datetime import datetime, timedelta

def calculate_windchill(temperature_c, wind_speed_kmh):
    """Calculate windchill (°C) given temperature (°C) and wind speed (km/h)."""
    if temperature_c <= 10 and wind_speed_kmh > 4.8:
        wc = 13.12 + 0.6215 * temperature_c - 11.37 * (wind_speed_kmh ** 0.16) + 0.3965 * temperature_c * (wind_speed_kmh ** 0.16)
        return round(wc, 1)
    return temperature_c

def get_weather_info(latitude=54, longitude=10):
    """
    Fetch current weather and next 24h hourly forecast from MET Norway API.
    
    Returns a dictionary:
    - current_time: HH:MM
    - current_weather: dict with temperature, windchill, wind_speed, humidity, cloudiness, precipitation
    - hourly_forecast: list of dicts with time, temperature, wind_speed, cloudiness, precipitation
    """
    now = datetime.now()
    url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={latitude}&lon={longitude}"
    headers = {"User-Agent": "Abfahrtsmonitor/1.0"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    data = r.json()

    # Current weather
    current_data = data["properties"]["timeseries"][0]["data"]["instant"]["details"]
    current_next1h = data["properties"]["timeseries"][0]["data"].get("next_1_hours", {}).get("details", {})
    
    temp_c = current_data["air_temperature"]
    wind_kmh = current_data["wind_speed"] * 3.6  # m/s -> km/h
    cloudiness = current_data.get("cloud_area_fraction", None)
    precipitation = current_next1h.get("precipitation_amount", 0)

    current_weather = {
        "temperature": temp_c,
        "windchill": calculate_windchill(temp_c, wind_kmh),
        "wind_speed": round(wind_kmh, 1),
        "humidity": current_data.get("humidity", None),
        "cloudiness": cloudiness,
        "precipitation_mm": precipitation
    }

    # Hourly forecast (next 24h)
    hourly_forecast = []
    for entry in data["properties"]["timeseries"][:24]:
        ts = entry["time"]
        details = entry["data"]["instant"]["details"]
        next1h = entry["data"].get("next_1_hours", {}).get("details", {})
        
        hourly_forecast.append({
            "time": ts,
            "temperature": details["air_temperature"],
            "wind_speed": round(details["wind_speed"] * 3.6, 1),
            "cloudiness": details.get("cloud_area_fraction", None),
            "precipitation_mm": next1h.get("precipitation_amount", 0)
        })

    return {
        "current_time": now.strftime("%H:%M"),
        "current_weather": current_weather,
        "hourly_forecast": hourly_forecast
    }
