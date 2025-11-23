"""
Reflection Workflow - End-of-day prompts and guided reflection system
Integrates with journaling and analytics
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from database import JournalEntry, MoodEntry, ProductivityEntry, TaskCompletion
from .analytics_engine import get_analytics_engine
from .ai_chat import response
from database import get_database


class ReflectionWorkflow:
    """Manages end-of-day reflection prompts and guided reflections"""
    
    def generate_end_of_day_prompt(self) -> str:
        """
        Generate an end-of-day reflection prompt based on today's activity
        
        Returns:
            Reflection prompt text
        """
        analytics = get_analytics_engine()
        today = datetime.now().date().isoformat()
        daily_data = analytics.get_daily_aggregate(today)
        
        # Get today's mood
        mood_entry = MoodEntry.get_today()
        mood_score = mood_entry.mood_score if mood_entry else None
        mood_text = mood_entry.mood_text if mood_entry else "not recorded"
        
        # Get productivity entry
        productivity_entry = ProductivityEntry.get_by_date(today)
        productivity_score = productivity_entry.productivity_score if productivity_entry else None
        
        # Get completions
        completions = TaskCompletion.get_by_date(today)
        
        # Build context for reflection prompt
        productivity_str = f"{productivity_score:.1f}/100" if productivity_score else "Not calculated"
        mood_str = f"{mood_score}/10 ({mood_text})" if mood_score else "Not recorded"
        
        prompt_context = f"""Today's Summary:
- Tasks Completed: {daily_data['tasks_completed']} out of {daily_data['tasks_planned']} planned
- Productivity Score: {productivity_str}
- Focus Hours: {daily_data['focus_hours']:.1f} hours
- Mood: {mood_str}
- Focus Sessions: {daily_data['focus_sessions']}

Generate a warm, empathetic end-of-day reflection prompt that:
1. Acknowledges what the user accomplished today
2. Asks thoughtful questions about:
   - What went well today?
   - What challenges did they face?
   - How did their mood affect their productivity?
   - What would they like to improve tomorrow?
3. Encourages them to reflect on their day
4. Adapts tone based on their mood (supportive if low, celebratory if high)
5. Keeps it concise (2-3 questions max)

Format as a friendly conversation starter that invites reflection."""
        
        # Save prompt to file for AI chat
        with open("data/client_question.txt", "w", encoding="utf-8") as f:
            f.write(prompt_context)
        
        # Get AI-generated reflection prompt
        ai_prompt = response(additional_context="")
        
        if not ai_prompt:
            # Fallback prompt
            ai_prompt = self._generate_fallback_prompt(daily_data, mood_score, productivity_score)
        
        return ai_prompt
    
    def _generate_fallback_prompt(self, daily_data: Dict, mood_score: Optional[int], 
                                  productivity_score: Optional[float]) -> str:
        """Generate a fallback reflection prompt"""
        tasks_completed = daily_data['tasks_completed']
        tasks_planned = daily_data['tasks_planned']
        focus_hours = daily_data['focus_hours']
        
        prompt = "Good evening! Let's take a moment to reflect on your day.\n\n"
        
        if tasks_completed > 0:
            prompt += f"You completed {tasks_completed} task{'s' if tasks_completed > 1 else ''} today. "
        else:
            prompt += "It looks like today was a lighter day. "
        
        if focus_hours > 0:
            prompt += f"You spent {focus_hours:.1f} hour{'s' if focus_hours != 1 else ''} in focused work. "
        
        if mood_score:
            if mood_score >= 7:
                prompt += f"Your mood was quite positive ({mood_score}/10). "
            elif mood_score <= 4:
                prompt += f"You've been feeling a bit low today ({mood_score}/10). "
            else:
                prompt += f"Your mood was moderate today ({mood_score}/10). "
        
        prompt += "\n\nHere are some questions to reflect on:\n"
        prompt += "1. What's one thing that went well today?\n"
        prompt += "2. What challenge did you face, and how did you handle it?\n"
        prompt += "3. What would you like to focus on improving tomorrow?\n\n"
        prompt += "Take your time to think about these, and feel free to share your thoughts."
        
        return prompt
    
    def generate_guided_reflection_questions(self, focus_area: Optional[str] = None) -> List[str]:
        """
        Generate guided reflection questions based on focus area
        
        Args:
            focus_area: Optional focus area (e.g., "productivity", "mood", "tasks")
            
        Returns:
            List of reflection questions
        """
        analytics = get_analytics_engine()
        today = datetime.now().date().isoformat()
        daily_data = analytics.get_daily_aggregate(today)
        
        questions = []
        
        if focus_area == "productivity" or focus_area is None:
            if daily_data['tasks_completed'] > 0:
                questions.append("What helped you stay productive today?")
                questions.append("Which task completion are you most proud of?")
            else:
                questions.append("What prevented you from completing tasks today?")
                questions.append("What could help you be more productive tomorrow?")
        
        if focus_area == "mood" or focus_area is None:
            mood_entry = MoodEntry.get_today()
            if mood_entry:
                if mood_entry.mood_score >= 7:
                    questions.append("What contributed to your positive mood today?")
                elif mood_entry.mood_score <= 4:
                    questions.append("What's been weighing on you today?")
                    questions.append("What's one small thing that could help improve your mood?")
                else:
                    questions.append("How did your mood affect your day?")
        
        if focus_area == "focus" or focus_area is None:
            if daily_data['focus_hours'] > 0:
                questions.append(f"You spent {daily_data['focus_hours']:.1f} hours in focused work. What helped you maintain focus?")
            else:
                questions.append("What distractions did you face today?")
                questions.append("How can you create better focus time tomorrow?")
        
        if focus_area == "tasks" or focus_area is None:
            completions = TaskCompletion.get_by_date(today)
            if completions:
                avg_focus = daily_data.get('avg_focus_score')
                if avg_focus:
                    questions.append(f"Your average focus score was {avg_focus:.1f}/10. What tasks required the most focus?")
        
        # If no specific questions generated, add general ones
        if not questions:
            questions = [
                "What's one thing you learned about yourself today?",
                "What are you grateful for today?",
                "What would make tomorrow even better?"
            ]
        
        return questions
    
    def save_reflection(self, reflection_text: str, reflection_type: str = "reflection") -> JournalEntry:
        """
        Save a reflection as a journal entry
        
        Args:
            reflection_text: The reflection text
            reflection_type: Type of reflection (default: "reflection")
            
        Returns:
            Created JournalEntry
        """
        return JournalEntry.create(
            content=reflection_text,
            entry_type=reflection_type
        )
    
    def generate_daily_summary(self) -> str:
        """
        Generate a daily summary for reflection
        
        Returns:
            Formatted daily summary text
        """
        analytics = get_analytics_engine()
        today = datetime.now().date().isoformat()
        daily_data = analytics.get_daily_aggregate(today)
        
        summary = f"📊 Daily Summary - {today}\n\n"
        
        # Tasks
        summary += f"✅ Tasks: {daily_data['tasks_completed']}/{daily_data['tasks_planned']} completed"
        if daily_data['tasks_planned'] > 0:
            completion_rate = (daily_data['tasks_completed'] / daily_data['tasks_planned']) * 100
            summary += f" ({completion_rate:.1f}%)\n"
        else:
            summary += "\n"
        
        # Productivity
        if daily_data['productivity_score']:
            summary += f"📈 Productivity Score: {daily_data['productivity_score']:.1f}/100\n"
        
        # Focus
        summary += f"🎯 Focus Hours: {daily_data['focus_hours']:.1f} hours\n"
        summary += f"🔋 Focus Sessions: {daily_data['focus_sessions']}\n"
        
        # Mood
        if daily_data['mood_score']:
            summary += f"😊 Mood: {daily_data['mood_score']}/10"
            mood_entry = MoodEntry.get_today()
            if mood_entry and mood_entry.mood_text:
                summary += f" ({mood_entry.mood_text})"
            summary += "\n"
        
        # Focus score
        if daily_data['avg_focus_score']:
            summary += f"💪 Average Focus Score: {daily_data['avg_focus_score']:.1f}/10\n"
        
        # Task duration
        if daily_data['avg_task_duration_minutes']:
            duration_hours = daily_data['avg_task_duration_minutes'] / 60
            summary += f"⏱️  Average Task Duration: {duration_hours:.1f} hours\n"
        
        summary += "\n"
        
        return summary
    
    def start_reflection_workflow(self, use_voice: bool = False) -> str:
        """
        Start a complete reflection workflow
        
        Args:
            use_voice: Whether to use voice input (STT)
            
        Returns:
            Reflection prompt text
        """
        # Generate daily summary
        summary = self.generate_daily_summary()
        
        # Generate reflection prompt
        prompt = self.generate_end_of_day_prompt()
        
        # Combine summary and prompt
        full_prompt = f"{summary}\n\n{prompt}"
        
        return full_prompt
    
    def process_reflection_response(self, reflection_text: str, 
                                   reflection_type: str = "reflection") -> JournalEntry:
        """
        Process and save a reflection response
        
        Args:
            reflection_text: The reflection text from user
            reflection_type: Type of reflection
            
        Returns:
            Created JournalEntry
        """
        # Add timestamp and context
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_reflection = f"[{timestamp}] {reflection_text}"
        
        return self.save_reflection(formatted_reflection, reflection_type)


# Global reflection workflow instance
_reflection_workflow: Optional[ReflectionWorkflow] = None


def get_reflection_workflow() -> ReflectionWorkflow:
    """Get or create global reflection workflow instance"""
    global _reflection_workflow
    if _reflection_workflow is None:
        _reflection_workflow = ReflectionWorkflow()
    return _reflection_workflow

