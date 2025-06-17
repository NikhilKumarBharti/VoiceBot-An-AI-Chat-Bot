# The Voice-Bot - Deployment Guide

## Overview
This is a web-based voice bot that responds as an AI-chatbot would, with both text and voice interaction capabilities. The application is built with Flask and uses object-oriented design with separate modules for different functionalities.

## Project Structure
```
claude-voice-bot/
├── app.py                 # Main Flask application
├── claude_responder.py    # Claude personality and response generation
├── voice_handler.py       # Speech-to-text and text-to-speech
├── conversation_manager.py # Conversation history management
├── templates/
│   └── index.html        # Web interface
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

<!-- ## Quick Deployment Options

### Option 1: Heroku (Recommended for beginners)

1. **Create a Heroku account** at https://heroku.com
2. **Install Heroku CLI** from https://devcenter.heroku.com/articles/heroku-cli
3. **Create the app**:
   ```bash
   git clone <your-repo>
   cd claude-voice-bot
   heroku create your-app-name
   ```
4. **Set environment variables**:
   ```bash
   heroku config:set ANTHROPIC_API_KEY=your_api_key_here
   ```
5. **Deploy**:
   ```bash
   git push heroku main
   ```

### Option 2: Railway (Simple deployment)

1. **Sign up** at https://railway.app
2. **Connect your GitHub repository**
3. **Add environment variable**: `ANTHROPIC_API_KEY=your_key`
4. **Deploy automatically**

### Option 3: Render (Free tier available)

1. **Sign up** at https://render.com
2. **Create a new Web Service** from your GitHub repo
3. **Add environment variable**: `ANTHROPIC_API_KEY=your_key`
4. **Deploy** -->

## Local Development Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Microphone (for voice input testing)

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone <your-repo>
   cd claude-voice-bot
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up API key**:
- Visit https://openrouter.ai
- Create an account, and create your API key
3. Create a file called `.env`
4. Copy the following two variables into `.env`:
    ``` OPENROUTER_API_KEY="your-api-key"
OPENROUTER_MODEL="your-desired-model"
```

5. **Create templates directory and add index.html**:
   ```bash
   mkdir templates
   # Copy the HTML content to templates/index.html
   ```

6. **Run the application**:
   ```bash
   python app.py
   ```

7. **Open your preferred browser** and go to: `http://localhost:5000`

8. **Enjoy the app!**

## API Configuration

### Getting Anthropic API Key
1. Visit https://openrouter.ai
2. Create an account, and create your API key
3. Create a file called `.env`
4. Copy the following two variables into `.env`:
    ``` OPENROUTER_API_KEY="your-api-key"
OPENROUTER_MODEL="your-desired-model"
```

**Note**: The bot works without an API key using built-in responses for the sample questions.

**Important Note**: This web app requires the permission to use the device's microphone.

## Features

### Text Chat
- Type messages and get Claude-style responses
- Pre-built responses for common interview questions
- Conversation history tracking

### Voice Chat
- **Record voice**: Click "Start Voice" to record your question
- **Upload audio**: Upload pre-recorded audio files
- **Text-to-speech**: Bot responses are converted to speech
- **Speech-to-text**: Your voice is transcribed to text

### Sample Questions Covered
1. "What should we know about your life story in a few sentences?"
2. "What's your #1 superpower?"
3. "What are the top 3 areas you'd like to grow in?"
4. "What misconception do your coworkers have about you?"
5. "How do you push your boundaries and limits?"

## Technical Architecture

### Object-Oriented Design
- **VoiceBotApp**: Main application class managing Flask routes
- **BotResponder**: Handles AI-style response generation
- **VoiceHandler**: Manages speech-to-text and text-to-speech
- **ConversationManager**: Tracks conversation history

### API Endpoints
- `GET /`: Main web interface
- `POST /api/chat`: Text chat endpoint
- `POST /api/voice-chat`: Voice chat endpoint  
- `GET /api/conversation-history`: Get chat history
- `POST /api/clear-history`: Clear chat history

## Browser Compatibility
- Chrome/Edge: Full support (recommended)
- Firefox: Full support
- Safari: Limited voice support
- Mobile: Text chat works, voice may be limited

## Troubleshooting

### Common Issues

1. **Microphone not working**:
   - Check browser permissions
   - Use HTTPS (required for microphone access)
   - Try uploading audio files instead

2. **Audio playback issues**:
   - Check browser audio settings
   - Ensure audio codecs are supported

3. **API errors**:
   - Check API key is set correctly
   - App works without API key for sample questions

4. **Installation issues**:
   - Ensure Python 3.8+ is installed
   - Try upgrading pip: `pip install --upgrade pip`

### Dependencies Notes
- **pyttsx3**: Text-to-speech engine
- **SpeechRecognition**: Google's speech recognition
- **pydub**: Audio file processing
- **Flask-CORS**: Cross-origin resource sharing

## Deployment Checklist

✅ **Before deployment**:
- [ ] Test locally with `python app.py`
- [ ] Ensure all files are in the repository
- [ ] Set ANTHROPIC_API_KEY environment variable (optional)
- [ ] Test voice functionality in browser

✅ **After deployment**:
- [ ] Test the deployed URL
- [ ] Check that HTTPS is enabled (required for microphone)
- [ ] Test voice recording functionality
- [ ] Verify sample questions work correctly

## Security Notes
- API keys are stored as environment variables
- No sensitive data is logged
- Conversation history is stored temporarily
- Audio files are processed in memory only

## Fine-tuning Information

**Answer to your question**: You don't need to fine-tune a model for this purpose. The bot uses:

1. **Pre-written responses** for the specific sample questions you provided
2. **Anthropic's Claude API** (if available) for other questions
3. **Fallback responses** using rule-based logic for common conversation patterns

The personality and response style are built into the `ClaudeResponder` class, which mimics Claude's communication patterns without requiring model fine-tuning.

## Support
For issues or questions, please check:
1. Browser console for JavaScript errors
2. Server logs for Python errors
3. Network tab for API call failures

The application is designed to be user-friendly with clear error messages and fallback functionality.