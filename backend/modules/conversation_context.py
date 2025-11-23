"""
Conversation Context Manager - Stores and manages conversation history
Includes Redis caching for improved performance
"""
from datetime import datetime
from typing import List, Dict, Optional
import json
import os
from database import get_database


class ConversationContext:
    """Manages conversation history and context"""
    
    def __init__(self, max_history: int = 10, storage_file: str = "data/conversation_history.json"):
        self.max_history = max_history
        self.storage_file = storage_file
        self.history: List[Dict] = []
        self.last_response: Optional[str] = None
        self.load_history()
    
    def add_exchange(self, user_input: str, ai_response: str):
        """Add a user-AI exchange to history (invalidates Redis cache)"""
        exchange = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "ai": ai_response
        }
        self.history.append(exchange)
        self.last_response = ai_response
        
        # Keep only recent history
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        
        # Invalidate Redis cache when new exchange is added
        db = get_database()
        redis_client = db.get_redis()
        if redis_client:
            # Invalidate all context caches
            for n in [3, 5, 10]:
                redis_client.delete(f"conversation:context:{n}")
        
        self.save_history()
    
    def get_context_string(self, include_last_n: int = 5) -> str:
        """
        Get formatted context string for AI (with Redis caching)
        
        Args:
            include_last_n: Number of recent exchanges to include
            
        Returns:
            Formatted context string
        """
        db = get_database()
        redis_client = db.get_redis()
        
        # Check Redis cache (5 minutes TTL)
        cache_key = f"conversation:context:{include_last_n}"
        if redis_client:
            cached_context = redis_client.get(cache_key)
            if cached_context:
                return cached_context
        
        if not self.history:
            return ""
        
        recent = self.history[-include_last_n:]
        context_parts = []
        
        for exchange in recent:
            context_parts.append(f"User: {exchange['user']}")
            context_parts.append(f"Assistant: {exchange['ai']}")
        
        context_string = "\n".join(context_parts)
        
        # Cache in Redis (5 minutes TTL)
        if redis_client:
            redis_client.set(cache_key, context_string, ttl=300)
        
        return context_string
    
    def get_last_response(self) -> Optional[str]:
        """Get the last AI response"""
        return self.last_response
    
    def clear_history(self):
        """Clear conversation history"""
        self.history = []
        self.last_response = None
        self.save_history()
    
    def save_history(self):
        """Save history to file"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "history": self.history,
                    "last_response": self.last_response
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save conversation history: {e}")
    
    def load_history(self):
        """Load history from file"""
        if not os.path.exists(self.storage_file):
            return
        
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.history = data.get("history", [])
                self.last_response = data.get("last_response")
                
                # Ensure we don't exceed max_history
                if len(self.history) > self.max_history:
                    self.history = self.history[-self.max_history:]
        except Exception as e:
            print(f"Warning: Could not load conversation history: {e}")
            self.history = []
            self.last_response = None


# Global context instance
_context = ConversationContext()


def get_context() -> ConversationContext:
    """Get the global conversation context"""
    return _context

