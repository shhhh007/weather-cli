
import sys
import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    0: "ясно",
    1: "малооблачно",
    2: "переменная облачность",
    3: "пасмурно",
    45: "туман",
    48: "туман с изморозью",
    51: "лёгкая морось",
    53: "морось",
    55: "сильная морось",
    61: "небольшой дождь",
    63: "дождь",
    65: "сильный дождь",
    71: "небольшой снег",
    73: "снег",
    75: "сильный снег",
    80: "ливень",
    81: "сильный ливень",
    82: "очень сильный ливень",
    95: "гроза",
    96: "гроза с градом",
    99: "сильная гроза с градом",
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

def find_city(city_name):
    params = {
        "name": city_name,
        "count": 1,
        "language": "ru",
        "format": "json",
    }

    try:
        response = requests.get(GEOCODING_URL, params=params, timeout=10)
    except requests.exceptions.RequestException:
        print("Ошибка: нет подключения к интернету.")
        return None

    if response.status_code != 200:
        print("Ошибка: сервис погоды сейчас недоступен.")
        return None

    data = response.json()
    results = data.get("results")

    if not results:
        return None

    first_result = results[0]

    city_info = {
        "name": first_result.get("name", city_name),
        "country": first_result.get("country", ""),
        "latitude": first_result["latitude"],
        "longitude": first_result["longitude"],
    }

    return city_info

def get_weather(latitude, longitude):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,wind_speed_10m,weather_code",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min",
        "forecast_days": 3,
        "timezone": "auto",
    }

    try:
        response = requests.get(FORECAST_URL, params=params, timeout=10)
    except requests.exceptions.RequestException:
        print("Ошибка: нет подключения к интернету.")
        return None

    if response.status_code != 200:
        print("Ошибка: сервис погоды сейчас недоступен.")
        return None

    return response.json()

def print_weather(city_info, weather_data):
    city_name = city_info["name"]
    country = city_info["country"]

    if country:
        location = city_name + ", " + country
    else:
        location = city_name

    current = weather_data["current"]
    code = current["weather_code"]
    icon = WEATHER_ICONS.get(code, "🌡️")
    condition = WEATHER_CODES.get(code, "неизвестно")

    print(icon + " Погода в городе " + location)
    print("🌡️ Температура: " + str(current["temperature_2m"]) + " °C")
    print("💨 Ветер:       " + str(current["wind_speed_10m"]) + " км/ч")
    print(icon + " Состояние:   " + condition)

    print("")
    print("Прогноз на 3 дня:")

    daily = weather_data["daily"]
    dates = daily["time"]
    codes = daily["weather_code"]
    max_temps = daily["temperature_2m_max"]
    min_temps = daily["temperature_2m_min"]

    for i in range(len(dates)):
        day_code = codes[i]
        day_icon = WEATHER_ICONS.get(day_code, "🌡️")
        day_condition = WEATHER_CODES.get(day_code, "неизвестно")

        print(
            "  " + dates[i] + " " + day_icon + " "
            + str(min_temps[i]) + " / " + str(max_temps[i]) + " °C "
            + day_condition
        )

def main():
    if len(sys.argv) > 1:
        city_name = sys.argv[1]
    else:
        city_name = "Frankfurt"

    city_info = find_city(city_name)

    if city_info is None:
        print("Город не найден: " + city_name)
        sys.exit(1)

    weather_data = get_weather(city_info["latitude"], city_info["longitude"])

    if weather_data is None:
        sys.exit(1)

    print_weather(city_info, weather_data)

if __name__ == "__main__":
    main()
