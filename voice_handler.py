#!/usr/bin/env python3
"""
Voice Handler Module
Handles speech-to-text and text-to-speech functionality
"""

import os
import io
import base64
import tempfile
import logging
from typing import Optional, Union
import speech_recognition as sr
import pyttsx3
import threading
from pydub import AudioSegment

logger = logging.getLogger(__name__)

class VoiceHandler:
    """Handles voice input and output operations"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.tts_engine = self._initialize_tts()
        self.microphone = sr.Microphone() if self._check_microphone_available() else None
        
    def _initialize_tts(self) -> pyttsx3.Engine:
        """Initialize text-to-speech engine"""
        try:
            engine = pyttsx3.init()
            
            # Configure voice settings
            voices = engine.getProperty('voices')
            if voices:
                # Try to use a female voice if available
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
                else:
                    # Use the first available voice
                    engine.setProperty('voice', voices[0].id)
            
            # Set speech rate and volume
            engine.setProperty('rate', 180)  # Speed of speech
            engine.setProperty('volume', 0.8)  # Volume level (0.0 to 1.0)
            
            return engine
            
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {str(e)}")
            return None
    
    def _check_microphone_available(self) -> bool:
        """Check if microphone is available"""
        try:
            with sr.Microphone() as source:
                pass
            return True
        except Exception as e:
            logger.warning(f"Microphone not available: {str(e)}")
            return False
    
    def speech_to_text(self, audio_file) -> Optional[str]:
        """Convert speech to text from audio file"""
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                audio_file.save(temp_file.name)
                temp_path = temp_file.name
            
            try:
                # Convert audio file to the right format if needed
                audio = AudioSegment.from_file(temp_path)
                audio = audio.set_frame_rate(16000).set_channels(1)
                
                # Save converted audio
                converted_path = temp_path.replace('.wav', '_converted.wav')
                audio.export(converted_path, format='wav')
                
                # Perform speech recognition
                with sr.AudioFile(converted_path) as source:
                    audio_data = self.recognizer.record(source)
                    text = self.recognizer.recognize_google(audio_data)
                    
                logger.info(f"Transcribed text: {text}")
                return text
                
            finally:
                # Clean up temporary files
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                if os.path.exists(converted_path):
                    os.unlink(converted_path)
                    
        except sr.UnknownValueError:
            logger.error("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Speech to text error: {str(e)}")
            return None
    
    def text_to_speech(self, text: str) -> Optional[str]:
        """Convert text to speech and return base64 encoded audio"""
        if not self.tts_engine:
            logger.error("TTS engine not available")
            return None
            
        try:
            # Create temporary file for audio output
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_path = temp_file.name
            
            # Generate speech
            self.tts_engine.save_to_file(text, temp_path)
            self.tts_engine.runAndWait()
            
            # Read the audio file and encode to base64
            with open(temp_path, 'rb') as audio_file:
                audio_data = audio_file.read()
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # Clean up
            os.unlink(temp_path)
            
            return audio_base64
            
        except Exception as e:
            logger.error(f"Text to speech error: {str(e)}")
            return None
    
    def listen_from_microphone(self, timeout: int = 5) -> Optional[str]:
        """Listen for speech from microphone (for future use)"""
        if not self.microphone:
            logger.error("Microphone not available")
            return None
            
        try:
            with self.microphone as source:
                logger.info("Listening for speech...")
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                # Listen for audio
                audio = self.recognizer.listen(source, timeout=timeout)
                
            # Recognize speech
            text = self.recognizer.recognize_google(audio)
            logger.info(f"Recognized: {text}")
            return text
            
        except sr.WaitTimeoutError:
            logger.warning("Listening timeout")
            return None
        except sr.UnknownValueError:
            logger.error("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Microphone listening error: {str(e)}")
            return None
    
    def test_audio_capabilities(self) -> dict:
        """Test audio input/output capabilities"""
        results = {
            'microphone_available': self.microphone is not None,
            'tts_available': self.tts_engine is not None,
            'speech_recognition_available': True
        }
        
        # Test TTS
        if self.tts_engine:
            try:
                test_audio = self.text_to_speech("Testing audio capabilities")
                results['tts_test'] = test_audio is not None
            except Exception as e:
                results['tts_test'] = False
                results['tts_error'] = str(e)
        
        return results