from utils.logging import get_logger
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
from pydub import AudioSegment

load_dotenv()
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

app = Flask(__name__)
CORS(app)

logger = get_logger(__name__)


os.makedirs('uploads', exist_ok=True)

class ChirpSTTService:
    
    def __init__(self, file_ext) -> None:
        self.supported_formats = ['wav', 'mp3', 'ogg', 'webm']
        self.file_ext = file_ext
        
    def transcribe_audio(self, audio_file_path: str) -> dict:
        try:
            client = speech.SpeechClient()
            
            with open(audio_file_path, 'rb') as f:
                content = f.read()
                
            audio = speech.RecognitionAudio(content=content)
            
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code = "en-US",
                model = "chirp"
            )
            response = client.recognize(config=config, audio=audio)
            if not response.results:
                return {"error": "no transcription resuls."}
            
            result = response.results[0].alternatives[0]
            return {
                "transcript": result.transcript,
                "confidence": result.confidence,
                "language": result.language_code,
                "duration": None,
                "model": "chirp"
            }
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return {"error": f"Transcription failed: {str(e)}"}
    
    def get_audio_encoding(self, file_ext: str):
        mapping = {
            'wav': speech.RecognitionConfig.AudioEncoding.LINEAR16,
            'mp3': speech.RecognitionConfig.AudioEncoding.MP3,
            'ogg': speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
            'webm': speech.RecognitionConfig.AudioEncoding.OGG_OPUS,  # WebM often uses OGG_OPUS codec
            'flac': speech.RecognitionConfig.AudioEncoding.FLAC
        }
        if file_ext not in mapping:
            raise ValueError(f"Unsupported audio format: {file_ext}")
        return mapping[file_ext]
        
    
    def process_audio_data(self, audio_data: bytes, format: str = 'wav') -> dict:
        try:
            if format not in self.supported_formats:
                return {"error": f"Unsupported audio format: {format}"}
            
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
        Returns:List of supported language codes
        """
        return [
            "en-US", "en-IN", "hi-IN", "bn-IN", "te-IN", 
            "ta-IN", "mr-IN", "gu-IN", "kn-IN", "pa-IN"
        ]

# Initialize STT service function
def get_stt_service(file_ext):
    return ChirpSTTService(file_ext)



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
        stt_service = get_stt_service(file_ext)
        result = stt_service.process_audio_data(audio_data, file_ext)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in speech transcription endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/speech/languages', methods=['GET'])
def get_supported_languages():
    """Get supported languages for STT"""
    stt_service = get_stt_service('wav')  # Use default format for languages
    languages = stt_service.get_supported_languages()
    return jsonify({'languages': languages}), 200

if __name__ == '__main__':
    app.run(debug=True)