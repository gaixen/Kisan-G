from utils.logging import get_logger, log_exception, log_execution_time
import pandas as pd
import openmeteo_requests
import requests_cache
from retry_requests import retry
from access_location import access_location

logger = get_logger(__name__)

class WeatherService:
    def __init__(self):
        """Initialize the weather service client."""
        self.cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        self.retry_session = retry(self.cache_session, retries=5, backoff_factor=0.2)
        self.openmeteo = openmeteo_requests.Client(session=self.retry_session)
        logger.info("WeatherService initialized.")

    @log_exception()
    @log_execution_time()
    def get_weather_for_static_location(self):
        """
        Fetches weather data for a static location determined by the access_location service.
        """
        try:
            location = access_location()
            if not location or 'latitude' not in location or 'longitude' not in location:
                logger.error("Failed to get location from access_location service.")
                return None
                
            latitude = location['latitude']
            longitude = location['longitude']
            
            logger.info(f"Fetching weather for static location: Lat {latitude}, Lon {longitude}")

            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "hourly": ["temperature_2m", "relative_humidity_2m", "rain"],
            }
            responses = self.openmeteo.weather_api(url, params=params)
            
            if not responses:
                logger.error("Open-Meteo API returned no response.")
                return None
                
            response = responses[0]

            if hasattr(response, "Hourly") and response.Hourly() is None:
                logger.error("Open-Meteo API returned no hourly data.")
                return None

            hourly = response.Hourly()
            
            # Process data into a DataFrame
            hourly_data = {
                "date": pd.to_datetime(hourly.Time(), unit="s", utc=True),
                "temperature_2m": hourly.Variables(0).ValuesAsNumpy(),
                "relative_humidity_2m": hourly.Variables(1).ValuesAsNumpy(),
                "rain": hourly.Variables(2).ValuesAsNumpy(),
            }
            hourly_dataframe = pd.DataFrame(data=hourly_data)
            
            # Convert Timestamp objects to strings to prevent JSON serialization errors
            hourly_dataframe['date'] = hourly_dataframe['date'].astype(str)
            
            records = hourly_dataframe.to_dict(orient='records')

            logger.info(f"Successfully fetched {len(records)} weather records.")
            
            return {
                "latitude": latitude,
                "longitude": longitude,
                "weather_info": records
            }

        except Exception as e:
            logger.error(f"An unexpected error occurred in get_weather_for_static_location: {str(e)}")
            return None

if __name__ == "__main__":
    service = WeatherService()
    weather_data = service.get_weather_for_static_location()
    if weather_data:
        print("Weather data fetched successfully:")
        print(weather_data)
    else:
        print("Failed to fetch weather data.")