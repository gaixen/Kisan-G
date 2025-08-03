from typing import Literal, Any
from access_location import get_location
from flask import Flask, jsonify
from flask_cors import CORS
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
CORS(app)
logger = logging.getLogger(__name__)

cache_session = requests_cache.CachedSession('.cache', expire_after = 3600) # seconds
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

url = "https://api.open-meteo.com/v1/forecast"
metadata = get_location()
params = {
	"latitude": metadata['latitude'],
	"longitude": metadata['longitude'],
	"hourly": ["temperature_2m", "relative_humidity_2m", "rain"],
}
responses = openmeteo.weather_api(url, params=params)
response = responses[0]

# print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
# print(f"Elevation: {response.Elevation()} m asl")
# print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

@app.route('/api/weather', methods=['GET'])
def get_weather() -> (tuple[Any, Literal[200]] | tuple[Any, Literal[500]]):
    
    """ fetching weather data from openmeteo"""
    
    city = 'kolkata' 
    try:
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
        
        houly_dataframe = pd.DataFrame(data = hourly_data)
        
        weather_info = {
            'temperature': houly_dataframe['temperature_2m'].tolist(),
            'humidity': houly_dataframe['relative_humidity_2m'].tolist(),
            'condition': houly_dataframe['rain'].tolist(),
            'longitude': metadata['longitude'],
            'latitude': metadata['longitude']
        }
        
        return jsonify(weather_info), 200
    except Exception as e:
        logger.error(f"Error fetching weather data: {str(e)}")
        return jsonify({'error': 'Failed to fetch weather data'}), 500

if __name__ == '__main__':
    app.run(debug=True)
