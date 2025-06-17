#!/usr/bin/env python3
"""
Conversation Manager Module
Manages conversation history and context
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ConversationManager:
    """Manages conversation history and context"""
    
    def __init__(self, history_file: str = 'conversation_history.json'):
        self.history_file = history_file
        self.conversation_history = self._load_history()
        self.max_history_length = 100  # Keep last 100 exchanges
        
    def _load_history(self) -> List[Dict]:
        """Load conversation history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Error loading history: {str(e)}")
            return []
    
    def _save_history(self) -> None:
        """Save conversation history to file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving history: {str(e)}")
    
    def add_exchange(self, user_message: str, assistant_response: str) -> None:
        """Add a conversation exchange to history"""
        exchange = {
            'timestamp': datetime.now().isoformat(),
            'user_message': user_message,
            'assistant_response': assistant_response,
            'exchange_id': len(self.conversation_history) + 1
        }
        
        self.conversation_history.append(exchange)
        
        # Trim history if it gets too long
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history = self.conversation_history[-self.max_history_length:]
        
        self._save_history()
        logger.info(f"Added exchange {exchange['exchange_id']}")
    
    def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """Get conversation history"""
        if limit:
            return self.conversation_history[-limit:]
        return self.conversation_history
    
    def get_recent_context(self, num_exchanges: int = 3) -> str:
        """Get recent conversation context as a formatted string"""
        recent_history = self.conversation_history[-num_exchanges:] if self.conversation_history else []
        
        if not recent_history:
            return ""
        
        context_parts = []
        for exchange in recent_history:
            context_parts.append(f"User: {exchange['user_message']}")
            context_parts.append(f"Assistant: {exchange['assistant_response']}")
            context_parts.append("---")
        
        return "\n".join(context_parts)
    
    def search_history(self, query: str) -> List[Dict]:
        """Search conversation history for specific terms"""
        query_lower = query.lower()
        matching_exchanges = []
        
        for exchange in self.conversation_history:
            if (query_lower in exchange['user_message'].lower() or 
                query_lower in exchange['assistant_response'].lower()):
                matching_exchanges.append(exchange)
        
        return matching_exchanges
    
    def get_conversation_stats(self) -> Dict:
        """Get statistics about the conversation"""
        if not self.conversation_history:
            return {
                'total_exchanges': 0,
                'first_interaction': None,
                'last_interaction': None,
                'avg_user_message_length': 0,
                'avg_assistant_response_length': 0
            }
        
        user_lengths = [len(ex['user_message']) for ex in self.conversation_history]
        assistant_lengths = [len(ex['assistant_response']) for ex in self.conversation_history]
        
        return {
            'total_exchanges': len(self.conversation_history),
            'first_interaction': self.conversation_history[0]['timestamp'],
            'last_interaction': self.conversation_history[-1]['timestamp'],
            'avg_user_message_length': sum(user_lengths) / len(user_lengths),
            'avg_assistant_response_length': sum(assistant_lengths) / len(assistant_lengths)
        }
    
    def clear_history(self) -> None:
        """Clear all conversation history"""
        self.conversation_history = []
        if os.path.exists(self.history_file):
            os.remove(self.history_file)
        logger.info("Conversation history cleared")
    
    def export_history(self, format_type: str = 'json') -> str:
        """Export conversation history in different formats"""
        if format_type.lower() == 'json':
            return json.dumps(self.conversation_history, indent=2, ensure_ascii=False)
        
        elif format_type.lower() == 'txt':
            lines = []
            for exchange in self.conversation_history:
                lines.append(f"[{exchange['timestamp']}]")
                lines.append(f"User: {exchange['user_message']}")
                lines.append(f"Assistant: {exchange['assistant_response']}")
                lines.append("-" * 50)
            return "\n".join(lines)
        
        elif format_type.lower() == 'markdown':
            lines = ["# Conversation History", ""]
            for exchange in self.conversation_history:
                lines.append(f"## Exchange {exchange['exchange_id']}")
                lines.append(f"*{exchange['timestamp']}*")
                lines.append("")
                lines.append(f"**User:** {exchange['user_message']}")
                lines.append("")
                lines.append(f"**Assistant:** {exchange['assistant_response']}")
                lines.append("")
                lines.append("---")
                lines.append("")
            return "\n".join(lines)
        
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def get_frequent_topics(self, top_n: int = 5) -> List[Dict]:
        """Analyze conversation for frequent topics (basic keyword analysis)"""
        # Simple keyword extraction from user messages
        word_counts = {}
        
        for exchange in self.conversation_history:
            words = exchange['user_message'].lower().split()
            # Filter out common words
            filtered_words = [word for word in words if len(word) > 3 and 
                            word not in ['what', 'how', 'when', 'where', 'why', 'that', 'this', 'with', 'from']]
            
            for word in filtered_words:
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # Sort by frequency and return top N
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        return [{'word': word, 'count': count} for word, count in sorted_words[:top_n]]