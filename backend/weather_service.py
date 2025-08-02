import requests
from flask import Flask, jsonify
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Replace with your actual API key
API_KEY = 'YOUR_GOOGLE_WEATHER_API_KEY'

@app.route('/api/weather', methods=['GET'])
def get_weather():
    """Fetch weather data from Google Weather API"""
    city = 'Bangalore'  # Default city for demonstration, can be dynamic
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
