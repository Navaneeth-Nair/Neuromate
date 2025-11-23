"""
Command Handler - Handles voice commands and connects parser to database
"""
from .command_parser import parse_command, CommandIntent
from database import Task, MoodEntry, JournalEntry
from .conversation_context import get_context
from .ai_chat import response
from .ai_planner import get_planner
from .productivity_tracker import get_productivity_tracker
from .focus_tracker import get_focus_tracker
from .reflection_workflow import get_reflection_workflow
from .dashboard import get_dashboard
from .motivation_engine import get_motivation_engine
from . import tts as speak

# Ensure database is initialized
from database import db_init


class CommandHandler:
    """Handles parsed commands and executes appropriate actions"""
    
    def __init__(self):
        self.last_action = None  # For undo functionality
    
    def handle_command(self, text: str) -> str:
        """
        Handle a voice command
        
        Args:
            text: The transcribed voice command
            
        Returns:
            Response text to speak
        """
        # Parse the command
        intent, entities = parse_command(text)
        print(f"[DEBUG] Parsed intent: {intent}, entities: {entities}")
        
        # Save command as journal entry
        JournalEntry.create(text, entry_type="voice_command")
        
        # Handle based on intent
        if intent == CommandIntent.ADD_TASK:
            return self._handle_add_task(entities)
        elif intent == CommandIntent.SHOW_TASKS:
            return self._handle_show_tasks()
        elif intent == CommandIntent.COMPLETE_TASK:
            return self._handle_complete_task(entities)
        elif intent == CommandIntent.DELETE_TASK:
            return self._handle_delete_task(entities)
        elif intent == CommandIntent.SET_MOOD:
            return self._handle_set_mood(entities)
        elif intent == CommandIntent.CHECK_MOOD:
            return self._handle_check_mood()
        elif intent == CommandIntent.GET_PLAN:
            return self._handle_get_plan(entities)
        elif intent == CommandIntent.SUGGEST_TASKS:
            return self._handle_suggest_tasks()
        elif intent == CommandIntent.WHAT_SHOULD_I_DO:
            return self._handle_what_should_i_do()
        elif intent == CommandIntent.CHECK_PRODUCTIVITY:
            return self._handle_check_productivity()
        elif intent == CommandIntent.PRODUCTIVITY_INSIGHTS:
            return self._handle_productivity_insights()
        elif intent == CommandIntent.START_FOCUS:
            return self._handle_start_focus(entities)
        elif intent == CommandIntent.END_FOCUS:
            return self._handle_end_focus()
        elif intent == CommandIntent.REFLECT:
            return self._handle_reflect()
        elif intent == CommandIntent.DAILY_SUMMARY:
            return self._handle_daily_summary()
        elif intent == CommandIntent.SHOW_DASHBOARD:
            return self._handle_show_dashboard()
        elif intent == CommandIntent.MOTIVATION:
            return self._handle_motivation()
        elif intent == CommandIntent.SUGGEST_ROUTINE:
            return self._handle_suggest_routine()
        elif intent == CommandIntent.REPEAT:
            return self._handle_repeat()
        elif intent == CommandIntent.UNDO:
            return self._handle_undo()
        else:
            # General question - use AI chat
            return self._handle_general_question(text)
    
    def _handle_add_task(self, entities: dict) -> str:
        """Handle add task command"""
        title = entities.get("title", "")
        if not title:
            return "I didn't catch the task name. Could you repeat it?"
        
        due_date = entities.get("due_date")
        due_time = entities.get("due_time", "")
        
        # Create task
        task = Task.create(title=title, description="", due_date=due_date)
        self.last_action = ("add_task", task.id)
        
        # Build confirmation message
        message = f"I've added the task: {title}"
        if due_date:
            message += f" for {due_date}"
        if due_time:
            message += f" at {due_time}"
        message += "."
        
        return message
    
    def _handle_show_tasks(self) -> str:
        """Handle show tasks command"""
        tasks = Task.get_all(status="pending")
        
        if not tasks:
            response = "You don't have any pending tasks right now."
        elif len(tasks) == 1:
            response = f"You have one task: {tasks[0].title}"
        else:
            message = f"You have {len(tasks)} tasks: "
            task_names = [task.title for task in tasks[:5]]  # Limit to 5
            message += ", ".join(task_names)
            
            if len(tasks) > 5:
                message += f", and {len(tasks) - 5} more"
            response = message
        
        # Write response to file for TTS
        try:
            with open("data/response.txt", 'w', encoding='utf-8') as f:
                f.write(response)
        except Exception as e:
            print(f"Warning: Could not write response to file: {e}")
        
        return response
    
    def _handle_complete_task(self, entities: dict) -> str:
        """Handle complete task command"""
        task_name = entities.get("task_name", "").lower()
        
        if not task_name:
            return "Which task would you like to complete?"
        
        # Find task by name
        tasks = Task.get_all(status="pending")
        matching_tasks = [t for t in tasks if task_name in t.title.lower()]
        
        if not matching_tasks:
            return f"I couldn't find a task matching '{task_name}'."
        
        if len(matching_tasks) == 1:
            task = matching_tasks[0]
            task.complete()
            self.last_action = ("complete_task", task.id)
            
            # Update productivity tracking
            tracker = get_productivity_tracker()
            tracker.update_today()
            
            return f"Great! I've marked '{task.title}' as completed."
        else:
            return f"I found multiple tasks matching that. Could you be more specific?"
    
    def _handle_delete_task(self, entities: dict) -> str:
        """Handle delete task command"""
        task_name = entities.get("task_name", "").lower()
        
        if not task_name:
            return "Which task would you like to delete?"
        
        # Find task by name
        tasks = Task.get_all()
        matching_tasks = [t for t in tasks if task_name in t.title.lower()]
        
        if not matching_tasks:
            return f"I couldn't find a task matching '{task_name}'."
        
        if len(matching_tasks) == 1:
            task = matching_tasks[0]
            task.delete()
            self.last_action = ("delete_task", task.id)
            return f"I've deleted the task '{task.title}'."
        else:
            return f"I found multiple tasks matching that. Could you be more specific?"
    
    def _handle_set_mood(self, entities: dict) -> str:
        """Handle set mood command"""
        mood_score = entities.get("mood")
        mood_text = entities.get("mood_text", "")
        
        if mood_score is None:
            # Try to get mood from text using AI
            return "I'm not sure how to interpret that mood. Could you tell me on a scale of 1 to 10?"
        
        # Create mood entry
        mood_entry = MoodEntry.create(mood_score=mood_score, mood_text=mood_text)
        self.last_action = ("set_mood", mood_entry.id)
        
        # Generate response based on mood
        if mood_score >= 7:
            return f"That's wonderful! I'm glad you're feeling good. I've recorded your mood as {mood_score} out of 10."
        elif mood_score >= 5:
            return f"Thanks for sharing. I've recorded your mood as {mood_score} out of 10."
        else:
            return f"I'm here for you. I've recorded your mood as {mood_score} out of 10. Is there anything I can help with?"
    
    def _handle_check_mood(self) -> str:
        """Handle check mood command"""
        mood_entry = MoodEntry.get_today()
        
        if not mood_entry:
            return "You haven't logged your mood today. How are you feeling?"
        
        return f"Your mood today is {mood_entry.mood_score} out of 10. {mood_entry.mood_text if mood_entry.mood_text else ''}"
    
    def _handle_repeat(self) -> str:
        """Handle repeat command"""
        context = get_context()
        last_response = context.get_last_response()
        
        if last_response:
            return last_response
        else:
            return "I don't have anything to repeat."
    
    def _handle_undo(self) -> str:
        """Handle undo command"""
        if not self.last_action:
            return "There's nothing to undo."
        
        action_type, action_id = self.last_action
        
        if action_type == "add_task":
            try:
                task = Task.get_by_id(action_id)
                if task:
                    task.delete()
                    self.last_action = None
                    return f"I've undone adding the task '{task.title}'."
            except:
                pass
        elif action_type == "complete_task":
            try:
                task = Task.get_by_id(action_id)
                if task:
                    task.status = "pending"
                    task.update()
                    self.last_action = None
                    return f"I've undone completing the task '{task.title}'."
            except:
                pass
        
        return "I couldn't undo that action."
    
    def _handle_get_plan(self, entities: dict) -> str:
        """Handle get plan command"""
        planner = get_planner()
        time_of_day = entities.get("time_of_day")
        
        # Generate daily plan
        plan = planner.generate_daily_plan(time_of_day=time_of_day)
        
        # Determine tone based on mood
        mood_entry = MoodEntry.get_today()
        tone = "focused"  # Default for planning
        if mood_entry:
            if mood_entry.mood_score >= 7:
                tone = "cheerful"
            elif mood_entry.mood_score < 5:
                tone = "calm"
        
        # Save plan to response file for TTS
        with open("data/response.txt", 'w', encoding='utf-8') as f:
            f.write(plan)
        
        # Speak with appropriate tone
        speak.speak(text=plan, tone=tone)
        
        return plan
    
    def _handle_suggest_tasks(self) -> str:
        """Handle suggest tasks command"""
        planner = get_planner()
        tasks = Task.get_all(status="pending")
        
        if not tasks:
            return "You don't have any pending tasks. Great job!"
        
        # Get mood for prioritization
        mood_entry = MoodEntry.get_today()
        mood_score = mood_entry.mood_score if mood_entry else 5
        
        # Get suggested order
        suggested_tasks = planner.suggest_task_order(tasks, mood_score)
        
        # Build response
        response_parts = ["Here are your tasks in suggested order:"]
        for i, task in enumerate(suggested_tasks[:5], 1):
            response_parts.append(f"{i}. {task.title}")
            if task.due_date:
                response_parts.append(f"   Due: {task.due_date}")
        
        if len(suggested_tasks) > 5:
            response_parts.append(f"\nYou have {len(suggested_tasks) - 5} more tasks.")
        
        response_text = "\n".join(response_parts)
        
        # Determine tone
        tone = "focused"
        if mood_entry:
            if mood_entry.mood_score >= 7:
                tone = "cheerful"
            elif mood_entry.mood_score < 5:
                tone = "calm"
        
        # Speak
        speak.speak(text=response_text, tone=tone)
        
        return response_text
    
    def _handle_what_should_i_do(self) -> str:
        """Handle what should I do command - same as get plan"""
        return self._handle_get_plan({})
    
    def _handle_check_productivity(self) -> str:
        """Handle check productivity command"""
        tracker = get_productivity_tracker()
        entry = tracker.get_today()
        
        if not entry:
            # Calculate for today
            entry = tracker.update_today()
        
        mood_entry = MoodEntry.get_today()
        mood_score = mood_entry.mood_score if mood_entry else 5
        
        response_parts = [f"Today's productivity score: {entry.productivity_score:.1f} out of 100."]
        response_parts.append(f"You've completed {entry.tasks_completed} out of {entry.tasks_total} tasks.")
        
        if entry.productivity_score >= 70:
            response_parts.append("Excellent work today!")
        elif entry.productivity_score >= 50:
            response_parts.append("Good progress!")
        else:
            response_parts.append("Keep going, you're doing great!")
        
        response_text = " ".join(response_parts)
        
        # Determine tone
        tone = "cheerful" if mood_score >= 7 else "calm" if mood_score < 5 else "neutral"
        speak.speak(text=response_text, tone=tone)
        
        return response_text
    
    def _handle_productivity_insights(self) -> str:
        """Handle productivity insights command"""
        tracker = get_productivity_tracker()
        correlation = tracker.get_mood_productivity_correlation(days=30)
        
        mood_entry = MoodEntry.get_today()
        mood_score = mood_entry.mood_score if mood_entry else 5
        
        response_parts = ["Here are your productivity insights:"]
        response_parts.append(f"Correlation between mood and productivity: {correlation['correlation']:.2f}")
        
        if correlation['high_mood_days'] > 0:
            response_parts.append(
                f"On high mood days, your average productivity is {correlation['avg_productivity_high_mood']:.1f}"
            )
        
        if correlation['low_mood_days'] > 0:
            response_parts.append(
                f"On low mood days, your average productivity is {correlation['avg_productivity_low_mood']:.1f}"
            )
        
        response_parts.append(correlation['insights'])
        
        response_text = ". ".join(response_parts) + "."
        
        # Determine tone
        tone = "focused"
        if mood_entry:
            if mood_entry.mood_score >= 7:
                tone = "cheerful"
            elif mood_entry.mood_score < 5:
                tone = "calm"
        
        speak.speak(text=response_text, tone=tone)
        
        return response_text
    
    def _handle_start_focus(self, entities: dict) -> str:
        """Handle start focus session command"""
        focus_tracker = get_focus_tracker()
        
        # Check if there's already an active session
        active_session = focus_tracker.get_active_session()
        if active_session:
            return f"You already have an active focus session that started at {active_session.started_at}. End it first before starting a new one."
        
        # Try to find task if mentioned
        task_id = None
        task_name = entities.get("task_name", "")
        if task_name:
            tasks = Task.get_all(status="pending")
            matching_tasks = [t for t in tasks if task_name.lower() in t.title.lower()]
            if matching_tasks:
                task_id = matching_tasks[0].id
        
        try:
            session = focus_tracker.start_session(task_id=task_id)
            response_text = "Focus session started! I'll track your focus time."
            if task_id:
                response_text += f" Working on task: {matching_tasks[0].title}"
        except ValueError as e:
            response_text = str(e)
        
        # Write response to file for TTS
        try:
            with open("data/response.txt", 'w', encoding='utf-8') as f:
                f.write(response_text)
        except Exception as e:
            print(f"Warning: Could not write response to file: {e}")
        
        return response_text
    
    def _handle_end_focus(self) -> str:
        """Handle end focus session command"""
        focus_tracker = get_focus_tracker()
        
        active_session = focus_tracker.get_active_session()
        if not active_session:
            response_text = "You don't have an active focus session."
        else:
            ended_session = focus_tracker.end_session()
            if ended_session:
                duration_minutes = ended_session.duration_minutes or 0
                duration_hours = duration_minutes / 60
                response_text = f"Focus session ended! You focused for {duration_minutes:.1f} minutes ({duration_hours:.2f} hours). Great work!"
            else:
                response_text = "Could not end focus session."
        
        # Write response to file for TTS
        try:
            with open("data/response.txt", 'w', encoding='utf-8') as f:
                f.write(response_text)
        except Exception as e:
            print(f"Warning: Could not write response to file: {e}")
        
        return response_text
    
    def _handle_reflect(self) -> str:
        """Handle reflection command"""
        reflection_workflow = get_reflection_workflow()
        
        try:
            prompt = reflection_workflow.start_reflection_workflow()
            response_text = prompt
        except Exception as e:
            response_text = f"I encountered an error generating your reflection prompt: {str(e)}"
        
        # Write response to file for TTS
        try:
            with open("data/response.txt", 'w', encoding='utf-8') as f:
                f.write(response_text)
        except Exception as e:
            print(f"Warning: Could not write response to file: {e}")
        
        return response_text
    
    def _handle_daily_summary(self) -> str:
        """Handle daily summary command"""
        reflection_workflow = get_reflection_workflow()
        
        try:
            summary = reflection_workflow.generate_daily_summary()
            response_text = summary
        except Exception as e:
            response_text = f"I encountered an error generating your daily summary: {str(e)}"
        
        # Write response to file for TTS
        try:
            with open("data/response.txt", 'w', encoding='utf-8') as f:
                f.write(response_text)
        except Exception as e:
            print(f"Warning: Could not write response to file: {e}")
        
        return response_text
    
    def _handle_show_dashboard(self) -> str:
        """Handle show dashboard command"""
        dashboard = get_dashboard()
        
        try:
            # Display dashboard (this will print to console)
            dashboard.display_full_dashboard()
            response_text = "Dashboard displayed! Check your console to see the full analytics."
        except Exception as e:
            response_text = f"I encountered an error displaying the dashboard: {str(e)}"
        
        # Write response to file for TTS
        try:
            with open("data/response.txt", 'w', encoding='utf-8') as f:
                f.write(response_text)
        except Exception as e:
            print(f"Warning: Could not write response to file: {e}")
        
        return response_text
    
    def _handle_motivation(self) -> str:
        """Handle motivation command"""
        motivation_engine = get_motivation_engine()
        
        # Check safety guardrails first
        mood_entry = MoodEntry.get_today()
        mood_score = mood_entry.mood_score if mood_entry else 5
        
        # Count consecutive low mood days
        days_low_mood = 0
        if mood_score <= 3:
            # Check recent mood entries
            recent_moods = MoodEntry.get_recent(limit=7)
            for mood in recent_moods:
                if mood.mood_score <= 3:
                    days_low_mood += 1
                else:
                    break
        
        should_suggest_help, help_message = motivation_engine.check_safety_guardrails(
            mood_score, days_low_mood
        )
        
        if should_suggest_help:
            response_text = help_message
        else:
            # Generate motivational message
            try:
                response_text = motivation_engine.generate_motivational_message()
            except Exception as e:
                response_text = f"I'm here to support you. Remember, every small step forward counts."
        
        # Get enhanced tone
        tone_name, tone_config = motivation_engine.get_enhanced_tone(mood_score)
        
        # Write response to file for TTS
        try:
            with open("data/response.txt", 'w', encoding='utf-8') as f:
                f.write(response_text)
        except Exception as e:
            print(f"Warning: Could not write response to file: {e}")
        
        # Speak with appropriate tone
        speak.speak(text=response_text, tone=tone_name)
        
        return response_text
    
    def _handle_suggest_routine(self) -> str:
        """Handle suggest routine command"""
        motivation_engine = get_motivation_engine()
        
        try:
            routine_suggestion = motivation_engine.suggest_routine()
            response_text = routine_suggestion
        except Exception as e:
            response_text = "Try breaking your work into focused sessions with breaks in between. This can help maintain your energy throughout the day."
        
        # Get tone based on mood
        mood_entry = MoodEntry.get_today()
        mood_score = mood_entry.mood_score if mood_entry else 5
        tone_name, _ = motivation_engine.get_enhanced_tone(mood_score)
        
        # Write response to file for TTS
        try:
            with open("data/response.txt", 'w', encoding='utf-8') as f:
                f.write(response_text)
        except Exception as e:
            print(f"Warning: Could not write response to file: {e}")
        
        # Speak with appropriate tone
        speak.speak(text=response_text, tone=tone_name)
        
        return response_text
    
    def _handle_general_question(self, text: str) -> str:
        """Handle general questions using AI"""
        # Get task list for context
        tasks = Task.get_all(status="pending")
        task_context = ""
        if tasks:
            task_list = "\n".join([f"- {t.title}" for t in tasks[:5]])
            task_context = f"User's current tasks:\n{task_list}\n\n"
        
        # Get mood context
        mood_entry = MoodEntry.get_today()
        mood_context = ""
        if mood_entry:
            mood_context = f"User's mood today: {mood_entry.mood_score}/10 ({mood_entry.mood_text})\n\n"
        
        additional_context = task_context + mood_context
        
        # Get AI response
        ai_response = response(additional_context=additional_context)
        
        # Ensure response is written to file for TTS
        if ai_response:
            try:
                with open("data/response.txt", 'w', encoding='utf-8') as f:
                    f.write(ai_response)
            except Exception as e:
                print(f"Warning: Could not write response to file: {e}")
            return ai_response
        else:
            error_msg = "I'm sorry, I couldn't generate a response. Please check your API key or try again."
            try:
                with open("data/response.txt", 'w', encoding='utf-8') as f:
                    f.write(error_msg)
            except:
                pass
            return error_msg


# Global handler instance
_handler = CommandHandler()


def handle_command(text: str) -> str:
    """Convenience function to handle a command"""
    return _handler.handle_command(text)

