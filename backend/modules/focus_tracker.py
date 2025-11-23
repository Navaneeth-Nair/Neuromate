"""
Focus Tracker - Tracks focus sessions and calculates focus hours
Integrates with productivity tracking
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from database import FocusSession, Task
from database import get_database


class FocusTracker:
    """Tracks focus sessions and calculates daily focus hours"""
    
    def start_session(self, task_id: Optional[int] = None, notes: Optional[str] = None) -> FocusSession:
        """
        Start a new focus session
        
        Args:
            task_id: Optional task ID to associate with this session
            notes: Optional notes about the session
            
        Returns:
            FocusSession object
        """
        # Check if there's an active session
        active_session = FocusSession.get_active()
        if active_session:
            raise ValueError(f"Active focus session already exists (started at {active_session.started_at})")
        
        return FocusSession.start(task_id=task_id, notes=notes)
    
    def end_session(self, notes: Optional[str] = None) -> Optional[FocusSession]:
        """
        End the current focus session
        
        Args:
            notes: Optional notes about the session
            
        Returns:
            Ended FocusSession object, or None if no active session
        """
        active_session = FocusSession.get_active()
        if not active_session:
            return None
        
        active_session.end(notes=notes)
        return active_session
    
    def get_daily_focus_hours(self, date: Optional[str] = None) -> float:
        """
        Calculate total focus hours for a given date
        
        Args:
            date: Date string (YYYY-MM-DD), defaults to today
            
        Returns:
            Total focus hours (float)
        """
        if date is None:
            date = datetime.now().date().isoformat()
        
        sessions = FocusSession.get_by_date(date)
        total_minutes = sum(
            float(session.duration_minutes) if session.duration_minutes else 0.0
            for session in sessions
            if session.ended_at and session.duration_minutes
        )
        
        return float(total_minutes) / 60.0  # Convert minutes to hours
    
    def get_weekly_focus_hours(self, start_date: Optional[str] = None) -> Dict[str, float]:
        """
        Get focus hours for each day in a week
        
        Args:
            start_date: Start date (YYYY-MM-DD), defaults to Monday of current week
            
        Returns:
            Dictionary mapping date strings to focus hours
        """
        if start_date is None:
            today = datetime.now().date()
            # Get Monday of current week
            days_since_monday = today.weekday()
            start_date_obj = today - timedelta(days=days_since_monday)
        else:
            start_date_obj = datetime.fromisoformat(start_date).date()
        
        focus_hours_by_date = {}
        for i in range(7):
            date_obj = start_date_obj + timedelta(days=i)
            date_str = date_obj.isoformat()
            focus_hours_by_date[date_str] = self.get_daily_focus_hours(date_str)
        
        return focus_hours_by_date
    
    def get_active_session(self) -> Optional[FocusSession]:
        """Get the currently active focus session"""
        return FocusSession.get_active()
    
    def get_recent_sessions(self, limit: int = 10) -> List[FocusSession]:
        """Get recent focus sessions"""
        return FocusSession.get_recent(limit=limit)
    
    def get_sessions_by_task(self, task_id: int) -> List[FocusSession]:
        """Get all focus sessions for a specific task"""
        db = get_database()
        results = db.execute(
            "SELECT * FROM focus_sessions WHERE task_id = ? ORDER BY started_at DESC",
            (task_id,)
        )
        return [FocusSession(**row) for row in results]


# Global focus tracker instance
_focus_tracker: Optional[FocusTracker] = None


def get_focus_tracker() -> FocusTracker:
    """Get or create global focus tracker instance"""
    global _focus_tracker
    if _focus_tracker is None:
        _focus_tracker = FocusTracker()
    return _focus_tracker

