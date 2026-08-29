"""Tests for weather.py."""

from __future__ import annotations

import requests

import weather


class FakeResponse:
    """Minimal stand-in for requests.Response."""

    def __init__(self, json_data, status_code=200):
        self._json_data = json_data
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        return self._json_data


# ---------------------------------------------------------------------------
# request_json
# ---------------------------------------------------------------------------


def test_request_json_returns_data(monkeypatch):
    monkeypatch.setattr(
        weather.requests,
        "get",
        lambda *a, **k: FakeResponse({"ok": True}),
    )

    result = weather.request_json("http://example.test", {})

    assert result == {"ok": True}


def test_request_json_network_error(monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.ConnectionError("no network")

    monkeypatch.setattr(weather.requests, "get", fake_get)

    try:
        weather.request_json("http://example.test", {})
        assert False, "expected WeatherError"
    except weather.WeatherError as error:
        assert "Network error" in str(error)


def test_request_json_invalid_json(monkeypatch):
    class BadJsonResponse(FakeResponse):
        def json(self):
            raise ValueError("bad json")

    monkeypatch.setattr(
        weather.requests,
        "get",
        lambda *a, **k: BadJsonResponse(None),
    )

    try:
        weather.request_json("http://example.test", {})
        assert False, "expected WeatherError"
    except weather.WeatherError as error:
        assert "invalid data" in str(error)


def test_request_json_non_dict_response(monkeypatch):
    monkeypatch.setattr(
        weather.requests,
        "get",
        lambda *a, **k: FakeResponse([1, 2, 3]),
    )

    try:
        weather.request_json("http://example.test", {})
        assert False, "expected WeatherError"
    except weather.WeatherError as error:
        assert "invalid response" in str(error)


# ---------------------------------------------------------------------------
# get_place
# ---------------------------------------------------------------------------


def test_get_place_found(monkeypatch):
    monkeypatch.setattr(
        weather,
        "request_json",
        lambda url, params: {
            "results": [
                {
                    "latitude": 50.1109,
                    "longitude": 8.6821,
                    "name": "Frankfurt am Main",
                    "country": "Germany",
                }
            ]
        },
    )

    place = weather.get_place("Frankfurt")

    assert place == (50.1109, 8.6821, "Frankfurt am Main", "Germany")


def test_get_place_not_found(monkeypatch):
    monkeypatch.setattr(
        weather,
        "request_json",
        lambda url, params: {"results": []},
    )

    assert weather.get_place("Nonexistentcityxyz") is None


def test_get_place_missing_country(monkeypatch):
    monkeypatch.setattr(
        weather,
        "request_json",
        lambda url, params: {
            "results": [
                {
                    "latitude": 1.0,
                    "longitude": 2.0,
                    "name": "Somewhere",
                }
            ]
        },
    )

    place = weather.get_place("Somewhere")

    assert place == (1.0, 2.0, "Somewhere", "")


def test_get_place_invalid_data(monkeypatch):
    monkeypatch.setattr(
        weather,
        "request_json",
        lambda url, params: {"results": [{"latitude": "not-a-number"}]},
    )

    try:
        weather.get_place("Weiskirchen")
        assert False, "expected WeatherError"
    except weather.WeatherError as error:
        assert "location data" in str(error)


# ---------------------------------------------------------------------------
# get_weather
# ---------------------------------------------------------------------------


def test_get_weather_passes_coordinates(monkeypatch):
    captured = {}

    def fake_request_json(url, params):
        captured["url"] = url
        captured["params"] = params
        return {"current": {}, "daily": {}}

    monkeypatch.setattr(weather, "request_json", fake_request_json)

    weather.get_weather(50.11, 8.68)

    assert captured["url"] == weather.FORECAST_URL
    assert captured["params"]["latitude"] == 50.11
    assert captured["params"]["longitude"] == 8.68
    assert captured["params"]["forecast_days"] == 3


# ---------------------------------------------------------------------------
# print_weather
# ---------------------------------------------------------------------------


def test_print_weather_output(capsys):
    place = (50.11, 8.68, "Frankfurt am Main", "Germany")
    data = {
        "current": {
            "temperature_2m": 21.6,
            "wind_speed_10m": 8.0,
            "weather_code": 1,
        },
        "daily": {
            "time": ["2026-08-29"],
            "weather_code": [1],
            "temperature_2m_max": [22.0],
            "temperature_2m_min": [15.0],
        },
    }

    weather.print_weather(place, data)

    output = capsys.readouterr().out
    assert "Frankfurt am Main, Germany" in output
    assert "21.6" in output
    assert "3-day forecast" in output


def test_print_weather_incomplete_current_data():
    place = (0.0, 0.0, "Nowhere", "")
    data = {"current": {}, "daily": {}}

    try:
        weather.print_weather(place, data)
        assert False, "expected WeatherError"
    except weather.WeatherError as error:
        assert "weather data" in str(error)


# ---------------------------------------------------------------------------
# parse_args
# ---------------------------------------------------------------------------


def test_parse_args_default(monkeypatch):
    monkeypatch.setattr("sys.argv", ["weather.py"])

    args = weather.parse_args()

    assert args.city == "Frankfurt"


def test_parse_args_custom_city(monkeypatch):
    monkeypatch.setattr("sys.argv", ["weather.py", "Berlin"])

    args = weather.parse_args()

    assert args.city == "Berlin"


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def test_main_success(monkeypatch):
    monkeypatch.setattr("sys.argv", ["weather.py", "Frankfurt"])
    monkeypatch.setattr(
        weather,
        "get_place",
        lambda city: (50.11, 8.68, "Frankfurt am Main", "Germany"),
    )
    monkeypatch.setattr(
        weather,
        "get_weather",
        lambda lat, lon: {
            "current": {
                "temperature_2m": 20.0,
                "wind_speed_10m": 5.0,
                "weather_code": 0,
            },
            "daily": {
                "time": ["2026-08-29"],
                "weather_code": [0],
                "temperature_2m_max": [21.0],
                "temperature_2m_min": [14.0],
            },
        },
    )

    assert weather.main() == 0


def test_main_city_not_found(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["weather.py", "Nonexistentcityxyz"])
    monkeypatch.setattr(weather, "get_place", lambda city: None)

    exit_code = weather.main()

    assert exit_code == 1
    assert "City not found" in capsys.readouterr().err


def test_main_handles_weather_error(monkeypatch, capsys):
    def raise_error(city):
        raise weather.WeatherError("Network error. Check your internet connection.")

    monkeypatch.setattr("sys.argv", ["weather.py", "Frankfurt"])
    monkeypatch.setattr(weather, "get_place", raise_error)

    exit_code = weather.main()

    assert exit_code == 1
    assert "Error:" in capsys.readouterr().err
