"""Console weather utility using the Open-Meteo API."""

from __future__ import annotations

import argparse
import sys
from typing import Any

import requests


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
REQUEST_TIMEOUT = 10


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


WEATHER_ICONS = {
    0: "☀️",
    1: "🌤️",
    2: "⛅",
    3: "☁️",
    45: "🌫️",
    48: "🌫️",
    51: "🌦️",
    53: "🌦️",
    55: "🌧️",
    61: "🌦️",
    63: "🌧️",
    65: "🌧️",
    71: "🌨️",
    73: "🌨️",
    75: "❄️",
    80: "🌦️",
    81: "🌧️",
    82: "⛈️",
    95: "⛈️",
    96: "⛈️",
    99: "⛈️",
}


class WeatherError(Exception):
    """Expected application error."""


def request_json(
    url: str,
    params: dict[str, Any],
) -> dict[str, Any]:
    """Perform an HTTP request and return a JSON object."""
    try:
        response = requests.get(
            url,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()

    except requests.RequestException as error:
        raise WeatherError(
            "Network error. Check your internet connection."
        ) from error

    except ValueError as error:
        raise WeatherError(
            "The weather service returned invalid data."
        ) from error

    if not isinstance(data, dict):
        raise WeatherError(
            "The weather service returned an invalid response."
        )

    return data


def get_place(city: str) -> tuple[float, float, str, str] | None:
    """Convert a city name into coordinates."""
    data = request_json(
        GEOCODING_URL,
        {
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json",
        },
    )

    results = data.get("results", [])

    if not results:
        return None

    place = results[0]

    try:
        return (
            float(place["latitude"]),
            float(place["longitude"]),
            str(place["name"]),
            str(place.get("country", "")),
        )

    except (KeyError, TypeError, ValueError) as error:
        raise WeatherError(
            "Invalid location data received from the API."
        ) from error


def get_weather(latitude: float, longitude: float) -> dict[str, Any]:
    """Fetch current weather and a three-day forecast."""
    return request_json(
        FORECAST_URL,
        {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,"
                "wind_speed_10m,"
                "weather_code"
            ),
            "daily": (
                "weather_code,"
                "temperature_2m_max,"
                "temperature_2m_min"
            ),
            "forecast_days": 3,
            "timezone": "auto",
        },
    )


def print_weather(
    place: tuple[float, float, str, str],
    data: dict[str, Any],
) -> None:
    """Print current weather and the forecast."""
    _, _, name, country = place

    if country:
        location = f"{name}, {country}"
    else:
        location = name

    try:
        current = data["current"]
        daily = data["daily"]
        current_code = int(current["weather_code"])

    except (KeyError, TypeError, ValueError) as error:
        raise WeatherError(
            "Incomplete weather data received from the API."
        ) from error

    icon = WEATHER_ICONS.get(current_code, "🌡️")
    condition = WEATHER_CODES.get(
        current_code,
        "unknown condition",
    )

    print(f"{icon} Weather in {location}")
    print(f"🌡️ Temperature: {current['temperature_2m']} °C")
    print(f"💨 Wind:        {current['wind_speed_10m']} km/h")
    print(f"{icon} Condition:   {condition}")

    print("\n3-day forecast:")

    try:
        forecast_rows = zip(
            daily["time"],
            daily["weather_code"],
            daily["temperature_2m_max"],
            daily["temperature_2m_min"],
        )

        for date, code, temperature_max, temperature_min in forecast_rows:
            code = int(code)

            day_icon = WEATHER_ICONS.get(code, "🌡️")
            description = WEATHER_CODES.get(
                code,
                "unknown condition",
            )

            print(
                f"  {date} {day_icon} "
                f"{float(temperature_min):>5.1f} / "
                f"{float(temperature_max):.1f} °C "
                f"{description}"
            )

    except (KeyError, TypeError, ValueError) as error:
        raise WeatherError(
            "Incomplete forecast data received from the API."
        ) from error


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Show the current weather and "
            "a three-day forecast."
        ),
    )

    parser.add_argument(
        "city",
        nargs="?",
        default="Frankfurt",
        help="city name, for example: Berlin",
    )

    return parser.parse_args()


def main() -> int:
    """Run the application."""
    args = parse_args()

    try:
        place = get_place(args.city)

        if place is None:
            print(
                f"City not found: {args.city}",
                file=sys.stderr,
            )
            return 1

        weather = get_weather(
            place[0],
            place[1],
        )

        print_weather(place, weather)
        return 0

    except WeatherError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
