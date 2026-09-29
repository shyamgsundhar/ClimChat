
from datetime import datetime

import requests


class WeatherClient:
    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, settings):
        self.settings = settings
        self.session = requests.Session()

    def fetch(self, city) -> dict:
        params = {
            "latitude": city.latitude,
            "longitude": city.longitude,
            "current": (
                "temperature_2m,relative_humidity_2m,"
                "apparent_temperature,precipitation,"
                "weather_code,wind_speed_10m"
            ),
            "hourly": (
                "precipitation_probability,precipitation,"
                "temperature_2m"
            ),
            "forecast_days": 2,
            "timezone": self.settings.timezone,
        }

        response = self.session.get(
            self.BASE_URL,
            params=params,
            timeout=self.settings.request_timeout,
        )
        response.raise_for_status()

        payload = response.json()
        current = payload.get("current", {})
        hourly = payload.get("hourly", {})

        times = hourly.get("time", [])
        rain_values = hourly.get("precipitation", [])
        probability_values = hourly.get("precipitation_probability", [])
        temperature_values = hourly.get("temperature_2m", [])

        current_time = current.get("time")
        start_index = 0

        if current_time and times:
            for index, time_value in enumerate(times):
                if time_value >= current_time:
                    start_index = index
                    break

        end_index = min(start_index + 6, len(times))

        rain_slice = rain_values[start_index:end_index]
        probability_slice = probability_values[start_index:end_index]
        temperature_slice = temperature_values[start_index:end_index]

        return {
            "city": city.name,
            "latitude": city.latitude,
            "longitude": city.longitude,
            "temperature_c": current.get("temperature_2m"),
            "feels_like_c": current.get("apparent_temperature"),
            "humidity_percent": current.get("relative_humidity_2m"),
            "precipitation_mm": current.get("precipitation"),
            "wind_kmh": current.get("wind_speed_10m"),
            "weather_code": current.get("weather_code"),
            "current_time": current_time,
            "next_6h_rain_mm": sum(
                float(value or 0) for value in rain_slice
            ),
            "next_6h_rain_probability_max": max(
                (int(value or 0) for value in probability_slice),
                default=0,
            ),
            "next_6h_temperatures": temperature_slice,
            "hourly_times": times[start_index:end_index],
        }


def weather_description(code) -> str:
    descriptions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with hail",
        99: "Thunderstorm with heavy hail",
    }
    return descriptions.get(code, "Unknown condition")