from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import logging
import cv2
from flask_cors import CORS
import logging
import sys
sys.path.append('..')
from market_scraper import MarketDataScraper
sys.path.append('../vectorstores')
from gov_rag_system import GovernmentRAGSystem

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Initialize market scraper
market_scraper = MarketDataScraper()

# Initialize RAG system for government schemes
rag_system = GovernmentRAGSystem()

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov', 'mkv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def handle_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({"error": "Internal server error", "details": str(e)}), 500
    return decorated_function


@app.route('/gemma-ai', methods=['POST'])
def interact_with_gemma():
    user_input = request.json.get('user_input', '')
    # Placeholder response from Gemma AI model
    response = {
        "response": f"Simulated response for: {user_input}"
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(debug=True)

from flask import jsonify
@app.route('/upload-crop-image', methods=['POST'])
@handle_errors
def upload_crop_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        # Simulate Gemma AI processing
        response = {
            "predicted_disease": "Leaf Blight",
            "confidence": 0.85,
            "solution": "Apply copper-based fungicide. Remove affected areas."
        }
        return jsonify(response), 200
    return jsonify({'error': 'Invalid file type'}), 400


@app.route('/upload-crop-video', methods=['POST'])
@handle_errors
def upload_crop_video():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        # Placeholder for video processing
        # Use OpenCV for video processing and simulation with Gemma AI model
        response = {
            "predicted_disease": "Simulated Disease",
            "confidence": 0.90,
            "solution": "Apply recommended treatment."
        }
        return jsonify(response), 200
    return jsonify({'error': 'Invalid file type'}), 400


@app.route('/api/market', methods=['GET'])
def get_market_data():
    """Get market data with optional filters"""
    commodity = request.args.get('commodity', 'Wheat')
    state = request.args.get('state', 'Karnataka')
    market = request.args.get('market', 'Bangalore')
    days = int(request.args.get('days', 7))
    
    data = market_scraper.scrape_market_data(commodity, state, market, days)
    
    # Apply filters if provided
    filters = {}
    if request.args.get('min_price'):
        filters['min_price_range'] = int(request.args.get('min_price'))
    if request.args.get('max_price'):
        filters['max_price_range'] = int(request.args.get('max_price'))
    if request.args.get('date_from'):
        filters['date_from'] = request.args.get('date_from')
    if request.args.get('date_to'):
        filters['date_to'] = request.args.get('date_to')
    
    if filters:
        data = market_scraper.filter_data(data, filters)
    
    return jsonify({
        'data': data,
        'metadata': {
            'commodity': commodity,
            'state': state,
            'market': market,
            'total_records': len(data),
            'filters_applied': filters
        }
    }), 200

@app.route('/api/market/commodities', methods=['GET'])
@handle_errors
def get_commodities():
    """Get list of available commodities"""
    commodities = market_scraper.get_available_commodities()
    return jsonify({'commodities': commodities}), 200

@app.route('/api/market/states', methods=['GET'])
@handle_errors
def get_states():
    """Get list of available states"""
    states = market_scraper.get_available_states()
    return jsonify({'states': states}), 200

@app.route('/api/market/markets/<state>', methods=['GET'])
@handle_errors
def get_markets(state):
    """Get list of markets for a specific state"""
    markets = market_scraper.get_markets_by_state(state)
    return jsonify({'markets': markets, 'state': state}), 200

@app.route('/api/market/trends/<commodity>', methods=['GET'])
@handle_errors
def get_price_trends(commodity):
    """Get price trends for a commodity"""
    days = int(request.args.get('days', 30))
    trends = market_scraper.get_price_trends(commodity, days)
    return jsonify(trends), 200

@app.route('/api/schemes/search', methods=['POST'])
@handle_errors
def search_schemes():
    """Search for schemes using RAG system"""
    data = request.get_json()
    query = data.get('query', '')
    user_profile = data.get('user', {})
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    schemes = rag_system.search_schemes(query, user_profile)
    
    return jsonify({
        'schemes': schemes,
        'query': query,
        'total_results': len(schemes)
    }), 200

@app.route('/api/schemes/<scheme_id>', methods=['GET'])
@handle_errors
def get_scheme_details_endpoint(scheme_id):
    """Get detailed scheme information"""
    scheme_details = rag_system.get_scheme_details(scheme_id)
    
    if not scheme_details:
        return jsonify({'error': 'Scheme not found'}), 404
    
    return jsonify(scheme_details), 200

@app.route('/api/schemes', methods=['GET'])
@handle_errors
def get_all_schemes():
    """Get all available schemes"""
    # Get all schemes by searching with empty query
    all_schemes = rag_system.search_schemes('')
    
    return jsonify({
        'schemes': all_schemes,
        'total_schemes': len(all_schemes),
        'metadata': {
            'sources_count': len(rag_system.sources),
            'last_updated': '2024-01-29T10:00:00Z'
        }
    }), 200

@app.route('/api/schemes/scrape', methods=['POST'])
@handle_errors
def scrape_government_data():
    """Trigger scraping of government websites"""
    scraped_data = rag_system.scrape_government_websites()
    
    return jsonify({
        'message': 'Scraping completed',
        'scraped_sources': len(scraped_data),
        'data': scraped_data
    }), 200

@app.route('/api/whatsapp/send', methods=['POST'])
@handle_errors
def send_whatsapp_message():
    """Send a message via WhatsApp API to a local officer"""
    data = request.get_json()
    phone_number = data.get('phone_number')
    message = data.get('message')
    
    if not phone_number or not message:
        return jsonify({'error': 'Phone number and message are required'}), 400
    
    # Mock sending WhatsApp message
    logger.info(f'Sending WhatsApp message to {phone_number}: {message}')
    # In a real implementation, you would call the actual WhatsApp API here
    
    return jsonify({'status': 'Message sent successfully'}), 200

@app.route('/api/weather', methods=['GET'])
@handle_errors
def get_weather():
    """Fetch weather data (mock implementation)"""
    city = request.args.get('city', 'Bangalore')
    
    # Mock weather data - in real implementation, use Google Weather API
    mock_weather = {
        'temperature': 28,
        'humidity': 65,
        'condition': 'Partly Cloudy',
        'location': city,
        'wind_speed': '15 km/h',
        'pressure': '1013 hPa',
        'visibility': '10 km',
        'uv_index': 6,
        'forecast': [
            {'day': 'Today', 'high': 30, 'low': 22, 'condition': 'Partly Cloudy'},
            {'day': 'Tomorrow', 'high': 32, 'low': 24, 'condition': 'Sunny'},
            {'day': 'Day After', 'high': 29, 'low': 21, 'condition': 'Rainy'}
        ]
    }
    
    logger.info(f'Weather data requested for {city}')
    return jsonify(mock_weather), 200
def build_prompt(user_input : str, language : str = 'en') -> jsonify:
    # prompt = f"""You are Kisan-G , a farmer-friendly agenic AI model who 
    # gives responses to their queries in simple, effecive and practical way.
    # Your language of communication : {language}. Make sure it is well-researched and in long-term 
    # build user-accountability.
    # Farmer Query: {user_input}.
    # Your Suggestion: """
    
    jsonified_prompt = {
        "role": "system",
        "language": language,
        "user_input": user_input,
        "tone": "farmer-friendly, simple, effecive and practical",
        "accountability": "well-researched and in long-term build user-accountability",
    }
    
    return jsonified_prompt
    