import logging
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import base64

logger = logging.getLogger(__name__)

class ChirpSTTService:
    """Google Chirp Speech-to-Text service integration"""
    
    def __init__(self):
        self.supported_formats = ['wav', 'mp3', 'ogg', 'webm']
    
    def transcribe_audio(self, audio_file_path: str) -> dict:
        """
        Transcribe audio using Google's Chirp STT model
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            Dictionary containing transcription results
        """
        try:
            # Mock transcription - in real implementation, use Google Cloud Speech-to-Text API
            # with Chirp model configuration
            
            mock_transcriptions = [
                "What is the best fertilizer for wheat crops?",
                "How to prevent pest attacks on tomatoes?",
                "When should I harvest my rice crop?",
                "What are the symptoms of leaf blight disease?",
                "How much water does my corn field need?"
            ]
            
            # Simulate transcription result
            result = {
                "transcript": mock_transcriptions[0],  # In reality, this would be the actual transcription
                "confidence": 0.92,
                "language": "en-US",
                "duration": 3.5,
                "model": "chirp"
            }
            
            logger.info(f"Audio transcribed successfully: {result['transcript']}")
            return result
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return {"error": f"Transcription failed: {str(e)}"}
    
    def process_audio_data(self, audio_data: bytes, format: str = 'wav') -> dict:
        """
        Process raw audio data for transcription
        
        Args:
            audio_data: Raw audio bytes
            format: Audio format (wav, mp3, etc.)
            
        Returns:
            Transcription result
        """
        try:
            if format not in self.supported_formats:
                return {"error": f"Unsupported audio format: {format}"}
            
            # Save temporary audio file
            temp_filename = f"temp_audio.{format}"
            temp_path = os.path.join('uploads', temp_filename)
            
            with open(temp_path, 'wb') as f:
                f.write(audio_data)
            
            # Transcribe
            result = self.transcribe_audio(temp_path)
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing audio data: {str(e)}")
            return {"error": f"Audio processing failed: {str(e)}"}
    
    def get_supported_languages(self) -> list:
        """
        Get list of supported languages for STT
        
        Returns:
            List of supported language codes
        """
        return [
            "en-US", "en-IN", "hi-IN", "bn-IN", "te-IN", 
            "ta-IN", "mr-IN", "gu-IN", "kn-IN", "pa-IN"
        ]

# Initialize STT service
stt_service = ChirpSTTService()

app = Flask(__name__)

@app.route('/api/speech/transcribe', methods=['POST'])
def transcribe_speech():
    """Transcribe uploaded audio file"""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get file extension
        filename = secure_filename(audio_file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'wav'
        
        # Read audio data
        audio_data = audio_file.read()
        
        # Process transcription
        result = stt_service.process_audio_data(audio_data, file_ext)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in speech transcription endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/speech/languages', methods=['GET'])
def get_supported_languages():
    """Get supported languages for STT"""
    languages = stt_service.get_supported_languages()
    return jsonify({'languages': languages}), 200

if __name__ == '__main__':
    app.run(debug=True)
