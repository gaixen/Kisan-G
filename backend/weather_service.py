from typing import Literal, Unknown
from flask import Flask, jsonify
from retry_requests import retry
from dotenv import load_dotenv
import openmeteo_requests
import requests_cache
import pandas as pd
import numpy as np
import requests
import logging
import os

load_dotenv()

app = Flask(__name__)
logger = logging.getLogger(__name__)

cache_session = requests_cache.CachedSession('.cache', expire_after = 3600) # seconds
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 52.52,
	"longitude": 13.41,
	"hourly": ["temperature_2m", "relative_humidity_2m", "rain"],
}
responses = openmeteo.weather_api(url, params=params)
response = responses[0]
# print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
# print(f"Elevation: {response.Elevation()} m asl")
# print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

# API_KEY = os.getenv(WEATHER_API_KEY)

hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
hourly_rain = hourly.Variables(2).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}

hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
hourly_data["rain"] = hourly_rain

hourly_dataframe = pd.DataFrame(data = hourly_data)
print("\nHourly data\n", hourly_dataframe)

@app.route('/api/weather', methods=['GET'])
def get_weather() -> (tuple[Unknown, Literal[200]] | tuple[Unknown, Literal[500]]):
    
    """ fetching weather data from openmeteo"""
    
    city = 'kolkata'  # Default city for demonstration, can be dynamic
    try:
        # URL and parameters for the API request
        url = f'https://api.google.com/weather/v1/{city}?key={API_KEY}'

        # Fetch weather data
        response = requests.get(url)
        data = response.json()

        # Placeholder response for demonstration
        weather_info = {
            'temperature': data.get('temperature', 'N/A'),
            'humidity': data.get('humidity', 'N/A'),
            'condition': data.get('condition', 'Cloudy'),
            'location': city
        }

        return jsonify(weather_info), 200
    except Exception as e:
        logger.error(f"Error fetching weather data: {str(e)}")
        return jsonify({'error': 'Failed to fetch weather data'}), 500

if __name__ == '__main__':
    app.run(debug=True)
