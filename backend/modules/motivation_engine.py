"""
Motivation Engine - Generates motivational dialogues and adaptive suggestions
Includes tone adaptation rules, motivational messages, and routine recommendations
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
from database import MoodEntry, Task, ProductivityEntry, TaskCompletion, FocusSession
from .analytics_engine import get_analytics_engine
from .focus_tracker import get_focus_tracker
from .ai_chat import response
from .safety_filter import check_and_filter


class MotivationEngine:
    """Generates motivational dialogues and adaptive suggestions"""
    
    def __init__(self):
        self.analytics = get_analytics_engine()
    
    def get_enhanced_tone(self, mood_score: Optional[int] = None, 
                         context: str = "general") -> Tuple[str, Dict[str, any]]:
        """
        Enhanced tone adaptation with more sophisticated rules
        
        Args:
            mood_score: Current mood score (1-10)
            context: Context of interaction ("general", "planning", "reflection", "motivation")
            
        Returns:
            Tuple of (tone_name, tone_config) where tone_config includes rate, volume, and phrasing style
        """
        if mood_score is None:
            mood_entry = MoodEntry.get_today()
            mood_score = mood_entry.mood_score if mood_entry else 5
        
        # Enhanced tone mapping with more granular ranges
        if mood_score >= 9:
            # Very high mood - enthusiastic
            return ("cheerful", {
                "rate": 290,
                "volume": 1.0,
                "phrasing_style": "enthusiastic",
                "greeting": "Wonderful!",
                "encouragement": "You're doing amazing!"
            })
        elif mood_score >= 7:
            # High mood - upbeat
            return ("cheerful", {
                "rate": 280,
                "volume": 1.0,
                "phrasing_style": "upbeat",
                "greeting": "Great!",
                "encouragement": "Keep up the great work!"
            })
        elif mood_score >= 5:
            # Medium mood - neutral/balanced
            return ("neutral", {
                "rate": 250,
                "volume": 1.0,
                "phrasing_style": "balanced",
                "greeting": "Alright,",
                "encouragement": "You've got this!"
            })
        elif mood_score >= 3:
            # Low mood - supportive
            return ("calm", {
                "rate": 210,
                "volume": 0.85,
                "phrasing_style": "supportive",
                "greeting": "I understand,",
                "encouragement": "Take it one step at a time."
            })
        else:
            # Very low mood - gentle
            return ("calm", {
                "rate": 200,
                "volume": 0.8,
                "phrasing_style": "gentle",
                "greeting": "I'm here for you,",
                "encouragement": "Remember, it's okay to take breaks."
            })
    
    def generate_motivational_message(self, context: Optional[str] = None) -> str:
        """
        Generate a motivational dialogue tailored to user context
        
        Args:
            context: Optional context ("task_completion", "low_productivity", "high_productivity", "low_mood", "reflection")
            
        Returns:
            Motivational message text
        """
        mood_entry = MoodEntry.get_today()
        mood_score = mood_entry.mood_score if mood_entry else 5
        
        # Get productivity data
        today = datetime.now().date().isoformat()
        daily_data = self.analytics.get_daily_aggregate(today)
        productivity_score = daily_data.get('productivity_score')
        
        # Get task completion data
        tasks_completed = daily_data.get('tasks_completed', 0)
        tasks_planned = daily_data.get('tasks_planned', 0)
        
        # Build context for AI
        context_prompt = f"""You are Kasane Teto, an empathetic AI companion. Generate a short, personalized motivational message.

User Context:
- Current Mood: {mood_score}/10{f" ({mood_entry.mood_text})" if mood_entry and mood_entry.mood_text else ""}
- Tasks Completed Today: {tasks_completed}/{tasks_planned}
- Productivity Score: {productivity_score:.1f}/100 if productivity_score else "Not calculated"
- Focus Hours: {daily_data.get('focus_hours', 0):.1f} hours

Context: {context or "general encouragement"}

Generate a motivational message that:
1. Acknowledges the user's current state
2. Provides appropriate encouragement based on mood and productivity
3. Is empathetic and supportive (especially if mood is low)
4. Celebrates achievements (if any)
5. Offers gentle guidance without being pushy
6. Keeps it concise (2-3 sentences max)
7. Adapts tone to mood (supportive if low, celebratory if high)

Important: If mood is persistently low (3 or below), gently suggest that professional help might be beneficial, but don't be clinical or diagnostic.

Format as a warm, conversational message."""

        # Save prompt to file for AI chat
        with open("data/client_question.txt", "w", encoding="utf-8") as f:
            f.write(context_prompt)
        
        # Get AI response
        ai_message = response(additional_context="")
        
        if not ai_message:
            # Fallback motivational message
            ai_message = self._generate_fallback_motivation(mood_score, tasks_completed, productivity_score)
        
        # Safety check
        is_safe, filtered_message, category = check_and_filter(ai_message)
        if not is_safe:
            # Use safe fallback if AI generates unsafe content
            return self._generate_fallback_motivation(mood_score, tasks_completed, productivity_score)
        
        return filtered_message
    
    def _generate_fallback_motivation(self, mood_score: int, tasks_completed: int, 
                                     productivity_score: Optional[float]) -> str:
        """Generate fallback motivational message"""
        if mood_score >= 7:
            if tasks_completed > 0:
                return f"You're feeling great today and you've completed {tasks_completed} task{'s' if tasks_completed > 1 else ''}! Keep up the amazing work!"
            else:
                return "You're in a great mood today! This is a perfect time to tackle your tasks. You've got this!"
        elif mood_score >= 5:
            if tasks_completed > 0:
                return f"Nice work completing {tasks_completed} task{'s' if tasks_completed > 1 else ''} today! Every step forward counts."
            else:
                return "You're doing okay. Remember, progress doesn't have to be perfect. Small steps are still steps forward."
        elif mood_score >= 3:
            if tasks_completed > 0:
                return f"I know things feel tough right now, but you still managed to complete {tasks_completed} task{'s' if tasks_completed > 1 else ''}. That's something to be proud of."
            else:
                return "I understand you're not feeling your best today. It's okay to take things slow. Be gentle with yourself."
        else:
            return "I'm here for you. Remember, it's okay to not be okay. If you're struggling, consider reaching out to someone you trust or a mental health professional. You don't have to go through this alone."
    
    def suggest_routine(self) -> str:
        """
        Suggest a routine based on user's recent patterns
        
        Returns:
            Routine suggestion text
        """
        # Get recent analytics
        trends = self.analytics.get_trends(days=7)
        weekly_data = self.analytics.get_weekly_aggregate()
        
        # Analyze patterns
        avg_focus_hours = trends.get('avg_focus_hours', 0)
        avg_productivity = trends.get('avg_productivity')
        avg_mood = trends.get('avg_mood')
        
        # Get focus session patterns
        focus_tracker = get_focus_tracker()
        recent_sessions = focus_tracker.get_recent_sessions(limit=10)
        
        # Analyze focus session durations
        session_durations = []
        for session in recent_sessions:
            if session.duration_minutes:
                session_durations.append(session.duration_minutes)
        
        avg_session_duration = sum(session_durations) / len(session_durations) if session_durations else 0
        
        # Build context for AI
        context_prompt = f"""You are Kasane Teto, an empathetic AI companion. Suggest a simple, personalized routine based on the user's recent patterns.

User's Recent Patterns (Last 7 Days):
- Average Focus Hours: {avg_focus_hours:.1f} hours/day
- Average Productivity: {avg_productivity:.1f}/100 if avg_productivity else "Not available"
- Average Mood: {avg_mood:.1f}/10 if avg_mood else "Not available"
- Average Focus Session Duration: {avg_session_duration:.1f} minutes
- Number of Focus Sessions: {len(recent_sessions)}

Generate a simple routine suggestion that:
1. References the user's own data (e.g., "Based on your recent patterns...")
2. Suggests a realistic routine (e.g., "Try 90-minute deep work sessions followed by 20-minute breaks")
3. Adapts to their patterns (if they work in shorter bursts, suggest shorter sessions)
4. Includes breaks and self-care
5. Keeps it simple and actionable (2-3 elements max)
6. Is encouraging and non-judgmental

Format as a friendly, conversational suggestion."""

        # Save prompt to file for AI chat
        with open("data/client_question.txt", "w", encoding="utf-8") as f:
            f.write(context_prompt)
        
        # Get AI response
        ai_suggestion = response(additional_context="")
        
        if not ai_suggestion:
            # Fallback routine suggestion
            ai_suggestion = self._generate_fallback_routine(avg_focus_hours, avg_session_duration)
        
        # Safety check
        is_safe, filtered_suggestion, category = check_and_filter(ai_suggestion)
        if not is_safe:
            return self._generate_fallback_routine(avg_focus_hours, avg_session_duration)
        
        return filtered_suggestion
    
    def _generate_fallback_routine(self, avg_focus_hours: float, avg_session_duration: float) -> str:
        """Generate fallback routine suggestion"""
        if avg_session_duration > 0:
            # Suggest based on their average session duration
            work_duration = int(avg_session_duration)
            break_duration = max(5, int(work_duration / 4))  # 25% break time
            
            return f"Based on your recent patterns, you tend to focus for about {work_duration} minutes at a time. Try scheduling {work_duration}-minute work sessions followed by {break_duration}-minute breaks. This matches your natural rhythm!"
        elif avg_focus_hours > 0:
            # Suggest based on daily focus hours
            return f"You've been averaging {avg_focus_hours:.1f} hours of focused work per day. Try breaking this into 2-3 focused sessions with breaks in between. This can help maintain your energy throughout the day."
        else:
            # Generic suggestion
            return "Try starting with 25-minute focused work sessions followed by 5-minute breaks. This Pomodoro technique can help build your focus gradually."
    
    def check_safety_guardrails(self, mood_score: Optional[int] = None, 
                                days_low_mood: int = 0) -> Tuple[bool, Optional[str]]:
        """
        Check safety guardrails and suggest professional help if needed
        
        Args:
            mood_score: Current mood score
            days_low_mood: Number of consecutive days with low mood
            
        Returns:
            Tuple of (should_suggest_help, suggestion_message)
        """
        if mood_score is None:
            mood_entry = MoodEntry.get_today()
            mood_score = mood_entry.mood_score if mood_entry else 5
        
        # Check for persistent low mood
        if days_low_mood >= 3 and mood_score <= 3:
            suggestion = (
                "I've noticed you've been feeling low for several days now. "
                "While I'm here to support you, I want to gently suggest that "
                "speaking with a mental health professional or someone you trust "
                "might be helpful. You don't have to go through difficult times alone. "
                "Remember, seeking help is a sign of strength, not weakness."
            )
            return (True, suggestion)
        
        # Check for very low mood
        if mood_score <= 2:
            suggestion = (
                "I'm concerned about how you're feeling right now. "
                "Please consider reaching out to someone you trust or a mental health professional. "
                "If you're in crisis, please contact a crisis helpline in your area. "
                "You matter, and there are people who want to help."
            )
            return (True, suggestion)
        
        return (False, None)
    
    def get_phrasing_template(self, tone_config: Dict[str, any], 
                              message_type: str = "encouragement") -> str:
        """
        Get phrasing template based on tone configuration
        
        Args:
            tone_config: Tone configuration from get_enhanced_tone()
            message_type: Type of message ("encouragement", "greeting", "reminder")
            
        Returns:
            Phrasing template string
        """
        phrasing_style = tone_config.get("phrasing_style", "balanced")
        
        templates = {
            "enthusiastic": {
                "encouragement": "You're absolutely crushing it!",
                "greeting": "Wonderful to see you!",
                "reminder": "Ready to tackle this? Let's go!"
            },
            "upbeat": {
                "encouragement": "Keep up the great work!",
                "greeting": "Great to see you!",
                "reminder": "You've got this!"
            },
            "balanced": {
                "encouragement": "You're doing well!",
                "greeting": "Hello there!",
                "reminder": "Remember to take breaks."
            },
            "supportive": {
                "encouragement": "Take it one step at a time.",
                "greeting": "I'm here for you.",
                "reminder": "Be gentle with yourself."
            },
            "gentle": {
                "encouragement": "It's okay to take things slow.",
                "greeting": "I'm here to support you.",
                "reminder": "Remember, self-care is important."
            }
        }
        
        return templates.get(phrasing_style, templates["balanced"]).get(
            message_type, 
            templates["balanced"][message_type]
        )


# Global motivation engine instance
_motivation_engine: Optional[MotivationEngine] = None


def get_motivation_engine() -> MotivationEngine:
    """Get or create global motivation engine instance"""
    global _motivation_engine
    if _motivation_engine is None:
        _motivation_engine = MotivationEngine()
    return _motivation_engine

