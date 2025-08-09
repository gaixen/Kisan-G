import React, { useState } from 'react';
import { sendWhatsappMessage } from '../services/api';

interface WhatsappButtonProps {
  phoneNumber: string;
  message: string;
}

const WhatsappButton: React.FC<WhatsappButtonProps> = ({ phoneNumber, message }) => {
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    setLoading(true);
    try {
      await sendWhatsappMessage(phoneNumber, message);
      alert('WhatsApp message sent successfully!');
    } catch (error) {
      console.error('Error sending WhatsApp message:', error);
      alert('Failed to send WhatsApp message.');
    }
    setLoading(false);
  };

  return (
    <button onClick={handleClick} disabled={loading}>
      {loading ? 'Sending...' : 'Send via WhatsApp'}
    </button>
  );
};

export default WhatsappButton;

