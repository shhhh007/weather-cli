# Weather CLI ⛅

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

Console weather utility in Python — my second learning project.
Fetches a forecast from the free [Open-Meteo API](https://open-meteo.com) and prints it nicely to the terminal.

> Built evening by evening, one small step at a time. See the roadmap below.

## Roadmap

- [x] Evening 1 — first HTTP request with `requests`, print raw JSON
- [x] Evening 2 — parse the JSON: temperature, wind, weather codes
- [x] Evening 3 — city name → coordinates via the geocoding API
- [x] Evening 4 — pretty formatted output for several days
- [x] Evening 5 — error handling: city not found, no network
- [x] Evening 6 — command-line arguments, final polish
- [x] Evening 7 — README demo section, tests, release

## Usage

```text
$ python weather.py
🌤️ Погода в городе Frankfurt am Main
🌡️ Температура: 21.6 °C
💨 Ветер:       8.0 км/ч
🌤️ Состояние:   малооблачно

Прогноз на 3 дня:
  2026-08-29 🌤️  15.0 / 22.0 °C малооблачно
  2026-08-30 ⛅  14.0 / 20.0 °C переменная облачность
  2026-08-31 ☀️  13.0 / 19.0 °C ясно
```

You can also pass a city name:

```text
$ python weather.py Berlin
```

If the city can't be found or there's no network connection, the tool prints
a clear error message and exits with a non-zero status code instead of
crashing.

Requires the `requests` library: `pip install requests`.
Data by the free [Open-Meteo API](https://open-meteo.com) — no API key needed.

## Tests

The project has a small `pytest` suite that mocks all HTTP calls, so it runs
fully offline:

```text
pip install pytest
pytest
```

## License

MIT
