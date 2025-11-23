"""
Voice Command Parser - Extracts intents and entities from voice commands
"""
import re
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from enum import Enum


class CommandIntent(Enum):
    """Supported command intents"""
    ADD_TASK = "add_task"
    SHOW_TASKS = "show_tasks"
    COMPLETE_TASK = "complete_task"
    DELETE_TASK = "delete_task"
    CHECK_MOOD = "check_mood"
    SET_MOOD = "set_mood"
    ASK_QUESTION = "ask_question"
    REPEAT = "repeat"
    UNDO = "undo"
    GET_PLAN = "get_plan"
    SUGGEST_TASKS = "suggest_tasks"
    WHAT_SHOULD_I_DO = "what_should_i_do"
    CHECK_PRODUCTIVITY = "check_productivity"
    PRODUCTIVITY_INSIGHTS = "productivity_insights"
    START_FOCUS = "start_focus"
    END_FOCUS = "end_focus"
    REFLECT = "reflect"
    DAILY_SUMMARY = "daily_summary"
    SHOW_DASHBOARD = "show_dashboard"
    MOTIVATION = "motivation"
    SUGGEST_ROUTINE = "suggest_routine"
    UNKNOWN = "unknown"


class CommandParser:
    """Parses voice commands to extract intent and entities"""
    
    def __init__(self):
        # Patterns for different commands
        self.patterns = {
            CommandIntent.ADD_TASK: [
                r"add\s+(?:a\s+)?task\s+(?:called\s+)?(.+)",
                r"create\s+(?:a\s+)?task\s+(?:called\s+)?(.+)",
                r"new\s+task\s+(?:called\s+)?(.+)",
                r"remind\s+me\s+to\s+(.+)",
                r"i\s+need\s+to\s+(.+)",
            ],
            CommandIntent.SHOW_TASKS: [
                r"show\s+(?:me\s+)?(?:my\s+)?(?:all\s+)?tasks?(?:\s+for\s+(?:today|tomorrow))?",
                r"list\s+(?:my\s+)?(?:all\s+)?tasks?",
                r"what\s+(?:are\s+)?(?:my\s+)?(?:all\s+)?tasks?",
                r"tell\s+me\s+(?:about\s+)?(?:my\s+)?tasks?",
                r"show\s+(?:me\s+)?(?:all\s+)?(?:my\s+)?tasks?",
            ],
            CommandIntent.COMPLETE_TASK: [
                r"complete\s+(?:task\s+)?(.+)",
                r"finish\s+(?:task\s+)?(.+)",
                r"done\s+with\s+(.+)",
                r"mark\s+(.+)?\s+as\s+done",
                r"i\s+finished\s+(.+)",
            ],
            CommandIntent.DELETE_TASK: [
                r"delete\s+(?:task\s+)?(.+)",
                r"remove\s+(?:task\s+)?(.+)",
                r"cancel\s+(?:task\s+)?(.+)",
            ],
            CommandIntent.SET_MOOD: [
                r"i\s+(?:am\s+)?feeling\s+(.+)",
                r"my\s+mood\s+is\s+(.+)",
                r"i\s+feel\s+(.+)",
                r"set\s+mood\s+to\s+(.+)",
            ],
            CommandIntent.CHECK_MOOD: [
                r"how\s+am\s+i\s+feeling",
                r"what\s+(?:is\s+)?(?:my\s+)?mood",
                r"check\s+(?:my\s+)?mood",
            ],
            CommandIntent.REPEAT: [
                r"repeat",
                r"say\s+that\s+again",
                r"what\s+did\s+you\s+say",
            ],
            CommandIntent.UNDO: [
                r"undo",
                r"cancel\s+that",
                r"take\s+that\s+back",
            ],
            CommandIntent.GET_PLAN: [
                r"what\s+(?:is\s+)?(?:my\s+)?plan\s+(?:for\s+)?(?:today|this\s+(?:morning|afternoon|evening))?",
                r"show\s+me\s+(?:my\s+)?plan",
                r"tell\s+me\s+(?:my\s+)?plan",
                r"what\s+should\s+i\s+do\s+(?:today|this\s+(?:morning|afternoon|evening))?",
                r"give\s+me\s+(?:my\s+)?plan",
            ],
            CommandIntent.SUGGEST_TASKS: [
                r"suggest\s+(?:some\s+)?tasks?",
                r"what\s+tasks?\s+should\s+i\s+do",
                r"recommend\s+(?:some\s+)?tasks?",
                r"what\s+should\s+i\s+focus\s+on",
            ],
            CommandIntent.WHAT_SHOULD_I_DO: [
                r"what\s+should\s+i\s+do",
                r"what\s+do\s+i\s+do\s+next",
                r"help\s+me\s+plan",
                r"plan\s+my\s+day",
            ],
            CommandIntent.CHECK_PRODUCTIVITY: [
                r"how\s+(?:am\s+i\s+)?(?:doing|productive)",
                r"what\s+(?:is\s+)?(?:my\s+)?productivity",
                r"check\s+(?:my\s+)?productivity",
                r"show\s+(?:my\s+)?productivity",
            ],
            CommandIntent.PRODUCTIVITY_INSIGHTS: [
                r"productivity\s+insights",
                r"how\s+does\s+mood\s+affect\s+productivity",
                r"productivity\s+trend",
                r"show\s+me\s+productivity\s+insights",
            ],
            CommandIntent.START_FOCUS: [
                r"start\s+(?:a\s+)?focus\s+(?:session|time)",
                r"begin\s+(?:a\s+)?focus\s+(?:session|time)",
                r"focus\s+mode",
                r"start\s+focusing",
            ],
            CommandIntent.END_FOCUS: [
                r"end\s+(?:the\s+)?focus\s+(?:session|time)",
                r"stop\s+(?:the\s+)?focus\s+(?:session|time)",
                r"finish\s+(?:the\s+)?focus\s+(?:session|time)",
            ],
            CommandIntent.REFLECT: [
                r"reflect\s+(?:on\s+)?(?:today|my\s+day)",
                r"end\s+of\s+day\s+reflection",
                r"how\s+did\s+i\s+do\s+today",
                r"daily\s+reflection",
            ],
            CommandIntent.DAILY_SUMMARY: [
                r"daily\s+summary",
                r"today\s+summary",
                r"show\s+(?:me\s+)?(?:my\s+)?(?:daily\s+)?summary",
                r"what\s+did\s+i\s+do\s+today",
            ],
            CommandIntent.SHOW_DASHBOARD: [
                r"show\s+(?:me\s+)?(?:the\s+)?dashboard",
                r"open\s+(?:the\s+)?dashboard",
                r"dashboard",
                r"analytics",
            ],
            CommandIntent.MOTIVATION: [
                r"motivate\s+me",
                r"give\s+me\s+motivation",
                r"encourage\s+me",
                r"i\s+need\s+motivation",
                r"cheer\s+me\s+up",
            ],
            CommandIntent.SUGGEST_ROUTINE: [
                r"suggest\s+(?:a\s+)?routine",
                r"recommend\s+(?:a\s+)?routine",
                r"what\s+routine\s+should\s+i\s+try",
                r"routine\s+suggestion",
            ],
        }
    
    def parse(self, text: str) -> Tuple[CommandIntent, Dict]:
        """
        Parse a voice command and return intent and extracted entities
        
        Args:
            text: The transcribed voice command
            
        Returns:
            Tuple of (intent, entities_dict)
        """
        if not text:
            return CommandIntent.UNKNOWN, {}
        
        text_lower = text.lower().strip()
        
        # Check each intent pattern
        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    entities = self._extract_entities(intent, text_lower, match)
                    return intent, entities
        
        # If no pattern matches, treat as general question
        return CommandIntent.ASK_QUESTION, {"question": text}
    
    def _extract_entities(self, intent: CommandIntent, text: str, match: re.Match) -> Dict:
        """Extract entities from matched command"""
        entities = {}
        
        if intent == CommandIntent.ADD_TASK:
            # Extract task title
            task_text = match.group(1).strip() if match.groups() else text
            
            # Try to extract time/date (improved pattern to catch "10:00 p.m.")
            time_match = re.search(r"(?:at|by|on)\s+(\d{1,2}(?::\d{2})?\s*(?:a\.?m\.?|p\.?m\.?))", text, re.IGNORECASE)
            if time_match:
                entities["due_time"] = time_match.group(1).strip()
                # Remove time from task title (improved pattern)
                task_text = re.sub(r"\s*(?:at|by|on)\s+\d{1,2}(?::\d{2})?\s*(?:a\.?m\.?|p\.?m\.?)", "", task_text, flags=re.IGNORECASE)
            
            # Try to extract date
            date_patterns = [
                r"today",
                r"tomorrow",
                r"next\s+\w+day",
                r"\d{1,2}[/-]\d{1,2}",
            ]
            for pattern in date_patterns:
                date_match = re.search(pattern, text, re.IGNORECASE)
                if date_match:
                    entities["due_date"] = self._parse_date(date_match.group(0))
                    break
            
            entities["title"] = task_text.strip()
            
        elif intent == CommandIntent.COMPLETE_TASK:
            entities["task_name"] = match.group(1).strip() if match.groups() else ""
            
        elif intent == CommandIntent.DELETE_TASK:
            entities["task_name"] = match.group(1).strip() if match.groups() else ""
            
        elif intent == CommandIntent.SET_MOOD:
            mood_text = match.group(1).strip() if match.groups() else ""
            entities["mood"] = self._parse_mood(mood_text)
            entities["mood_text"] = mood_text
        
        elif intent == CommandIntent.GET_PLAN:
            # Extract time of day if mentioned
            if re.search(r"morning", text, re.IGNORECASE):
                entities["time_of_day"] = "morning"
            elif re.search(r"afternoon", text, re.IGNORECASE):
                entities["time_of_day"] = "afternoon"
            elif re.search(r"evening|night", text, re.IGNORECASE):
                entities["time_of_day"] = "evening"
        
        return entities
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string to ISO format"""
        date_str_lower = date_str.lower()
        
        if "today" in date_str_lower:
            return datetime.now().date().isoformat()
        elif "tomorrow" in date_str_lower:
            return (datetime.now() + timedelta(days=1)).date().isoformat()
        else:
            # Try to parse date formats
            try:
                # MM/DD or DD/MM format
                parts = re.split(r"[/-]", date_str)
                if len(parts) == 2:
                    month, day = int(parts[0]), int(parts[1])
                    year = datetime.now().year
                    return datetime(year, month, day).date().isoformat()
            except:
                pass
        
        return None
    
    def _parse_mood(self, mood_text: str) -> Optional[int]:
        """
        Parse mood text to numeric score (1-10)
        Returns None if cannot determine
        """
        mood_text_lower = mood_text.lower()
        
        # Positive moods
        positive_keywords = ["happy", "great", "excellent", "amazing", "wonderful", "good", "fine", "okay", "alright"]
        # Negative moods
        negative_keywords = ["sad", "bad", "terrible", "awful", "depressed", "anxious", "stressed", "tired", "exhausted"]
        # Neutral
        neutral_keywords = ["okay", "fine", "neutral", "normal", "alright"]
        
        # Check for numeric score
        score_match = re.search(r"(\d+)(?:\s*out\s*of\s*10)?", mood_text)
        if score_match:
            score = int(score_match.group(1))
            return max(1, min(10, score))
        
        # Check keywords
        if any(keyword in mood_text_lower for keyword in positive_keywords):
            if any(kw in mood_text_lower for kw in ["very", "extremely", "super"]):
                return 9
            return 7
        elif any(keyword in mood_text_lower for keyword in negative_keywords):
            if any(kw in mood_text_lower for kw in ["very", "extremely"]):
                return 2
            return 4
        elif any(keyword in mood_text_lower for keyword in neutral_keywords):
            return 5
        
        return None


# Global parser instance
_parser = CommandParser()


def parse_command(text: str) -> Tuple[CommandIntent, Dict]:
    """Convenience function to parse a command"""
    return _parser.parse(text)

