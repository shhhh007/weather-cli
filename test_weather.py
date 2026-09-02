import weather

class FakeResponse:

    def __init__(self, data, status_code=200):
        self.data = data
        self.status_code = status_code

    def json(self):
        return self.data

def test_find_city_success(monkeypatch):
    fake_data = {
        "results": [
            {
                "name": "Berlin",
                "country": "Germany",
                "latitude": 52.52,
                "longitude": 13.41,
            }
        ]
    }

    def fake_get(url, params, timeout):
        return FakeResponse(fake_data)

    monkeypatch.setattr(weather.requests, "get", fake_get)

    city_info = weather.find_city("Berlin")

    assert city_info["name"] == "Berlin"
    assert city_info["country"] == "Germany"
    assert city_info["latitude"] == 52.52

def test_find_city_not_found(monkeypatch):
    def fake_get(url, params, timeout):
        return FakeResponse({"results": []})

    monkeypatch.setattr(weather.requests, "get", fake_get)

    city_info = weather.find_city("Несуществующийгород123")

    assert city_info is None

def test_find_city_no_internet(monkeypatch, capsys):
    def fake_get(url, params, timeout):
        raise weather.requests.exceptions.RequestException()

    monkeypatch.setattr(weather.requests, "get", fake_get)

    city_info = weather.find_city("Berlin")

    assert city_info is None
    printed = capsys.readouterr().out
    assert "интернет" in printed

def test_get_weather_success(monkeypatch):
    fake_data = {
        "current": {
            "temperature_2m": 20.0,
            "wind_speed_10m": 5.0,
            "weather_code": 0,
        },
        "daily": {
            "time": ["2026-08-29"],
            "weather_code": [0],
            "temperature_2m_max": [22.0],
            "temperature_2m_min": [15.0],
        },
    }

    def fake_get(url, params, timeout):
        return FakeResponse(fake_data)

    monkeypatch.setattr(weather.requests, "get", fake_get)

    result = weather.get_weather(52.52, 13.41)

    assert result["current"]["temperature_2m"] == 20.0

def test_get_weather_no_internet(monkeypatch):
    def fake_get(url, params, timeout):
        raise weather.requests.exceptions.RequestException()

    monkeypatch.setattr(weather.requests, "get", fake_get)

    result = weather.get_weather(52.52, 13.41)

    assert result is None

def test_print_weather(capsys):
    city_info = {
        "name": "Berlin",
        "country": "Germany",
        "latitude": 52.52,
        "longitude": 13.41,
    }

    weather_data = {
        "current": {
            "temperature_2m": 20.0,
            "wind_speed_10m": 5.0,
            "weather_code": 0,
        },
        "daily": {
            "time": ["2026-08-29"],
            "weather_code": [0],
            "temperature_2m_max": [22.0],
            "temperature_2m_min": [15.0],
        },
    }

    weather.print_weather(city_info, weather_data)

    printed = capsys.readouterr().out
    assert "Berlin, Germany" in printed
    assert "20.0" in printed
    assert "Прогноз на 3 дня" in printed

def test_main_city_not_found(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["weather.py", "Несуществующийгород123"])
    monkeypatch.setattr(weather, "find_city", lambda name: None)

    try:
        weather.main()
    except SystemExit as e:
        assert e.code == 1

    printed = capsys.readouterr().out
    assert "не найден" in printed
