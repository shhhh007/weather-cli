import sys

import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

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


def get_place(city):
    """Turn a city name into coordinates. Returns (latitude, longitude, name, country) or None."""
    response = requests.get(GEOCODING_URL, params={
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json",
    })
    results = response.json().get("results")
    if not results:
        return None
    place = results[0]
    return place["latitude"], place["longitude"], place["name"], place.get("country", "")


def get_weather(latitude, longitude):
    """Fetch current weather and a 3-day forecast for the given coordinates."""
    response = requests.get(FORECAST_URL, params={
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,wind_speed_10m,weather_code",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min",
        "forecast_days": 3,
        "timezone": "auto",
    })
    return response.json()


def main():
    # first command-line argument is the city, fallback: Frankfurt
    city = sys.argv[1] if len(sys.argv) > 1 else "Frankfurt"

    place = get_place(city)
    if place is None:
        print(f"City not found: {city}")
        return
    latitude, longitude, name, country = place

    data = get_weather(latitude, longitude)
    current = data["current"]

    location = f"{name}, {country}" if country else name
    code = current["weather_code"]
    icon = WEATHER_ICONS.get(code, "🌡️")

    print(f"{icon} Weather in {location}")
    print(f"🌡️ Temperature: {current['temperature_2m']} °C")
    print(f"💨 Wind:        {current['wind_speed_10m']} km/h")
    print(f"{icon} Condition:   {WEATHER_CODES.get(code, 'unknown condition')}")

    # the API returns parallel lists: dates, codes, daily max and min temperatures
    daily = data["daily"]
    print("\n3-day forecast:")
    for date, day_code, t_max, t_min in zip(
        daily["time"],
        daily["weather_code"],
        daily["temperature_2m_max"],
        daily["temperature_2m_min"],
    ):
        day_icon = WEATHER_ICONS.get(day_code, "🌡️")
        description = WEATHER_CODES.get(day_code, "")
        print(f"  {date}  {day_icon} {t_min:>5.1f} / {t_max:.1f} °C  {description}")


if __name__ == "__main__":
    main()
