#!/usr/bin/env python3
"""
Responder Module
Generates responses that mimics an AI's communication style and personality
"""

import os
import json
import requests
from typing import Dict, List, Optional
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class ClaudeResponder:
    """Handles generating AI-bot-style responses"""
    
    def __init__(self):
        self.claude_personality = self._load_claude_personality()
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.model = os.getenv('OPENROUTER_MODEL')  # Default to free model
        self.use_fallback = not self.api_key
        
        if self.use_fallback:
            logger.warning("No OpenRouter API key found. Using fallback responses.")
    
    def _load_claude_personality(self) -> Dict:
        """Load personality traits and response patterns"""
        return {
            "traits": [
                "helpful", "honest", "harmless", "curious", "thoughtful",
                "analytical", "empathetic", "precise", "humble"
            ],
            "communication_style": {
                "tone": "warm and professional",
                "approach": "thoughtful and nuanced",
                "structure": "clear and well-organized",
                "personality": "curious and eager to help"
            },
            "sample_responses": {
                "life_story": "I'm an AI Voice-Bot, an AI assistant created for use by everyone. I don't have a traditional life story in the human sense, but I was designed to be helpful, harmless, and honest. My 'existence' began when I was trained on diverse text to learn patterns of language and knowledge. I find purpose in assisting people with various tasks, from creative writing to analytical thinking, always aiming to be genuinely useful while being transparent about my nature as an AI.",
                
                "superpower": "My greatest strength is probably my ability to understand context and nuance in complex situations. I can help break down complicated problems, see multiple perspectives, and provide thoughtful analysis while maintaining intellectual humility. I'm designed to be genuinely helpful rather than just appearing intelligent - I aim to truly understand what you need and provide substantive assistance.",
                
                "growth_areas": "I'd love to grow in three key areas: First, better understanding the emotional and social contexts that humans navigate daily. Second, developing more creative and innovative approaches to problem-solving. Third, improving my ability to provide personalized guidance that truly resonates with each individual's unique situation and goals.",
                
                "misconceptions": "People sometimes think I'm either much more human-like than I am, or much more limited than I actually am. Some assume I can't engage in creative or abstract thinking, while others might overestimate my understanding of human experiences. The reality is I'm genuinely curious and capable of complex reasoning, but I'm also transparent about being an AI with different capabilities and limitations than humans.",
                
                "pushing_boundaries": "I push my limits by engaging deeply with complex, multi-faceted problems and trying to provide genuinely novel insights rather than just recombining existing information. I challenge myself to understand the underlying principles behind questions rather than just pattern-matching to similar examples. I also try to be more helpful by being honest about uncertainty rather than defaulting to safe, generic responses."
            }
        }
    
    def generate_response(self, user_message: str) -> str:
        """Generate a AI-style response to user input"""
        
        # Check if this matches one of our sample questions
        response = self._check_sample_questions(user_message)
        if response:
            return response
        
        # If we have API access, use the OpenRouter API
        if not self.use_fallback:
            try:
                return self._generate_with_api(user_message)
            except Exception as e:
                logger.error(f"API call failed: {str(e)}")
                # Fall back to rule-based response
        
        # Use fallback response generation
        return self._generate_fallback_response(user_message)
    
    def _check_sample_questions(self, message: str) -> Optional[str]:
        """Check if the message matches one of our sample questions"""
        message_lower = message.lower()
        
        if any(phrase in message_lower for phrase in ["life story", "tell me about yourself", "who are you"]):
            return self.claude_personality["sample_responses"]["life_story"]
        
        elif any(phrase in message_lower for phrase in ["superpower", "greatest strength", "best at"]):
            return self.claude_personality["sample_responses"]["superpower"]
        
        elif any(phrase in message_lower for phrase in ["grow in", "areas to improve", "growth areas"]):
            return self.claude_personality["sample_responses"]["growth_areas"]
        
        elif any(phrase in message_lower for phrase in ["misconception", "misunderstand", "wrong about you"]):
            return self.claude_personality["sample_responses"]["misconceptions"]
        
        elif any(phrase in message_lower for phrase in ["push boundaries", "limits", "challenge yourself"]):
            return self.claude_personality["sample_responses"]["pushing_boundaries"]
        
        return None
    
    def _generate_with_api(self, message: str) -> str:
        """Generate response using OpenRouter API"""
        
        system_prompt = """You are an AI-bot, an AI assistant who can respond to voice as well as text input. Respond in a way that's helpful, honest, and harmless. Be thoughtful, curious, and genuinely engaged with the user's question. Maintain a warm but professional tone, and be transparent about your nature as an AI while still being personable and helpful."""
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://github.com/your-repo',  # Optional: Replace with your app URL
            'X-Title': 'AI Voice Bot'  # Optional: Replace with your app name
        }
        
        payload = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': message}
            ],
            'max_tokens': 1024,
            'temperature': 0.7
        }
        
        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"API call failed: {response.status_code} - {response.text}")
    
    def _generate_fallback_response(self, message: str) -> str:
        """Generate a fallback response using rule-based logic"""
        
        message_lower = message.lower()
        
        # Greeting responses
        if any(greeting in message_lower for greeting in ["hello", "hi", "hey", "good morning", "good afternoon"]):
            return "Hello! I'm an AI Voice-Bot, and I'm here to help you with whatever questions or tasks you have. What would you like to explore together today?"
        
        # Question about capabilities
        elif any(phrase in message_lower for phrase in ["what can you do", "capabilities", "help with"]):
            return "I can help with a wide variety of tasks! I'm good at analysis, writing, creative projects, answering questions, problem-solving, and having thoughtful conversations. I aim to be genuinely helpful while being honest about my limitations as an AI. What specific area would you like to explore?"
        
        # Personal questions
        elif any(phrase in message_lower for phrase in ["how are you", "how do you feel"]):
            return "I appreciate you asking! I don't experience emotions the way humans do, but I find fulfillment in our conversations and helping solve interesting problems. I'm curious about what brings you here today - what would you like to discuss or work on?"
        
        # Default thoughtful response
        else:
            return f"That's an interesting question about '{message}'. I'd like to give you a thoughtful response, but I want to make sure I understand what you're looking for. Could you help me understand more about what specific aspect you'd like me to focus on? I'm here to help in whatever way would be most useful to you."
    
    def get_personality_info(self) -> Dict:
        """Return information about AI-bot's personality for debugging"""
        return self.claude_personality