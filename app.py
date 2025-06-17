#!/usr/bin/env python3
"""
Voice Bot Web Application - Main Flask App
A voice-enabled chatbot that responds as Claude would respond
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import logging
from datetime import datetime

# Configure logging to output to stdout
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Application Factory to create and configure the Flask app"""
    app = Flask(__name__)
    CORS(app)

    # Initialize components
    from voice_handler import VoiceHandler
    from claude_responder import ClaudeResponder
    from conversation_manager import ConversationManager

    voice_handler = VoiceHandler()
    claude_responder = ClaudeResponder()
    conversation_manager = ConversationManager()

    @app.route('/')
    def index():
        """Main page route"""
        return render_template('index.html')

    @app.route('/api/chat', methods=['POST'])
    def chat():
        """Handle text chat requests"""
        try:
            data = request.get_json()
            user_message = data.get('message', '')

            if not user_message:
                return jsonify({'error': 'No message provided'}), 400

            response = claude_responder.generate_response(user_message)
            conversation_manager.add_exchange(user_message, response)

            return jsonify({
                'response': response,
                'timestamp': datetime.now().isoformat()
            })

        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/voice-chat', methods=['POST'])
    def voice_chat():
        """Handle voice chat requests"""
        try:
            if 'audio' not in request.files:
                return jsonify({'error': 'No audio file provided'}), 400

            audio_file = request.files['audio']
            transcribed_text = voice_handler.speech_to_text(audio_file)

            if not transcribed_text:
                return jsonify({'error': 'Could not transcribe audio'}), 400

            text_response = claude_responder.generate_response(transcribed_text)
            audio_response = voice_handler.text_to_speech(text_response)
            conversation_manager.add_exchange(transcribed_text, text_response)

            return jsonify({
                'transcription': transcribed_text,
                'text_response': text_response,
                'audio_response': audio_response,
                'timestamp': datetime.now().isoformat()
            })

        except Exception as e:
            logger.error(f"Voice chat error: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/conversation-history', methods=['GET'])
    def get_conversation_history():
        """Get conversation history"""
        try:
            history = conversation_manager.get_history()
            return jsonify({'history': history})
        except Exception as e:
            logger.error(f"History error: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/clear-history', methods=['POST'])
    def clear_history():
        """Clear conversation history"""
        try:
            conversation_manager.clear_history()
            return jsonify({'message': 'History cleared successfully'})
        except Exception as e:
            logger.error(f"Clear history error: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500

    return app

if __name__ == '__main__':
    # Create the app
    app = create_app()
