import requests
from flask import Flask, request, jsonify
from typing import List, Dict
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Simulated source list and mock scheme data
SCHEME_SOURCES = {
    "PM-KISAN": "https://pmkisan.gov.in",
    "Crop Insurance": "https://pmfby.gov.in",
    "Soil Health Card": "https://soilhealth.dac.gov.in",
    "KVK-ICAR": "https://icar.org.in"
}

MOCK_SCHEMES = [
    {
        "id": "pm-kisan",
        "title": "PM-KISAN Samman Nidhi",
        "description": "Direct income support for small farmer families.",
        "eligibility": "Landholding up to 2 hectares",
        "source": SCHEME_SOURCES["PM-KISAN"]
    },
    {
        "id": "crop-insurance",
        "title": "Pradhan Mantri Fasal Bima Yojana",
        "description": "Crop insurance scheme providing coverage against crop loss.",
        "eligibility": "All farmers growing notified crops",
        "source": SCHEME_SOURCES["Crop Insurance"]
    },
    {
        "id": "soil-health",
        "title": "Soil Health Card Scheme",
        "description": "Provides information on soil nutrient status to farmers.",
        "eligibility": "All farmers",
        "source": SCHEME_SOURCES["Soil Health Card"]
    }
]

@app.route('/api/schemes', methods=['GET'])
def get_schemes():
    """Retrieve schemes with sources"""
    response = {
        "schemes": MOCK_SCHEMES,
        "metadata": {
            "total_schemes": len(MOCK_SCHEMES),
        }
    }
    return jsonify(response)

@app.route('/api/schemes/<scheme_id>', methods=['GET'])
def get_scheme_details(scheme_id):
    """Retrieve specific scheme details with source attribution"""
    scheme = next((s for s in MOCK_SCHEMES if s["id"] == scheme_id), None)
    if scheme:
        return jsonify(scheme)
    return jsonify({"error": "Scheme not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
