import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import List, Dict
from utils.logging import get_logger
import os
from dotenv import load_dotenv
from vectorstores.gov_rag_system import DocumentSource, GovernmentRAGSystem

load_dotenv()

load_dotenv(dotenv_path = os.path.join(os.path.dirname(__file__), '.env'))
app = Flask(__name__)
CORS(app)
logger = get_logger(__name__)

rag_system = GovernmentRAGSystem()

# Simulated source list and mock scheme data
@app.route('/api/rag/search', methods=['POST'])
def search_schemes():
    try:
        data = request.json
        query = data.get('query')
        user_profile = data.get('user_profile', None)

        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400

        results = rag_system.search_schemes(query, user_profile)
        return jsonify({'results': results}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rag/scheme/<scheme_id>', methods=['GET'])
def get_scheme_details(scheme_id):
    try:
        details = rag_system.get_scheme_details(scheme_id)
        if not details:
            return jsonify({'error': 'Scheme not found'}), 404
        
        return jsonify(details), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rag/scrape', methods=['POST'])
def scrape_government_websites():
    try:
        scraped_data = rag_system.scrape_government_websites()
        return jsonify({'scraped_data': scraped_data}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rag/add-document', methods=['POST'])
def add_document():
    try:
        data = request.json
        content = data.get('content')
        source_info = data.get('source')
        scheme_id = data.get('scheme_id')
        keywords = data.get('keywords', [])

        if not all([content, source_info, scheme_id]):
            return jsonify({'error': 'Missing required fields'}), 400

        source = DocumentSource(
            url=source_info['url'],
            title=source_info['title'],
            organization=source_info['organization']
        )

        rag_system.add_document(content, source, scheme_id, keywords)

        return jsonify({'message': 'Document added successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0', port=5000)
