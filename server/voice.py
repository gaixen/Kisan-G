import assemblyai as aai
import os
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("ASSEMBLYAI_API_KEY")  

aai.settings.api_key = KEY

audio_file = r"C:\Users\sudip\Gemma-3n-impact\remote\server\uploads\sample01.mp3"

class AudioTranscriber:
    
    def __init__(self, audio_file):
        self.audio_file = audio_file
        
    def transcriber(self, audio_file):
        
        aai.settings.api_key = KEY
        config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.best)
        transcript = aai.Transcriber(config=config).transcribe(audio_file)
        
        if transcript.status == "error":
            raise RuntimeError(f"Transcription failed: {transcript.error}")
        
        return transcript.text
    

if __name__ == "__main__":
    transcriber = AudioTranscriber(audio_file)
    text = transcriber.transcriber(audio_file)
    print(text)
