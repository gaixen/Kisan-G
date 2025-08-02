// src/components/VoiceAssistantInput.tsx
import React, { useState } from 'react';
import { FaMicrophone, FaPaperPlane } from 'react-icons/fa';

type VoiceAssistantInputProps = {
  onSend?: (query: string) => void;
};

const VoiceAssistantInput: React.FC<VoiceAssistantInputProps> = ({ onSend }) => {
  const [query, setQuery] = useState('');

  const handleSend = () => {
    if (query.trim()) {
      onSend?.(query.trim());
      setQuery('');
    }
  };

  // Placeholder for voice start logic
  const startVoiceRecognition = () => {
    alert('Voice input integration coming soon!');
  };

  return (
    <div className="fixed bottom-16 left-0 right-0 px-4 sm:px-0 max-w-3xl mx-auto">
      <div className="bg-white shadow-lg rounded-full flex items-center gap-3 p-3">
        <button
          onClick={startVoiceRecognition}
          className="text-primary text-xl p-2 hover:bg-gray-100 rounded-full"
          aria-label="Start Voice Input"
        >
          <FaMicrophone />
        </button>
        <input
          type="text"
          placeholder="Ask Gemini..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-grow border border-gray-300 rounded-full px-4 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-primary"
          onKeyDown={(e) => {
            if (e.key === 'Enter') handleSend();
          }}
          aria-label="Type your question"
        />
        <button
          onClick={handleSend}
          disabled={!query.trim()}
          className="text-white bg-primary hover:bg-green-700 rounded-full p-2 disabled:opacity-50"
          aria-label="Send Query"
        >
          <FaPaperPlane />
        </button>
      </div>
    </div>
  );
};

export default VoiceAssistantInput;
