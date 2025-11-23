"""
Analytics Engine - Aggregates and analyzes productivity data
Provides daily, weekly, and monthly insights
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from database import Task, TaskCompletion, FocusSession, ProductivityEntry, MoodEntry
from .focus_tracker import get_focus_tracker
from .productivity_tracker import get_productivity_tracker
from database import get_database


class AnalyticsEngine:
    """Analytics engine for aggregating and analyzing productivity data"""
    
    def get_daily_aggregate(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get daily aggregate statistics
        
        Args:
            date: Date string (YYYY-MM-DD), defaults to today
            
        Returns:
            Dictionary with daily statistics
        """
        if date is None:
            date = datetime.now().date().isoformat()
        
        # Get tasks
        all_tasks = Task.get_all()
        date_obj = datetime.fromisoformat(date).date()
        
        # Filter tasks for this date
        tasks_planned = []
        tasks_completed = []
        for task in all_tasks:
            task_date = datetime.fromisoformat(task.created_at).date()
            if task_date <= date_obj:
                tasks_planned.append(task)
                if task.status == "completed":
                    updated_date = datetime.fromisoformat(task.updated_at).date()
                    if updated_date == date_obj:
                        tasks_completed.append(task)
        
        # Get completions for this date
        completions = TaskCompletion.get_by_date(date)
        
        # Get focus sessions for this date
        focus_tracker = get_focus_tracker()
        focus_hours = focus_tracker.get_daily_focus_hours(date)
        
        # Get productivity entry
        productivity_entry = ProductivityEntry.get_by_date(date)
        
        # Get mood entry
        mood_entry = MoodEntry.get_today() if date == datetime.now().date().isoformat() else None
        if not mood_entry:
            # Try to get mood for the specific date
            mood_entries = MoodEntry.get_by_date_range(date, date)
            mood_entry = mood_entries[0] if mood_entries else None
        
        # Calculate average focus score
        avg_focus_score = None
        if completions:
            focus_scores = [c.focus_score for c in completions if c.focus_score is not None]
            if focus_scores:
                avg_focus_score = sum(focus_scores) / len(focus_scores)
        
        # Calculate average task duration
        avg_duration = None
        if completions:
            durations = [c.duration_minutes for c in completions if c.duration_minutes is not None]
            if durations:
                avg_duration = sum(durations) / len(durations)
        
        return {
            "date": date,
            "tasks_planned": len(tasks_planned),
            "tasks_completed": len(tasks_completed),
            "completion_rate": len(tasks_completed) / len(tasks_planned) if tasks_planned else 0.0,
            "focus_hours": focus_hours,
            "focus_sessions": len(FocusSession.get_by_date(date)),
            "avg_focus_score": avg_focus_score,
            "avg_task_duration_minutes": avg_duration,
            "productivity_score": productivity_entry.productivity_score if productivity_entry else None,
            "mood_score": mood_entry.mood_score if mood_entry else None,
            "completions": [c.to_dict() for c in completions]
        }
    
    def get_weekly_aggregate(self, start_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get weekly aggregate statistics
        
        Args:
            start_date: Start date (YYYY-MM-DD), defaults to Monday of current week
            
        Returns:
            Dictionary with weekly statistics
        """
        if start_date is None:
            today = datetime.now().date()
            days_since_monday = today.weekday()
            start_date_obj = today - timedelta(days=days_since_monday)
        else:
            start_date_obj = datetime.fromisoformat(start_date).date()
        
        # Get daily aggregates for the week
        daily_aggregates = []
        total_tasks_planned = 0
        total_tasks_completed = 0
        total_focus_hours = 0.0
        focus_scores = []
        durations = []
        productivity_scores = []
        mood_scores = []
        
        for i in range(7):
            date_obj = start_date_obj + timedelta(days=i)
            date_str = date_obj.isoformat()
            daily = self.get_daily_aggregate(date_str)
            daily_aggregates.append(daily)
            
            total_tasks_planned += daily["tasks_planned"]
            total_tasks_completed += daily["tasks_completed"]
            total_focus_hours += daily["focus_hours"]
            
            if daily["avg_focus_score"] is not None:
                focus_scores.append(daily["avg_focus_score"])
            if daily["avg_task_duration_minutes"] is not None:
                durations.append(daily["avg_task_duration_minutes"])
            if daily["productivity_score"] is not None:
                productivity_scores.append(daily["productivity_score"])
            if daily["mood_score"] is not None:
                mood_scores.append(daily["mood_score"])
        
        return {
            "start_date": start_date_obj.isoformat(),
            "end_date": (start_date_obj + timedelta(days=6)).isoformat(),
            "total_tasks_planned": total_tasks_planned,
            "total_tasks_completed": total_tasks_completed,
            "avg_completion_rate": total_tasks_completed / total_tasks_planned if total_tasks_planned > 0 else 0.0,
            "total_focus_hours": total_focus_hours,
            "avg_daily_focus_hours": total_focus_hours / 7.0,
            "avg_focus_score": sum(focus_scores) / len(focus_scores) if focus_scores else None,
            "avg_task_duration_minutes": sum(durations) / len(durations) if durations else None,
            "avg_productivity_score": sum(productivity_scores) / len(productivity_scores) if productivity_scores else None,
            "avg_mood_score": sum(mood_scores) / len(mood_scores) if mood_scores else None,
            "daily_aggregates": daily_aggregates
        }
    
    def get_monthly_aggregate(self, year: Optional[int] = None, month: Optional[int] = None) -> Dict[str, Any]:
        """
        Get monthly aggregate statistics
        
        Args:
            year: Year (defaults to current year)
            month: Month (1-12, defaults to current month)
            
        Returns:
            Dictionary with monthly statistics
        """
        if year is None or month is None:
            now = datetime.now()
            year = year or now.year
            month = month or now.month
        
        start_date = datetime(year, month, 1).date()
        # Get last day of month
        if month == 12:
            end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
        
        # Get all tasks created in this month
        all_tasks = Task.get_all()
        tasks_planned = []
        tasks_completed = []
        
        for task in all_tasks:
            task_date = datetime.fromisoformat(task.created_at).date()
            if start_date <= task_date <= end_date:
                tasks_planned.append(task)
                if task.status == "completed":
                    updated_date = datetime.fromisoformat(task.updated_at).date()
                    if start_date <= updated_date <= end_date:
                        tasks_completed.append(task)
        
        # Get productivity entries for this month
        productivity_entries = ProductivityEntry.get_recent(limit=100)
        month_entries = [
            e for e in productivity_entries
            if start_date <= datetime.fromisoformat(e.date).date() <= end_date
        ]
        
        # Calculate averages
        avg_productivity = None
        if month_entries:
            avg_productivity = sum(e.productivity_score for e in month_entries) / len(month_entries)
        
        # Get focus hours for each day in the month
        total_focus_hours = 0.0
        focus_tracker = get_focus_tracker()
        current_date = start_date
        while current_date <= end_date:
            total_focus_hours += focus_tracker.get_daily_focus_hours(current_date.isoformat())
            current_date += timedelta(days=1)
        
        return {
            "year": year,
            "month": month,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "tasks_planned": len(tasks_planned),
            "tasks_completed": len(tasks_completed),
            "completion_rate": len(tasks_completed) / len(tasks_planned) if tasks_planned else 0.0,
            "total_focus_hours": total_focus_hours,
            "avg_daily_focus_hours": total_focus_hours / (end_date - start_date).days if start_date != end_date else 0.0,
            "avg_productivity_score": avg_productivity,
            "days_tracked": len(month_entries)
        }
    
    def get_trends(self, days: int = 30) -> Dict[str, Any]:
        """
        Get productivity trends over a period
        
        Args:
            days: Number of days to analyze (defaults to 30)
            
        Returns:
            Dictionary with trend data
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days - 1)
        
        daily_data = []
        current_date = start_date
        
        while current_date <= end_date:
            daily = self.get_daily_aggregate(current_date.isoformat())
            daily_data.append(daily)
            current_date += timedelta(days=1)
        
        # Calculate trends
        productivity_trend = []
        mood_trend = []
        completion_rate_trend = []
        focus_hours_trend = []
        
        for daily in daily_data:
            if daily["productivity_score"] is not None:
                productivity_trend.append(daily["productivity_score"])
            if daily["mood_score"] is not None:
                mood_trend.append(daily["mood_score"])
            completion_rate_trend.append(daily["completion_rate"])
            focus_hours_trend.append(daily["focus_hours"])
        
        # Calculate correlation between mood and productivity
        mood_productivity_correlation = None
        if len(productivity_trend) == len(mood_trend) and len(productivity_trend) > 1:
            # Simple correlation coefficient
            n = len(productivity_trend)
            mean_mood = sum(mood_trend) / n
            mean_prod = sum(productivity_trend) / n
            
            numerator = sum((mood_trend[i] - mean_mood) * (productivity_trend[i] - mean_prod) for i in range(n))
            mood_var = sum((m - mean_mood) ** 2 for m in mood_trend)
            prod_var = sum((p - mean_prod) ** 2 for p in productivity_trend)
            
            if mood_var > 0 and prod_var > 0:
                mood_productivity_correlation = numerator / ((mood_var * prod_var) ** 0.5)
        
        return {
            "period_days": days,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "daily_data": daily_data,
            "avg_productivity": sum(productivity_trend) / len(productivity_trend) if productivity_trend else None,
            "avg_mood": sum(mood_trend) / len(mood_trend) if mood_trend else None,
            "avg_completion_rate": sum(completion_rate_trend) / len(completion_rate_trend) if completion_rate_trend else 0.0,
            "avg_focus_hours": sum(focus_hours_trend) / len(focus_hours_trend) if focus_hours_trend else 0.0,
            "mood_productivity_correlation": mood_productivity_correlation
        }


# Global analytics engine instance
_analytics_engine: Optional[AnalyticsEngine] = None


def get_analytics_engine() -> AnalyticsEngine:
    """Get or create global analytics engine instance"""
    global _analytics_engine
    if _analytics_engine is None:
        _analytics_engine = AnalyticsEngine()
    return _analytics_engine

