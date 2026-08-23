import requests

# Frankfurt am Main, Germany
URL = "https://api.open-meteo.com/v1/forecast?latitude=50.1109&longitude=8.6821&current=temperature_2m,wind_speed_10m,weather_code"

# WMO weather interpretation codes (WW): https://open-meteo.com/en/docs
WEATHER_CODES = {
    0: "clear sky",
    1: "mainly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "fog",
    48: "depositing rime fog",
    51: "light drizzle",
    53: "moderate drizzle",
    55: "dense drizzle",
    61: "slight rain",
    63: "moderate rain",
    65: "heavy rain",
    71: "slight snowfall",
    73: "moderate snowfall",
    75: "heavy snowfall",
    80: "slight rain showers",
    81: "moderate rain showers",
    82: "violent rain showers",
    95: "thunderstorm",
    96: "thunderstorm with slight hail",
    99: "thunderstorm with heavy hail",
}

# an icon for every group of weather codes
WEATHER_ICONS = {
    0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
    45: "🌫️", 48: "🌫️",
    51: "🌦️", 53: "🌦️", 55: "🌧️",
    61: "🌦️", 63: "🌧️", 65: "🌧️",
    71: "🌨️", 73: "🌨️", 75: "❄️",
    80: "🌦️", 81: "🌧️", 82: "⛈️",
    95: "⛈️", 96: "⛈️", 99: "⛈️",
}

response = requests.get(URL)
data = response.json()

# dig into the nested dictionary: data -> "current" -> keys
current = data["current"]
temperature = current["temperature_2m"]
wind = current["wind_speed_10m"]
code = current["weather_code"]
description = WEATHER_CODES.get(code, "unknown condition")
icon = WEATHER_ICONS.get(code, "🌡️")

print(f"{icon} Weather in Frankfurt am Main")
print(f"🌡️ Temperature: {temperature} °C")
print(f"💨 Wind:        {wind} km/h")
print(f"{icon} Condition:   {description}")
