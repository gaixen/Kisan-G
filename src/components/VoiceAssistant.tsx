import React, { useState, useRef } from 'react';
import { speechToText, getGovtSchemes } from '../services/api';
import { FaMicrophone, FaStop, FaSearch } from 'react-icons/fa';

const VoiceAssistant: React.FC = () => {
  const [recording, setRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [schemes, setSchemes] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const handleToggleRecording = async () => {
    if (!recording) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        chunksRef.current = [];

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            chunksRef.current.push(event.data);
          }
        };

        mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(chunksRef.current, { type: 'audio/wav' });
          const audioFile = new File([audioBlob], 'voice.wav', { type: 'audio/wav' });

          const formData = new FormData();
          formData.append('audio', audioFile);

          setLoading(true);
          try {
            const res = await speechToText(formData);
            if (res.data.transcript) {
              setTranscript(res.data.transcript);
              setError(null);
            } else {
              setError('No speech detected. Please try again.');
            }
          } catch (error) {
            console.error('Error transcribing audio:', error);
            setError('Failed to transcribe audio. Please try again.');
          }
          setLoading(false);

          // Stop all tracks to release microphone
          stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorder.start();
        setRecording(true);
        setError(null);
      } catch (error) {
        console.error('Error accessing microphone:', error);
        setError('Could not access microphone. Please check permissions.');
      }
    } else {
      // Stop recording
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
        mediaRecorderRef.current.stop();
      }
      setRecording(false);
    }
  };

  const handleSearch = async () => {
    if (!transcript) return;

    setLoading(true);
    setError(null);
    try {
      const res = await getGovtSchemes(transcript);
      if (res.data.schemes && res.data.schemes.length > 0) {
        setSchemes(res.data.schemes);
      } else {
        setError('No schemes found matching your query.');
      }
    } catch (error) {
      console.error('Error fetching government schemes:', error);
      setError('Failed to fetch schemes. Please try again.');
    }
    setLoading(false);
  };

  return (
    <div className="fixed bottom-4 right-4 bg-white p-4 rounded-lg shadow-lg max-w-sm">
      <h3 className="text-lg font-semibold mb-3 text-gray-800">Voice Assistant</h3>
      
      <button
        onClick={handleToggleRecording}
        className={`w-full p-3 rounded-lg font-semibold flex items-center justify-center ${
          recording
            ? 'bg-red-500 hover:bg-red-600 text-white'
            : 'bg-blue-500 hover:bg-blue-600 text-white'
        }`}
      >
        {recording ? (
          <>
            <FaStop className="mr-2" /> Stop Recording
          </>
        ) : (
          <>
            <FaMicrophone className="mr-2" /> Start Recording
          </>
        )}
      </button>

      {error && (
        <p className="mt-2 text-sm text-red-500 bg-red-100 p-2 rounded">{error}</p>
      )}

      {transcript && (
        <div className="mt-3">
          <p className="text-sm text-gray-600 mb-2">Transcript:</p>
          <p className="text-sm bg-gray-100 p-2 rounded mb-3">{transcript}</p>
          <button
            onClick={handleSearch}
            disabled={loading}
            className="w-full bg-green-500 hover:bg-green-600 text-white p-2 rounded flex items-center justify-center disabled:bg-gray-400"
          >
            {loading ? (
              'Searching...'
            ) : (
              <>
                <FaSearch className="mr-2" /> Search Schemes
              </>
            )}
          </button>
        </div>
      )}

      {schemes.length > 0 && (
        <div className="mt-3 max-h-40 overflow-y-auto">
          <h4 className="text-sm font-semibold mb-2 text-gray-700">Government Schemes</h4>
          {schemes.map((scheme, index) => (
            <div key={index} className="mb-2 p-2 bg-gray-50 rounded text-xs">
              <h5 className="font-semibold text-gray-800">{scheme.source?.title}</h5>
              <p className="text-gray-600 mb-1">{scheme.content?.substring(0, 100)}...</p>
              <a
                href={scheme.source?.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-500 hover:text-blue-700"
              >
                Learn More
              </a>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default VoiceAssistant;

