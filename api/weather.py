import json

import requests
from . import redis_client

WEATHER_API_KEY = "VCB2PCPUX4GJTFWPUAM8KKCYD"


def get_weather_forecast(lat, lon):
    data = redis_client.get(f"{lat}-{lon}")
    if data:
        return json.loads(data)["data"]

    response = requests.get(f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{lat},{lon}?key={WEATHER_API_KEY}&unitGroup=metric").json()
    daily_forecast = []
    for data in response["days"]:
        daily_forecast.append([data["datetime"], data["temp"], data["feelslike"], data["humidity"], data["windspeed"], data["sunrise"], data["sunset"]])

    data = json.dumps({"data": daily_forecast})
    redis_client.set(f"{lat}-{lon}", data, ex=36000)
    return daily_forecast
