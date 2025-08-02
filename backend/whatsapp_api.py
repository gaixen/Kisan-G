from flask import Flask, request, jsonify
import requests
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)

@app.route('/api/whatsapp/send', methods=['POST'])
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

if __name__ == '__main__':
    app.run(debug=True)
