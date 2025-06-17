#!/usr/bin/env python3
"""
Voice Bot Web Application - Main Flask App
A voice-enabled chatbot that responds as Claude would respond
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
import logging

# Import our custom modules
from voice_handler import VoiceHandler
from claude_responder import ClaudeResponder
from conversation_manager import ConversationManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceBotApp:
    """Main Voice Bot Application Class"""
    
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Initialize components
        self.voice_handler = VoiceHandler()
        self.claude_responder = ClaudeResponder()
        self.conversation_manager = ConversationManager()
        
        # Setup routes
        self._setup_routes()
        
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main page route"""
            return render_template('index.html')
        
        @self.app.route('/api/chat', methods=['POST'])
        def chat():
            """Handle text chat requests"""
            try:
                data = request.get_json()
                user_message = data.get('message', '')
                
                if not user_message:
                    return jsonify({'error': 'No message provided'}), 400
                
                # Generate Claude-style response
                response = self.claude_responder.generate_response(user_message)
                
                # Save conversation
                self.conversation_manager.add_exchange(user_message, response)
                
                return jsonify({
                    'response': response,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Chat error: {str(e)}")
                return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.route('/api/voice-chat', methods=['POST'])
        def voice_chat():
            """Handle voice chat requests"""
            try:
                # Check if audio file is present
                if 'audio' not in request.files:
                    return jsonify({'error': 'No audio file provided'}), 400
                
                audio_file = request.files['audio']
                
                # Process voice input
                transcribed_text = self.voice_handler.speech_to_text(audio_file)
                
                if not transcribed_text:
                    return jsonify({'error': 'Could not transcribe audio'}), 400
                
                # Generate Claude-style response
                text_response = self.claude_responder.generate_response(transcribed_text)
                
                # Convert response to speech
                audio_response = self.voice_handler.text_to_speech(text_response)
                
                # Save conversation
                self.conversation_manager.add_exchange(transcribed_text, text_response)
                
                return jsonify({
                    'transcription': transcribed_text,
                    'text_response': text_response,
                    'audio_response': audio_response,  # Base64 encoded audio
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Voice chat error: {str(e)}")
                return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.route('/api/conversation-history', methods=['GET'])
        def get_conversation_history():
            """Get conversation history"""
            try:
                history = self.conversation_manager.get_history()
                return jsonify({'history': history})
            except Exception as e:
                logger.error(f"History error: {str(e)}")
                return jsonify({'error': 'Internal server error'}), 500
        
        @self.app.route('/api/clear-history', methods=['POST'])
        def clear_history():
            """Clear conversation history"""
            try:
                self.conversation_manager.clear_history()
                return jsonify({'message': 'History cleared successfully'})
            except Exception as e:
                logger.error(f"Clear history error: {str(e)}")
                return jsonify({'error': 'Internal server error'}), 500
    
    def run(self, debug=False, host='0.0.0.0', port=5000):
        """Run the Flask application"""
        self.app.run(debug=debug, host=host, port=port)

if __name__ == '__main__':
    # Create and run the app
    voice_bot = VoiceBotApp()
    voice_bot.run(debug=True)