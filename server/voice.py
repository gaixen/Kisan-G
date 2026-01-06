"""
Voice interaction module for audio-directed navigation and transcription.

Provides voice assistant capabilities including:
- Audio transcription using AssemblyAI
- Voice command interpretation for navigation
- Intent detection for feature switching
- Multi-language support
"""

import assemblyai as aai
import os
import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv
from utils.logging import get_logger

load_dotenv()

logger = get_logger(__name__)


class NavigationIntent(Enum):
    """Available navigation intents for voice commands."""
    DASHBOARD = "dashboard"
    CROP_DOCTOR = "crop_doctor"
    MARKET_ANALYST = "market_analyst"
    SCHEME_NAVIGATOR = "scheme_navigator"
    SOIL_ANALYSIS = "soil_analysis"
    PROFILE = "profile"
    LANGUAGE_SELECT = "language_select"
    WEATHER = "weather"
    UNKNOWN = "unknown"


@dataclass
class VoiceCommandResult:
    """Result of voice command processing."""
    transcript: str
    intent: NavigationIntent
    confidence: float
    action: str
    parameters: Dict[str, Any]


class VoiceNavigationAgent:
    """Agent for interpreting voice commands and determining navigation actions.
    
    Similar to Google Voice Control or Apple Siri, this agent can:
    - Understand natural language commands
    - Extract navigation intents
    - Provide action recommendations
    """
    
    # Intent patterns for matching voice commands
    INTENT_PATTERNS = {
        NavigationIntent.DASHBOARD: [
            r"\b(go to|open|show|navigate to)\s+dashboard\b",
            r"\b(go to|show me)\s+home\b",
            r"\bmain\s+screen\b",
        ],
        NavigationIntent.CROP_DOCTOR: [
            r"\b(check|analyze|diagnose)\s+(my\s+)?(crop|plant)s?\b",
            r"\b(crop|plant)\s+(doctor|disease|health)\b",
            r"\bopen\s+crop\s+doctor\b",
        ],
        NavigationIntent.MARKET_ANALYST: [
            r"\b(check|show|get)\s+(market|price)s?\b",
            r"\b(market|price)\s+(trend|analysis|data)\b",
            r"\bopen\s+market\s+analyst\b",
        ],
        NavigationIntent.SCHEME_NAVIGATOR: [
            r"\b(find|show|search)\s+(government\s+)?schemes?\b",
            r"\bscheme\s+navigator\b",
            r"\bgovernment\s+programs?\b",
        ],
        NavigationIntent.SOIL_ANALYSIS: [
            r"\b(check|analyze|test)\s+soil\b",
            r"\bsoil\s+(analysis|health|condition)\b",
        ],
        NavigationIntent.WEATHER: [
            r"\b(check|show|what's)\s+the\s+weather\b",
            r"\bweather\s+(forecast|information)\b",
        ],
        NavigationIntent.PROFILE: [
            r"\b(go to|open|show)\s+(my\s+)?profile\b",
            r"\baccount\s+settings\b",
        ],
        NavigationIntent.LANGUAGE_SELECT: [
            r"\b(change|select)\s+language\b",
            r"\blanguage\s+(settings|selection)\b",
        ],
    }
    
    def detect_intent(self, text: str) -> tuple[NavigationIntent, float]:
        """Detect navigation intent from transcribed text.
        
        Args:
            text: Transcribed text from voice input
            
        Returns:
            Tuple of (intent, confidence_score)
        """
        text_lower = text.lower()
        
        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return intent, 0.9  # High confidence for pattern match
        
        return NavigationIntent.UNKNOWN, 0.0
    
    def extract_parameters(self, text: str, intent: NavigationIntent) -> Dict[str, Any]:
        """Extract parameters from voice command based on intent.
        
        Args:
            text: Transcribed text
            intent: Detected navigation intent
            
        Returns:
            Dictionary of extracted parameters
        """
        params = {}
        text_lower = text.lower()
        
        # Extract crop names for Crop Doctor
        if intent == NavigationIntent.CROP_DOCTOR:
            crops = ["tomato", "wheat", "rice", "corn", "potato", "cotton"]
            for crop in crops:
                if crop in text_lower:
                    params["crop"] = crop
                    break
        
        # Extract commodity names for Market Analyst
        elif intent == NavigationIntent.MARKET_ANALYST:
            commodities = ["wheat", "rice", "tomato", "onion", "potato"]
            for commodity in commodities:
                if commodity in text_lower:
                    params["commodity"] = commodity
                    break
        
        return params
    
    def process_command(self, transcript: str) -> VoiceCommandResult:
        """Process voice command and generate action.
        
        Args:
            transcript: Text transcription of voice command
            
        Returns:
            VoiceCommandResult with intent and action details
        """
        intent, confidence = self.detect_intent(transcript)
        parameters = self.extract_parameters(transcript, intent)
        
        # Generate action based on intent
        action_map = {
            NavigationIntent.DASHBOARD: "/dashboard",
            NavigationIntent.CROP_DOCTOR: "/crop-doctor",
            NavigationIntent.MARKET_ANALYST: "/market-analyst",
            NavigationIntent.SCHEME_NAVIGATOR: "/scheme-navigator",
            NavigationIntent.SOIL_ANALYSIS: "/soil-analysis",
            NavigationIntent.WEATHER: "/dashboard#weather",
            NavigationIntent.PROFILE: "/profile",
            NavigationIntent.LANGUAGE_SELECT: "/language-select",
            NavigationIntent.UNKNOWN: "",
        }
        
        action = action_map.get(intent, "")
        
        return VoiceCommandResult(
            transcript=transcript,
            intent=intent,
            confidence=confidence,
            action=action,
            parameters=parameters
        )


class AudioTranscriber:
    """Service for transcribing audio files using AssemblyAI.
    
    Supports multiple audio formats and provides high-quality transcription
    with optional language detection.
    """
    
    SUPPORTED_FORMATS = ['mp3', 'wav', 'flac', 'm4a', 'ogg']
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the transcriber.
        
        Args:
            api_key: AssemblyAI API key. If None, reads from environment.
        """
        self.api_key = api_key or os.getenv("ASSEMBLYAI_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "AssemblyAI API key not found. Set ASSEMBLYAI_API_KEY environment variable."
            )
        
        aai.settings.api_key = self.api_key
        self.navigation_agent = VoiceNavigationAgent()
    
    def transcribe(self, audio_file: str, language_code: Optional[str] = None) -> str:
        """Transcribe an audio file to text.
        
        Args:
            audio_file: Path to the audio file
            language_code: Optional language code (e.g., 'en', 'hi', 'es')
            
        Returns:
            Transcribed text
            
        Raises:
            RuntimeError: If transcription fails
            FileNotFoundError: If audio file doesn't exist
        """
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Audio file not found: {audio_file}")
        
        # Validate file format
        file_ext = audio_file.rsplit('.', 1)[-1].lower()
        if file_ext not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported audio format: {file_ext}. "
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
            )
        
        # Configure transcription
        config = aai.TranscriptionConfig(
            speech_model=aai.SpeechModel.best,
            language_code=language_code
        )
        
        # Perform transcription
        transcriber = aai.Transcriber(config=config)
        transcript = transcriber.transcribe(audio_file)
        
        if transcript.status == aai.TranscriptStatus.error:
            raise RuntimeError(f"Transcription failed: {transcript.error}")
        
        return transcript.text
    
    def transcribe_with_navigation(self, audio_file: str) -> VoiceCommandResult:
        """Transcribe audio and detect navigation intent.
        
        Args:
            audio_file: Path to the audio file
            
        Returns:
            VoiceCommandResult with transcript and navigation action
        """
        transcript = self.transcribe(audio_file)
        result = self.navigation_agent.process_command(transcript)
        return result
    
    # Backward compatibility method
    def transcriber(self, audio_file: str) -> str:
        """Transcribe audio (backward compatible method).
        
        Args:
            audio_file: Path to the audio file
            
        Returns:
            Transcribed text
        """
        return self.transcribe(audio_file)


# Factory function for creating transcriber instance
def create_audio_transcriber(api_key: Optional[str] = None) -> AudioTranscriber:
    """Create an AudioTranscriber instance.
    
    Args:
        api_key: Optional AssemblyAI API key
        
    Returns:
        Configured AudioTranscriber instance
    """
    return AudioTranscriber(api_key=api_key)


if __name__ == "__main__":
    # Demo usage
    logger.info("Voice Interaction Module Demo")
    logger.info("" + ("=" * 50))
    
    # Test navigation agent with sample commands
    agent = VoiceNavigationAgent()
    
    test_commands = [
        "Go to dashboard",
        "Check my crop health",
        "Show me market prices",
        "Find government schemes",
        "What's the weather like?",
        "Analyze my tomato plant",
    ]
    
    logger.info("\nTesting voice command interpretation:")
    for command in test_commands:
        result = agent.process_command(command)
        logger.info(f"\nCommand: {command}")
        logger.info(f"Intent: {result.intent.value}")
        logger.info(f"Action: {result.action}")
        logger.info(f"Confidence: {result.confidence}")
        if result.parameters:
            logger.info(f"Parameters: {result.parameters}")
    
    # Test transcriber if audio file exists
    test_audio = os.path.join("uploads", "sample01.mp3")
    if os.path.exists(test_audio):
        try:
            logger.info(f"\n\nTesting audio transcription with: {test_audio}")
            transcriber = create_audio_transcriber()
            result = transcriber.transcribe_with_navigation(test_audio)
            logger.info(f"Transcript: {result.transcript}")
            logger.info(f"Detected Intent: {result.intent.value}")
            logger.info(f"Suggested Action: {result.action}")
        except Exception as e:
            logger.warning(f"Transcription test skipped: {e}")
    else:
        logger.info(f"\n\nSkipping audio transcription test (file not found: {test_audio})")
