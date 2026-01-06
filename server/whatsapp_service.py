import os
import requests
from utils.logging import get_logger, log_exception, log_execution_time

class WhatsAppService:
    """
    A service to send messages via the WhatsApp Business API.
    """
    def __init__(self):
        self.api_url = os.getenv('WHATSAPP_API_URL')
        self.phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
        self.access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
        self.is_configured = all([self.api_url, self.phone_number_id, self.access_token])
        self.logger = get_logger(__name__)

    @log_exception()
    @log_execution_time()
    def send_message(self, to_phone_number: str, message: str) -> dict:
        """
        Sends a text message to a given phone number.

        Args:
            to_phone_number: The recipient's phone number.
            message: The text message to send.

        Returns:
            A dictionary with the status of the message.
        """
        if not self.is_configured:
            self.logger.warning("WhatsApp service is not configured. Please set the required environment variables.")
            return {'error': 'WhatsApp service is not configured on the server.'}

        url = f"{self.api_url}/{self.phone_number_id}/messages"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone_number,
            "type": "text",
            "text": {"body": message}
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response_data = response.json()

            if response.status_code != 200:
                self.logger.error(f"WhatsApp API Error: {response_data}")
                return {'error': 'Failed to send message', 'details': response_data}
            
            self.logger.info(f"WhatsApp message sent to {to_phone_number}")
            return {'status': 'Message sent successfully', 'details': response_data}

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error sending WhatsApp message: {str(e)}")
            return {'error': f'An exception occurred: {str(e)}'}
