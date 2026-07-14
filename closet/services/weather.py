import requests
import streamlit as st

LAHORE_LAT = 31.5497
LAHORE_LON = 74.3436

WMO_CONDITIONS = {
    0: ("Clear", "☀️"),
    1: ("Mostly Clear", "🌤️"),
    2: ("Partly Cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Foggy", "🌫️"), 48: ("Foggy", "🌫️"),
    51: ("Light Drizzle", "🌦️"), 53: ("Drizzle", "🌦️"), 55: ("Heavy Drizzle", "🌧️"),
    56: ("Freezing Drizzle", "🌧️"), 57: ("Freezing Drizzle", "🌧️"),
    61: ("Light Rain", "🌦️"), 63: ("Rain", "🌧️"), 65: ("Heavy Rain", "🌧️"),
    66: ("Freezing Rain", "🌧️"), 67: ("Freezing Rain", "🌧️"),
    71: ("Light Snow", "🌨️"), 73: ("Snow", "🌨️"), 75: ("Heavy Snow", "❄️"),
    77: ("Snow Grains", "🌨️"),
    80: ("Rain Showers", "🌦️"), 81: ("Rain Showers", "🌧️"), 82: ("Violent Showers", "⛈️"),
    85: ("Snow Showers", "🌨️"), 86: ("Snow Showers", "🌨️"),
    95: ("Thunderstorm", "⛈️"), 96: ("Thunderstorm", "⛈️"), 99: ("Thunderstorm", "⛈️"),
}
RAINY_CODES = {51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82, 95, 96, 99}

@st.cache_data(ttl=600)  
def get_current_weather(lat=LAHORE_LAT, lon=LAHORE_LON):
    try:
        resp = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current_weather": "true",
                "timezone": "auto",
            },
            timeout=5,
        )
        resp.raise_for_status()
        current = resp.json()["current_weather"]
        code = current.get("weathercode", 0)
        condition, icon = WMO_CONDITIONS.get(code, ("Unknown", "🌡️"))
        return {
            "temp_c": current["temperature"],
            "condition": condition,
            "icon": icon,
            "is_rainy": code in RAINY_CODES,
        }
    except Exception:
        return None