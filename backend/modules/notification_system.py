"""
Adaptive Notification System - Mood-based notification scheduling and frequency
Provides soft reminders when stressed, adjusts tone and timing based on mood
Includes Redis queue for async notification processing
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Callable
from database import MoodEntry, Task
from database import get_database
from . import tts as speak_module


class NotificationScheduler:
    """Manages adaptive notifications based on mood and task status"""
    
    def __init__(self):
        self.notification_callbacks: List[Callable] = []
        self.last_notification_time: Optional[datetime] = None
        self.notification_settings = {
            "enabled": True,
            "min_interval_minutes": 30,  # Minimum time between notifications
            "low_mood_interval_minutes": 60,  # Longer interval for low mood
            "high_mood_interval_minutes": 20,  # Shorter interval for high mood
        }
    
    def should_send_notification(self) -> bool:
        """
        Determine if a notification should be sent based on mood and timing
        
        Returns:
            True if notification should be sent
        """
        if not self.notification_settings["enabled"]:
            return False
        
        mood_entry = MoodEntry.get_today()
        mood_score = mood_entry.mood_score if mood_entry else 5
        
        # Determine interval based on mood
        if mood_score < 5:
            interval_minutes = self.notification_settings["low_mood_interval_minutes"]
        elif mood_score >= 7:
            interval_minutes = self.notification_settings["high_mood_interval_minutes"]
        else:
            interval_minutes = self.notification_settings["min_interval_minutes"]
        
        # Check if enough time has passed
        if self.last_notification_time:
            time_since = datetime.now() - self.last_notification_time
            if time_since < timedelta(minutes=interval_minutes):
                return False
        
        return True
    
    def send_task_reminder(self, task: Optional[Task] = None, custom_message: Optional[str] = None, use_queue: bool = True):
        """
        Send a task reminder notification (with optional Redis queue support)
        
        Args:
            task: Task to remind about (if None, uses next priority task)
            custom_message: Custom message to speak
            use_queue: If True and Redis available, queue notification instead of immediate send
        """
        if not self.should_send_notification():
            return
        
        mood_entry = MoodEntry.get_today()
        mood_score = mood_entry.mood_score if mood_entry else 5
        
        # Determine tone based on mood
        if mood_score < 5:
            tone = "calm"  # Softer, gentler tone for low mood
        elif mood_score >= 7:
            tone = "cheerful"  # Upbeat tone for high mood
        else:
            tone = "neutral"
        
        # Get message
        if custom_message:
            message = custom_message
        elif task:
            message = self._generate_task_reminder_message(task, mood_score)
        else:
            # Get next priority task
            tasks = Task.get_all(status="pending")
            if not tasks:
                return  # No tasks to remind about
            
            # Sort by priority and due date
            sorted_tasks = sorted(tasks, key=lambda t: (
                t.priority if t.priority else 5,
                t.due_date if t.due_date else "9999-12-31"
            ), reverse=True)
            
            task = sorted_tasks[0]
            message = self._generate_task_reminder_message(task, mood_score)
        
        # Try to use Redis queue if available
        db = get_database()
        redis_client = db.get_redis()
        
        if use_queue and redis_client and redis_client.is_connected():
            # Queue notification for async processing
            notification = {
                "type": "task_reminder",
                "message": message,
                "tone": tone,
                "task_id": task.id if task else None,
                "timestamp": datetime.now().isoformat()
            }
            redis_client.push_notification(notification)
        else:
            # Immediate notification
            speak_module.speak(text=message, tone=tone)
        
        # Update last notification time
        self.last_notification_time = datetime.now()
    
    def process_notification_queue(self):
        """Process pending notifications from Redis queue"""
        db = get_database()
        redis_client = db.get_redis()
        
        if not redis_client or not redis_client.is_connected():
            return
        
        # Process up to 5 notifications at a time
        for _ in range(5):
            notification = redis_client.pop_notification()
            if not notification:
                break
            
            try:
                message = notification.get("message", "")
                tone = notification.get("tone", "neutral")
                speak_module.speak(text=message, tone=tone)
            except Exception as e:
                print(f"Error processing notification: {e}")
    
    def _generate_task_reminder_message(self, task: Task, mood_score: int) -> str:
        """Generate a reminder message appropriate for the mood"""
        if mood_score < 5:
            # Low mood - gentle, supportive reminder
            messages = [
                f"Just a gentle reminder: {task.title}",
                f"When you're ready, you might want to work on {task.title}",
                f"Remember {task.title}? No pressure, just whenever you feel up to it.",
            ]
        elif mood_score >= 7:
            # High mood - energetic, encouraging reminder
            messages = [
                f"Hey! Don't forget about {task.title}",
                f"Quick reminder: {task.title} is waiting for you",
                f"You're doing great! How about tackling {task.title}?",
            ]
        else:
            # Medium mood - neutral reminder
            messages = [
                f"Reminder: {task.title}",
                f"Don't forget: {task.title}",
                f"Task reminder: {task.title}",
            ]
        
        import random
        base_message = random.choice(messages)
        
        # Add deadline info if available
        if task.due_date:
            try:
                due_date = datetime.fromisoformat(task.due_date).date()
                today = datetime.now().date()
                days_until = (due_date - today).days
                
                if days_until < 0:
                    base_message += " (This is overdue)"
                elif days_until == 0:
                    base_message += " (Due today)"
                elif days_until <= 2:
                    base_message += f" (Due in {days_until} days)"
            except:
                pass
        
        return base_message
    
    def send_break_reminder(self):
        """Send a break reminder (especially important for low mood)"""
        if not self.should_send_notification():
            return
        
        mood_entry = MoodEntry.get_today()
        mood_score = mood_entry.mood_score if mood_entry else 5
        
        if mood_score < 5:
            message = "You've been working hard. How about taking a short break? You deserve it."
            tone = "calm"
        elif mood_score >= 7:
            message = "Great work! Remember to take breaks to maintain your energy."
            tone = "cheerful"
        else:
            message = "Consider taking a short break to recharge."
            tone = "neutral"
        
        speak_module.speak(text=message, tone=tone)
        self.last_notification_time = datetime.now()
    
    def send_mood_check_reminder(self):
        """Send a reminder to check in with mood (if no mood entry today)"""
        mood_entry = MoodEntry.get_today()
        if mood_entry:
            return  # Already checked in today
        
        if not self.should_send_notification():
            return
        
        current_hour = datetime.now().hour
        
        # Only remind during reasonable hours (9 AM - 9 PM)
        if 9 <= current_hour < 21:
            message = "How are you feeling today? Let me know your mood when you have a moment."
            speak_module.speak(text=message, tone="neutral")
            self.last_notification_time = datetime.now()
    
    def send_productivity_summary(self):
        """Send end-of-day productivity summary"""
        if not self.should_send_notification():
            return
        
        from .productivity_tracker import get_productivity_tracker
        
        tracker = get_productivity_tracker()
        entry = tracker.get_today()
        
        if entry:
            mood_entry = MoodEntry.get_today()
            mood_score = mood_entry.mood_score if mood_entry else 5
            
            tone = "cheerful" if mood_score >= 7 else "calm" if mood_score < 5 else "neutral"
            
            message = f"Today you completed {entry.tasks_completed} out of {entry.tasks_total} tasks. "
            message += f"Your productivity score is {entry.productivity_score:.1f} out of 100."
            
            if entry.productivity_score >= 70:
                message += " Excellent work today!"
            elif entry.productivity_score >= 50:
                message += " Good progress!"
            else:
                message += " Every day is a new opportunity."
            
            speak_module.speak(text=message, tone=tone)
            self.last_notification_time = datetime.now()
    
    def enable(self):
        """Enable notifications"""
        self.notification_settings["enabled"] = True
    
    def disable(self):
        """Disable notifications"""
        self.notification_settings["enabled"] = False
    
    def set_interval(self, mood_score: int, interval_minutes: int):
        """
        Set notification interval for a specific mood range
        
        Args:
            mood_score: Mood score threshold
            interval_minutes: Minutes between notifications
        """
        if mood_score < 5:
            self.notification_settings["low_mood_interval_minutes"] = interval_minutes
        elif mood_score >= 7:
            self.notification_settings["high_mood_interval_minutes"] = interval_minutes
        else:
            self.notification_settings["min_interval_minutes"] = interval_minutes


# Global notification scheduler instance
_notification_scheduler = NotificationScheduler()


def get_notification_scheduler() -> NotificationScheduler:
    """Get the global notification scheduler instance"""
    return _notification_scheduler

