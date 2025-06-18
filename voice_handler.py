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
import subprocess
import platform

logger = logging.getLogger(__name__)

class VoiceHandler:
    """Handles voice input and output operations"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.tts_engine = self._initialize_tts()
        self.microphone = sr.Microphone() if self._check_microphone_available() else None
        
    def _initialize_tts(self) -> Optional[pyttsx3.Engine]:
        """Initialize text-to-speech engine with fallbacks"""
        
        # For Linux environments, prefer command-line tools
        if platform.system() == 'Linux':
            # Test if espeak command works first
            if self._test_espeak_command():
                logger.info("Using command-line espeak as primary TTS method")
                return None  # Signal to use fallback method
        
        # Try different TTS drivers in order of preference
        drivers_to_try = []
        
        if platform.system() == 'Linux':
            drivers_to_try = ['espeak']
        elif platform.system() == 'Darwin':  # macOS
            drivers_to_try = ['nsss']
        elif platform.system() == 'Windows':
            drivers_to_try = ['sapi5']
        
        # First try without specifying driver (default)
        try:
            engine = pyttsx3.init()
            return self._configure_engine(engine)
        except Exception as e:
            logger.warning(f"Failed to initialize default TTS engine: {str(e)}")
        
        # Try specific drivers
        for driver in drivers_to_try:
            try:
                logger.info(f"Trying TTS driver: {driver}")
                engine = pyttsx3.init(driverName=driver)
                return self._configure_engine(engine)
            except Exception as e:
                logger.warning(f"Failed to initialize TTS with {driver}: {str(e)}")
                continue
        
        logger.info("pyttsx3 drivers failed, will use command-line TTS")
        return None
    
    def _configure_engine(self, engine) -> pyttsx3.Engine:
        """Configure TTS engine settings"""
        try:
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
            logger.warning(f"Failed to configure TTS engine: {str(e)}")
            return engine
    
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
    
    def _test_espeak_command(self) -> bool:
        """Test if espeak command line tool works"""
        try:
            result = subprocess.run(['espeak', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False
    
    def text_to_speech(self, text: str) -> Optional[str]:
        """Convert text to speech and return base64 encoded audio"""
        # Try command-line first (more reliable in containers)
        if platform.system() == 'Linux':
            result = self._fallback_tts(text)
            if result:
                return result
        
        if not self.tts_engine:
            logger.warning("TTS engine not available and command-line fallback failed")
            return None
            
        try:
            # Create temporary file for audio output
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_path = temp_file.name
            
            # Generate speech
            self.tts_engine.save_to_file(text, temp_path)
            self.tts_engine.runAndWait()
            
            # Check if file was created and has content
            if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
                logger.warning("TTS engine didn't produce audio file, trying fallback")
                os.unlink(temp_path) if os.path.exists(temp_path) else None
                return self._fallback_tts(text)
            
            # Read the audio file and encode to base64
            with open(temp_path, 'rb') as audio_file:
                audio_data = audio_file.read()
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # Clean up
            os.unlink(temp_path)
            
            return audio_base64
            
        except Exception as e:
            logger.error(f"Text to speech error: {str(e)}")
            return self._fallback_tts(text)
    
    def _fallback_tts(self, text: str) -> Optional[str]:
        """Fallback TTS using command line espeak"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_path = temp_file.name
            
            # Try espeak command line
            cmd = ['espeak', '-w', temp_path, '-s', '180', text]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                with open(temp_path, 'rb') as audio_file:
                    audio_data = audio_file.read()
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                os.unlink(temp_path)
                logger.info("Used espeak command line fallback successfully")
                return audio_base64
            else:
                logger.error(f"Espeak command failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("Espeak command timed out")
        except Exception as e:
            logger.error(f"Fallback TTS error: {str(e)}")
        
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
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
        else:
            # Test fallback TTS
            try:
                test_audio = self._fallback_tts("Testing fallback audio")
                results['tts_test'] = test_audio is not None
                results['tts_fallback_used'] = True
            except Exception as e:
                results['tts_test'] = False
                results['tts_error'] = str(e)
        
        return results