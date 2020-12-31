#!/usr/bin/python3 -B
# weather.py

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import json
import requests
from config import IFTTT_WEBHOOK, LOCATION, OPENWEATHERMAP_API_KEY


# Send weather data
response = requests.get('http://api.openweathermap.org/data/2.5/weather?q={location}&appid={openweathermap_api_key}'.format(location=LOCATION, openweathermap_api_key=OPENWEATHERMAP_API_KEY))
if response.status_code == 200:
    json_obj = json.loads(response.content)
    weather = json_obj['weather'][0]['main']
    temperature = (json_obj['main']['temp'] - 273.15) * 9 / 5 + 32
    requests.post(IFTTT_WEBHOOK, json={'value1': '{location} Weather'.format(location=LOCATION.split(',')[0]), 'value2': '{temperature:.0f} °F — {weather}'.format(temperature=temperature, weather=weather), 'value3': 'https://www.google.com/search?q={location}+weather'.format(location=LOCATION.replace(' ', '+'))})
