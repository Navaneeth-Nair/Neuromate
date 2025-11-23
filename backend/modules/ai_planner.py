"""
AI Planning Assistant - Generates daily plans and task prioritization
Includes Redis caching for improved performance
"""
from database import Task, MoodEntry
from .ai_chat import response
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from database import get_database


class AIPlanner:
    """AI-powered planning assistant"""
    
    def generate_daily_plan(self, time_of_day: Optional[str] = None) -> str:
        """
        Generate a daily plan based on tasks, mood, and constraints (with Redis caching)
        
        Args:
            time_of_day: "morning", "afternoon", "evening", or None for full day
            
        Returns:
            Formatted plan text
        """
        db = get_database()
        redis_client = db.get_redis()
        
        # Get current time context
        current_hour = datetime.now().hour
        if time_of_day is None:
            if current_hour < 12:
                time_of_day = "morning"
            elif current_hour < 17:
                time_of_day = "afternoon"
            else:
                time_of_day = "evening"
        
        # Check Redis cache (1 hour TTL for daily plans)
        today = datetime.now().date().isoformat()
        cache_key = f"plan:{today}:{time_of_day}"
        if redis_client:
            cached_plan = redis_client.get(cache_key)
            if cached_plan:
                return cached_plan
        
        # Get current tasks
        tasks = Task.get_all(status="pending")
        
        if not tasks:
            return "You don't have any pending tasks. Great job staying on top of things!"
        
        # Get today's mood
        mood_entry = MoodEntry.get_today()
        mood_score = mood_entry.mood_score if mood_entry else 5
        mood_text = mood_entry.mood_text if mood_entry else "neutral"
        
        # Build context for AI
        task_list = "\n".join([
            f"- {task.title} (Priority: {task.priority}/10, Due: {task.due_date or 'No deadline'})"
            for task in tasks
        ])
        
        planning_prompt = f"""You are Kasane Teto, an empathetic AI planning assistant. Generate a personalized daily plan for the user.

User's Current Mood: {mood_score}/10 ({mood_text})
Time of Day: {time_of_day}
Current Time: {datetime.now().strftime('%I:%M %p')}

Pending Tasks:
{task_list}

Please create a thoughtful, prioritized plan for the {time_of_day}. Consider:
1. The user's mood - if they're feeling low, suggest lighter tasks first
2. Task priorities and deadlines
3. Realistic time estimates
4. Energy levels appropriate for the time of day
5. Balance between productivity and well-being

Format your response as a warm, encouraging plan that:
- Lists 3-5 prioritized tasks in order
- Explains why each task is important
- Suggests breaks if needed
- Adapts tone to the user's mood (supportive if low, celebratory if high)
- Keeps it concise but personal

Start with a brief greeting acknowledging their mood, then provide the plan."""

        # Save prompt to file for AI chat
        with open("data/client_question.txt", "w", encoding="utf-8") as f:
            f.write(planning_prompt)
        
        # Get AI response
        ai_response = response(additional_context="")
        
        if ai_response:
            plan_text = ai_response
        else:
            # Fallback to simple plan
            plan_text = self._generate_fallback_plan(tasks, mood_score, time_of_day)
        
        # Cache plan in Redis (1 hour TTL)
        if redis_client:
            redis_client.set(cache_key, plan_text, ttl=3600)
        
        return plan_text
    
    def _generate_fallback_plan(self, tasks: List[Task], mood_score: int, time_of_day: str) -> str:
        """Generate a simple fallback plan if AI fails"""
        # Sort tasks by priority and due date
        sorted_tasks = sorted(tasks, key=lambda t: (
            t.priority if t.priority else 5,
            t.due_date if t.due_date else "9999-12-31"
        ), reverse=True)
        
        plan_parts = []
        
        # Mood-based greeting
        if mood_score >= 7:
            plan_parts.append("You're feeling great today! Let's make the most of it.")
        elif mood_score >= 5:
            plan_parts.append("Here's your plan for today.")
        else:
            plan_parts.append("I'm here to help you through today. Let's take it one step at a time.")
        
        plan_parts.append(f"\nHere are your top priorities for the {time_of_day}:")
        
        for i, task in enumerate(sorted_tasks[:5], 1):
            plan_parts.append(f"{i}. {task.title}")
            if task.due_date:
                plan_parts.append(f"   (Due: {task.due_date})")
        
        if len(sorted_tasks) > 5:
            plan_parts.append(f"\nYou have {len(sorted_tasks) - 5} more tasks. Focus on these top ones first.")
        
        return "\n".join(plan_parts)
    
    def suggest_task_order(self, tasks: List[Task], mood_score: int = 5) -> List[Task]:
        """
        Suggest optimal task order based on mood, priority, and deadlines
        
        Args:
            tasks: List of tasks to prioritize
            mood_score: Current mood score (1-10)
            
        Returns:
            List of tasks in suggested order
        """
        if not tasks:
            return []
        
        # Calculate focus score for each task
        scored_tasks = []
        for task in tasks:
            focus_score = self._calculate_focus_score(task, mood_score)
            scored_tasks.append((focus_score, task))
        
        # Sort by focus score (highest first)
        scored_tasks.sort(key=lambda x: x[0], reverse=True)
        
        return [task for _, task in scored_tasks]
    
    def _calculate_focus_score(self, task: Task, mood_score: int) -> float:
        """
        Calculate focus score (0-100) for a task
        
        Factors:
        - Task priority (0-40 points)
        - Deadline urgency (0-30 points)
        - Mood compatibility (0-20 points)
        - Energy level (0-5 points) - estimated from mood and time of day
        - Time-of-day compatibility (0-5 points)
        """
        score = 0.0
        
        # Priority component (0-40)
        priority = task.priority if task.priority else 5
        score += (priority / 10) * 40
        
        # Deadline urgency (0-30)
        if task.due_date:
            try:
                due_date = datetime.fromisoformat(task.due_date).date()
                today = datetime.now().date()
                days_until = (due_date - today).days
                
                if days_until < 0:
                    # Overdue - high urgency
                    score += 30
                elif days_until == 0:
                    # Due today - high urgency
                    score += 25
                elif days_until <= 2:
                    # Due soon - medium-high urgency
                    score += 20
                elif days_until <= 7:
                    # Due this week - medium urgency
                    score += 10
                else:
                    # Not urgent - low urgency
                    score += 5
            except:
                pass
        
        # Mood compatibility (0-20)
        # High mood = can handle high priority tasks
        # Low mood = prefer easier/lower priority tasks
        if mood_score >= 7:
            # High mood - boost high priority tasks
            score += (priority / 10) * 20
        elif mood_score >= 5:
            # Medium mood - neutral
            score += 10
        else:
            # Low mood - prefer lower priority tasks (inverse)
            score += ((10 - priority) / 10) * 20
        
        # Energy level factor (0-5 points)
        # Estimate energy from mood and time of day
        current_hour = datetime.now().hour
        energy_level = self._estimate_energy_level(mood_score, current_hour)
        score += energy_level * 5
        
        # Time-of-day compatibility (0-5 points)
        # High priority tasks better in morning, low priority in afternoon/evening
        time_compatibility = self._calculate_time_compatibility(priority, current_hour)
        score += time_compatibility * 5
        
        return min(100, max(0, score))
    
    def _estimate_energy_level(self, mood_score: int, current_hour: int) -> float:
        """
        Estimate energy level (0-1) based on mood and time of day
        
        Returns:
            Energy level between 0.0 and 1.0
        """
        # Base energy from mood (0.3 to 1.0)
        mood_energy = 0.3 + (mood_score / 10) * 0.7
        
        # Time-of-day modifier
        # Morning (6-12): peak energy
        # Afternoon (12-17): moderate energy
        # Evening (17-22): lower energy
        # Night (22-6): very low energy
        
        if 6 <= current_hour < 12:
            time_modifier = 1.0  # Peak hours
        elif 12 <= current_hour < 17:
            time_modifier = 0.8  # Moderate
        elif 17 <= current_hour < 22:
            time_modifier = 0.6  # Lower
        else:
            time_modifier = 0.4  # Very low
        
        return mood_energy * time_modifier
    
    def _calculate_time_compatibility(self, priority: int, current_hour: int) -> float:
        """
        Calculate how well a task's priority matches the current time of day
        
        High priority tasks (7-10) work best in morning
        Medium priority tasks (4-6) work well in afternoon
        Low priority tasks (1-3) work well in evening
        
        Returns:
            Compatibility score between 0.0 and 1.0
        """
        if 6 <= current_hour < 12:
            # Morning - best for high priority
            if priority >= 7:
                return 1.0
            elif priority >= 4:
                return 0.7
            else:
                return 0.4
        elif 12 <= current_hour < 17:
            # Afternoon - good for medium-high priority
            if priority >= 7:
                return 0.8
            elif priority >= 4:
                return 1.0
            else:
                return 0.6
        elif 17 <= current_hour < 22:
            # Evening - better for lower priority
            if priority >= 7:
                return 0.5
            elif priority >= 4:
                return 0.7
            else:
                return 1.0
        else:
            # Night - low compatibility for all
            return 0.3
    
    def get_plan_summary(self) -> str:
        """Get a quick summary of today's plan"""
        tasks = Task.get_all(status="pending")
        mood = MoodEntry.get_today()
        
        if not tasks:
            return "You're all caught up! No pending tasks."
        
        summary_parts = [f"You have {len(tasks)} pending task(s)"]
        
        if mood:
            summary_parts.append(f"and you're feeling {mood.mood_score}/10 today.")
        else:
            summary_parts.append("How are you feeling today?")
        
        # Get top 3 tasks
        sorted_tasks = self.suggest_task_order(tasks, mood.mood_score if mood else 5)
        if sorted_tasks:
            summary_parts.append("\nTop priorities:")
            for i, task in enumerate(sorted_tasks[:3], 1):
                summary_parts.append(f"{i}. {task.title}")
        
        return " ".join(summary_parts)


# Global planner instance
_planner = AIPlanner()


def get_planner() -> AIPlanner:
    """Get the global AI planner instance"""
    return _planner

