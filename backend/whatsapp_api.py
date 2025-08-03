from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WHATSAPP_API_URL = os.getenv('WHATSAPP_API_URL')
WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN')

@app.route('/api/whatsapp/send', methods=['POST'])
def send_whatsapp_message():
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        message = data.get('message')

        if not phone_number or not message:
            return jsonify({'error': 'Phone number and message are required'}), 400

        url = f"{WHATSAPP_API_URL}/{WHATSAPP_PHONE_NUMBER_ID}/messages"

        headers = {
            'Authorization': f'Bearer {WHATSAPP_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {
                "body": message
            }
        }

        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()

        if response.status_code != 200:
            logger.error(f"WhatsApp API Error: {response_data}")
            return jsonify({'error': 'Failed to send message', 'details': response_data}), response.status_code

        logger.info(f"WhatsApp message sent to {phone_number}: {message}")
        return jsonify({'status': 'Message sent successfully', 'response': response_data}), 200

    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
