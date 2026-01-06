import os
import pandas as pd
import openmeteo_requests
import requests_cache
from utils.logging import get_logger, setup_logging, RequestLogger
from flask import Flask, jsonify, request
from flask_cors import CORS
from retry_requests import retry
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from database import DatabaseManager

load_dotenv()

# Initialize centralized logging
setup_logging()
logger = get_logger(__name__)

try:
    from whatsapp_service import WhatsAppService
    from agentic_int import CropDiseaseAnalyzer
    from market_scrapper import MarketDataScraper
    from vectorstores.gov_rag_system import GovernmentRAGSystem
    from weather_service import WeatherService
    from voice import AudioTranscriber
except ImportError as e:
    logger.warning(f"Warning: Error Importing: {str(e)}")
    CropDiseaseAnalyzer = None

app = Flask(__name__)

CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Note: logging already configured via utils.logging setup above

# Initialize the database manager
db_manager = DatabaseManager()

# Configure upload folder
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- API Clients Setup ---
# Setup for Open-Meteo API (Weather)
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# --- API Endpoints ---

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint to verify server is running."""
    return jsonify({
        'status': 'healthy',
        'message': 'Kisan-G Backend Server is running!',
        'version': '1.0.0'
    })

@app.route('/api/health', methods=['GET'])
def api_health():
    """API health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'message': 'API is working!',
        'endpoints': [
            '/api/location',
            '/api/crop-analysis',
            '/api/market-trends',
            '/api/govt-schemes',
            '/api/weather',
            '/api/soil-analysis',
            '/api/speech-to-text',
            '/api/whatsapp/send',
            '/api/stats'
        ]
    })

@app.route('/api/speech-to-text', methods=['POST'])
def speech_to_text():
    """
    Transcribes an audio file.
    Expects an 'audio' file in the multipart form data.
    """
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file part in the request'}), 400
    
    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({'error': 'No audio file selected'}), 400

    filename = secure_filename(audio_file.filename)
    # file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'wav'
    
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    audio_file.save(temp_path)

    try:
        if AudioTranscriber:
            stt_service = AudioTranscriber(audio_file=temp_path)
            result = stt_service.transcriber(audio_file=temp_path)
            return jsonify({'transcript': result})
        else:
            return jsonify({'error': 'Speech-to-text service not available'}), 503
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.route('/api/weather', methods=['GET'])
def get_weather():
    """
    Gets weather forecast data for a static, backend-defined location,
    stores it in the database, and returns it.
    """
    if not WeatherService:
        return jsonify({'error': 'Weather service is not available.'}), 503

    try:
        # 1. Initialize the service and fetch weather data
        service = WeatherService()
        weather_data = service.get_weather_for_static_location()

        if not weather_data:
            return jsonify({'error': 'Failed to fetch weather data from the service.'}), 500

        # 2. Store the fresh data in the database
        db_manager.store_weather_data(
            latitude=weather_data['latitude'],
            longitude=weather_data['longitude'],
            weather_info=weather_data['weather_info']
        )
        
        # 3. Return the fresh data to the frontend
        return jsonify(weather_data)

    except Exception as e:
        logger.error(f"Error in get_weather endpoint: {str(e)}")
        return jsonify({'error': f'An internal error occurred: {str(e)}'}), 500

@app.route('/api/crop-analysis', methods=['POST'])
def analyze_crop():
    """
    Analyzes a crop image for diseases.
    Expects a 'file' in the multipart form data and an optional 'query' field.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    filename = secure_filename(file.filename)
    media_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(media_path)

    query = request.form.get('query', 'Analyze the provided image for crop diseases.')
    
    try:
        if CropDiseaseAnalyzer:
            analyzer = CropDiseaseAnalyzer()
            result = analyzer.analyze_crop(media_path=media_path, query=query)
            return jsonify(result)
        else:
            # Fallback mock response when analyzer is not available
            mock_result = {
                'analysis': 'Image received and processed successfully',
                'disease_detected': 'Unable to analyze - service unavailable',
                'confidence': 0.0,
                'recommendations': 'Please consult with local agricultural expert',
                'message': 'Crop disease analyzer service not available'
            }
            return jsonify(mock_result)
    except Exception as e:
        logger.error(f"Error analyzing crop: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
    finally:
        # Clean up uploaded file
        if os.path.exists(media_path):
            os.remove(media_path)

@app.route('/api/market-trends', methods=['POST'])
def get_market_trends():
    """
    Gets market price trends for a given commodity, state, and market.
    Expects 'commodity', 'state', and 'market' in the JSON body.
    """
    import time
    start_time = time.time()
    
    data = request.get_json()
    commodity = data.get('commodity')
    state = data.get('state')
    market = data.get('market')
    
    logger.info(f"Market trends request - Commodity: {commodity}, State: {state}, Market: {market}")

    if not all([commodity, state, market]):
        error_response = {'error': 'Missing required parameters: commodity, state, market'}
        db_manager.log_request('/api/market-trends', 'POST', 
                            {'commodity': commodity, 'state': state, 'market': market}, 
                            400, error_response, time.time() - start_time)
        return jsonify(error_response), 400

    try:
        # Check if we have cached data in database first
        cached_data = db_manager.get_market_trends(commodity, state, market)
        if cached_data:
            logger.info("Returning cached market trends data")
            db_manager.log_request('/api/market-trends', 'POST', 
                                {'commodity': commodity, 'state': state, 'market': market}, 
                                200, cached_data, time.time() - start_time)
            return jsonify(cached_data)
        
        # Try to get fresh data from scraper
        if MarketDataScraper:
            try:
                scraper = MarketDataScraper(headless=True)
                trends = scraper.get_price_trends(commodity, state, market)
                # Store in database
                db_manager.store_market_trends(commodity, state, market, trends)
                logger.info("Fresh market trends data retrieved and stored")
                db_manager.log_request('/api/market-trends', 'POST', 
                                    {'commodity': commodity, 'state': state, 'market': market}, 
                                    200, trends, time.time() - start_time)
                return jsonify(trends)
            except Exception as scraper_error:
                logger.warning(f"Market scraper failed: {scraper_error}, falling back to mock data")
        
        # Fallback mock data when scraper is not available
        mock_data = {
            'commodity': commodity,
            'state': state, 
            'market': market,
            'latest_price': 2450,
            'trend': 'upward',
            'percentage_change': 8.5,
            'data_points_found': 15,
            'average_price': 2320,
            'highest_price': 2650,
            'lowest_price': 2100,
            'prices': [
                {'date': '2024-01-01', 'price': 2100, 'trend': 'up'},
                {'date': '2024-01-02', 'price': 2200, 'trend': 'up'},
                {'date': '2024-01-03', 'price': 2180, 'trend': 'down'},
                {'date': '2024-01-04', 'price': 2350, 'trend': 'up'},
                {'date': '2024-01-05', 'price': 2450, 'trend': 'up'}
            ],
            'message': 'Using mock data - market scraper not available'
        }
        
        # Store mock data in database
        db_manager.store_market_trends(commodity, state, market, mock_data)
        logger.info("Mock market trends data stored and returned")
        
        db_manager.log_request('/api/market-trends', 'POST', 
                            {'commodity': commodity, 'state': state, 'market': market}, 
                            200, mock_data, time.time() - start_time)
        return jsonify(mock_data)
        
    except Exception as e:
        logger.error(f"Error getting market trends: {str(e)}")
        error_response = {'error': f'An error occurred: {str(e)}'}
        db_manager.log_request('/api/market-trends', 'POST', 
                            {'commodity': commodity, 'state': state, 'market': market}, 
                            500, error_response, time.time() - start_time)
        return jsonify(error_response), 500

@app.route('/api/govt-schemes', methods=['GET'])
def get_govt_schemes():
    """
    Searches for government schemes based on a query.
    Expects 'query' as a query parameter.
    """
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Missing required query parameter: query'}), 400
        
    try:
        if GovernmentRAGSystem:
            rag_system = GovernmentRAGSystem()
            schemes = rag_system.search_schemes(query)
            db_manager.store_govt_schemes(query, schemes)
            return jsonify({'schemes': schemes})
        else:
            # Fallback mock data when RAG system is not available
            mock_schemes = [
                {
                    'title': 'Pradhan Mantri Fasal Bima Yojana',
                    'description': 'Crop insurance scheme providing coverage against crop loss',
                    'eligibility': 'All farmers including sharecroppers and tenant farmers',
                    'benefits': 'Financial support in case of crop loss due to natural calamities'
                },
                {
                    'title': 'PM-KISAN Scheme', 
                    'description': 'Direct income support to farmers',
                    'eligibility': 'Small and marginal farmers with landholding up to 2 hectares',
                    'benefits': 'Rs 6000 per year in three equal installments'
                },
                {
                    'title': 'Soil Health Card Scheme',
                    'description': 'Scheme to issue soil health cards to farmers',
                    'eligibility': 'All farmers',
                    'benefits': 'Information about nutrient status and recommendations for soil health'
                }
            ]
            db_manager.store_govt_schemes(query, mock_schemes, message='Using mock data - RAG system not available')
            return jsonify({'schemes': mock_schemes, 'message': 'Using mock data - RAG system not available'})
    except Exception as e:
        logger.error(f"Error getting government schemes: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/api/soil-analysis', methods=['GET'])
def get_soil_analysis():
    """
    Gets soil data for a given latitude and longitude from Open-Meteo.
    Expects 'latitude' and 'longitude' as query parameters.
    """
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')

    if not latitude or not longitude:
        return jsonify({'error': 'Latitude and longitude are required query parameters'}), 400

    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": float(latitude),
            "longitude": float(longitude),
            "hourly": ["soil_temperature_0_to_7cm", "soil_moisture_0_to_7cm"],
        }
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]

        hourly = response.Hourly()
        soil_data = {
            "time": pd.to_datetime(hourly.Time(), unit="s", utc=True).strftime('%Y-%m-%dT%H:%M:%S').tolist(),
            "soil_temperature_0_to_7cm": hourly.Variables(0).ValuesAsNumpy().tolist(),
            "soil_moisture_0_to_7cm": hourly.Variables(1).ValuesAsNumpy().tolist(),
        }
        
        return jsonify(soil_data)
    except Exception as e:
        return jsonify({'error': f'Failed to fetch soil data: {str(e)}'}), 500

@app.route('/api/whatsapp/send', methods=['POST'])
def send_whatsapp_message():
    """
    Sends a WhatsApp message to a given phone number.
    Expects 'to_phone_number' and 'message' in the JSON body.
    """
    data = request.get_json()
    to_phone_number = data.get('to_phone_number')
    message = data.get('message')

    if not to_phone_number or not message:
        return jsonify({'error': 'Missing required parameters: to_phone_number, message'}), 400

    try:
        if WhatsAppService:
            whatsapp = WhatsAppService()
            result = whatsapp.send_message(to_phone_number, message)
            if 'error' in result:
                return jsonify(result), 500
            return jsonify(result)
        else:
            # Fallback response when WhatsApp service is not available
            return jsonify({
                'success': False,
                'message': 'WhatsApp service not available',
                'status': 'service_unavailable'
            })
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)
