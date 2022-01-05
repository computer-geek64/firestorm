#!/usr/bin/python3 -B
# weather.py

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'util'))
import json
import requests
from life360 import life360
from config import IFTTT_WEBHOOK, LOCATION, OPENWEATHERMAP_API_KEY, LIFE360_USERNAME, LIFE360_PASSWORD


try:
    # Get current lat/lon coordinates from Life360
    life360_authorization_token = 'cFJFcXVnYWJSZXRyZTRFc3RldGhlcnVmcmVQdW1hbUV4dWNyRUh1YzptM2ZydXBSZXRSZXN3ZXJFQ2hBUHJFOTZxYWtFZHI0Vg=='
    life360_api = life360(authorization_token=life360_authorization_token, username=LIFE360_USERNAME, password=LIFE360_PASSWORD)
    if not api.authenticate():
        raise Exception('Failed to authenticate with Life360 API')

    circle = api.get_circle(api.get_circles()[0]['id'])
    life360_location = [member for member in circle['members'] if member['loginEmail'] == LIFE360_USERNAME][0]['location']
    lat, lon = life360_location['latitude'], life360_location['longitude']

    # Get weather data
    response = requests.get(f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHERMAP_API_KEY}')
    if response.status_code != 200:
        raise Exception(f'OpenWeatherMap HTTP {response.status_code}')

    json_obj = json.loads(response.text)
    weather = json_obj['weather'][0]['main']
    temperature = (json_obj['main']['temp'] - 273.15) * 9 / 5 + 32
    
    # Send weather data to IFTTT push notification
    requests.post(IFTTT_WEBHOOK, json={'value1': '{location} Weather'.format(location=json_obj['name']), 'value2': '{temperature:.0f} °F — {weather}'.format(temperature=temperature, weather=weather), 'value3': 'https://www.google.com/search?q={location}+weather'.format(location=json_obj['name'].replace(' ', '+'))})
except:
    # Resort to backup of hardcoded location
    response = requests.get('http://api.openweathermap.org/data/2.5/weather?q={location}&appid={openweathermap_api_key}'.format(location=LOCATION, openweathermap_api_key=OPENWEATHERMAP_API_KEY))
    if response.status_code == 200:
        json_obj = json.loads(response.text)
        weather = json_obj['weather'][0]['main']
        temperature = (json_obj['main']['temp'] - 273.15) * 9 / 5 + 32
        requests.post(IFTTT_WEBHOOK, json={'value1': '{location} Weather'.format(location=LOCATION.split(',')[0]), 'value2': '{temperature:.0f} °F — {weather}'.format(temperature=temperature, weather=weather), 'value3': 'https://www.google.com/search?q={location}+weather'.format(location=LOCATION.replace(' ', '+'))})
