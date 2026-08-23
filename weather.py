import requests

URL = "https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.405&current=temperature_2m,wind_speed_10m"

response = requests.get(URL)
data = response.json()
print(data)
