"""
Productivity Tracker - Calculates and tracks daily productivity scores
Correlates mood with task completion to provide insights
Includes Redis caching for improved performance
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from database import Task, MoodEntry, ProductivityEntry
from database import get_database


class ProductivityTracker:
    """Tracks productivity metrics and correlates mood with task completion"""
    
    def calculate_daily_productivity(self, date: Optional[str] = None, invalidate_cache: bool = True) -> ProductivityEntry:
        """
        Calculate productivity score for a given date
        
        Formula:
        - Base score: (tasks_completed / tasks_total) * 50
        - Mood multiplier: (avg_mood_score / 10) * 30
        - Focus bonus: (focus_hours / 8) * 20
        - Total: 0-100
        
        Args:
            date: Date string (YYYY-MM-DD), defaults to today
            
        Returns:
            ProductivityEntry with calculated score
        """
        if date is None:
            date = datetime.now().date().isoformat()
        
        # Get tasks for the date
        all_tasks = Task.get_all()
        date_obj = datetime.fromisoformat(date).date()
        
        # Filter tasks that were completed on this date
        completed_tasks = []
        total_tasks = []
        
        for task in all_tasks:
            # Check if task was created before or on this date
            task_date = datetime.fromisoformat(task.created_at).date()
            if task_date <= date_obj:
                total_tasks.append(task)
                if task.status == "completed":
                    # Check if completed on this date
                    updated_date = datetime.fromisoformat(task.updated_at).date()
                    if updated_date == date_obj:
                        completed_tasks.append(task)
        
        # If no tasks exist, still count tasks created on this date
        if not total_tasks:
            for task in all_tasks:
                task_date = datetime.fromisoformat(task.created_at).date()
                if task_date == date_obj:
                    total_tasks.append(task)
        
        tasks_completed = len(completed_tasks)
        tasks_total = max(len(total_tasks), 1)  # Avoid division by zero
        
        # Get mood entries for the date
        mood_entries = MoodEntry.get_recent(limit=100)
        date_mood_entries = [
            m for m in mood_entries
            if datetime.fromisoformat(m.created_at).date().isoformat() == date
        ]
        
        avg_mood_score = None
        if date_mood_entries:
            avg_mood_score = sum(m.mood_score for m in date_mood_entries) / len(date_mood_entries)
        
        # Calculate productivity score
        # Base score: task completion rate (0-50 points)
        completion_rate = tasks_completed / tasks_total if tasks_total > 0 else 0
        base_score = completion_rate * 50
        
        # Mood multiplier (0-30 points)
        mood_score = 0
        if avg_mood_score:
            mood_score = (avg_mood_score / 10) * 30
        
        # Focus hours bonus (0-20 points)
        # For now, estimate based on completed tasks (assume 1 hour per task)
        focus_hours = min(tasks_completed * 1.0, 8.0)  # Cap at 8 hours
        focus_bonus = (focus_hours / 8) * 20
        
        productivity_score = base_score + mood_score + focus_bonus
        productivity_score = min(100, max(0, productivity_score))
        
        # Create or update productivity entry
        entry = ProductivityEntry.create(
            date=date,
            productivity_score=productivity_score,
            tasks_completed=tasks_completed,
            tasks_total=tasks_total,
            avg_mood_score=avg_mood_score,
            focus_hours=focus_hours,
            notes=f"Auto-calculated: {tasks_completed}/{tasks_total} tasks completed"
        )
        
        # Invalidate productivity trend cache when productivity is updated
        if invalidate_cache:
            db = get_database()
            redis_client = db.get_redis()
            if redis_client:
                # Invalidate all trend caches
                for days in [7, 14, 30]:
                    redis_client.delete(f"productivity:trend:{days}")
                # Also invalidate productivity correlation cache
                redis_client.delete("productivity:correlation:30")
        
        return entry
    
    def get_productivity_trend(self, days: int = 7) -> List[Dict]:
        """
        Get productivity trend over the last N days (with Redis caching)
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of dictionaries with date, productivity_score, and avg_mood_score
        """
        db = get_database()
        redis_client = db.get_redis()
        
        # Check Redis cache first (15 minutes TTL)
        cache_key = f"productivity:trend:{days}"
        if redis_client:
            cached_trend = redis_client.get(cache_key)
            if cached_trend:
                return cached_trend
        
        # Calculate trend
        trend = []
        today = datetime.now().date()
        
        for i in range(days):
            date = (today - timedelta(days=i)).isoformat()
            entry = ProductivityEntry.get_by_date(date)
            
            if entry:
                trend.append({
                    "date": entry.date,
                    "productivity_score": entry.productivity_score,
                    "avg_mood_score": entry.avg_mood_score,
                    "tasks_completed": entry.tasks_completed,
                    "tasks_total": entry.tasks_total
                })
            else:
                # Calculate if doesn't exist
                entry = self.calculate_daily_productivity(date)
                trend.append({
                    "date": entry.date,
                    "productivity_score": entry.productivity_score,
                    "avg_mood_score": entry.avg_mood_score,
                    "tasks_completed": entry.tasks_completed,
                    "tasks_total": entry.tasks_total
                })
        
        # Cache in Redis (15 minutes TTL)
        if redis_client:
            redis_client.set(cache_key, trend, ttl=900)
        
        return trend
    
    def get_mood_productivity_correlation(self, days: int = 30) -> Dict:
        """
        Analyze correlation between mood and productivity
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with correlation metrics
        """
        trend = self.get_productivity_trend(days)
        
        if not trend:
            return {
                "correlation": 0.0,
                "avg_productivity_high_mood": 0.0,
                "avg_productivity_low_mood": 0.0,
                "insights": "Not enough data"
            }
        
        # Separate high mood vs low mood days
        high_mood_days = [d for d in trend if d["avg_mood_score"] and d["avg_mood_score"] >= 7]
        low_mood_days = [d for d in trend if d["avg_mood_score"] and d["avg_mood_score"] < 5]
        medium_mood_days = [
            d for d in trend
            if d["avg_mood_score"] and 5 <= d["avg_mood_score"] < 7
        ]
        
        # Calculate averages
        avg_high = (
            sum(d["productivity_score"] for d in high_mood_days) / len(high_mood_days)
            if high_mood_days else 0
        )
        avg_low = (
            sum(d["productivity_score"] for d in low_mood_days) / len(low_mood_days)
            if low_mood_days else 0
        )
        avg_medium = (
            sum(d["productivity_score"] for d in medium_mood_days) / len(medium_mood_days)
            if medium_mood_days else 0
        )
        
        # Simple correlation coefficient
        mood_scores = [d["avg_mood_score"] for d in trend if d["avg_mood_score"]]
        prod_scores = [d["productivity_score"] for d in trend if d["avg_mood_score"]]
        
        correlation = 0.0
        if len(mood_scores) > 1:
            # Calculate Pearson correlation coefficient
            n = len(mood_scores)
            mean_mood = sum(mood_scores) / n
            mean_prod = sum(prod_scores) / n
            
            numerator = sum((mood_scores[i] - mean_mood) * (prod_scores[i] - mean_prod) for i in range(n))
            mood_var = sum((m - mean_mood) ** 2 for m in mood_scores)
            prod_var = sum((p - mean_prod) ** 2 for p in prod_scores)
            
            if mood_var > 0 and prod_var > 0:
                correlation = numerator / ((mood_var * prod_var) ** 0.5)
        
        # Generate insights
        insights = []
        if avg_high > avg_low + 10:
            insights.append("You're significantly more productive on high mood days")
        elif avg_low > avg_high + 10:
            insights.append("You're more productive on low mood days (interesting pattern!)")
        else:
            insights.append("Mood doesn't strongly affect your productivity")
        
        if correlation > 0.5:
            insights.append("Strong positive correlation between mood and productivity")
        elif correlation < -0.5:
            insights.append("Negative correlation - mood and productivity are inversely related")
        else:
            insights.append("Weak correlation between mood and productivity")
        
        return {
            "correlation": round(correlation, 2),
            "avg_productivity_high_mood": round(avg_high, 1),
            "avg_productivity_low_mood": round(avg_low, 1),
            "avg_productivity_medium_mood": round(avg_medium, 1),
            "high_mood_days": len(high_mood_days),
            "low_mood_days": len(low_mood_days),
            "insights": "; ".join(insights)
        }
    
    def update_today(self):
        """Update today's productivity score"""
        return self.calculate_daily_productivity()


# Global tracker instance
_tracker = ProductivityTracker()


def get_productivity_tracker() -> ProductivityTracker:
    """Get the global productivity tracker instance"""
    return _tracker

