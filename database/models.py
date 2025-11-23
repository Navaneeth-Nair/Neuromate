"""
Data Models - Task, Mood, Journal, Habit models with CRUD operations
Includes Redis caching support for improved performance
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from .database import get_database

# Ensure database is initialized
from . import db_init


class Task:
    """Task model with CRUD operations"""
    
    def __init__(self, id: Optional[int] = None, title: str = "", description: str = "",
                 due_date: Optional[str] = None, priority: int = 5, status: str = "pending",
                 created_at: Optional[str] = None, updated_at: Optional[str] = None):
        self.id = id
        self.title = title
        self.description = description
        self.due_date = due_date
        self.priority = priority  # 1-10 scale
        self.status = status  # pending, in_progress, completed, cancelled
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()
    
    @classmethod
    def create(cls, title: str, description: str = "", due_date: Optional[str] = None,
               priority: int = 5) -> 'Task':
        """Create a new task in the database"""
        db = get_database()
        now = datetime.now().isoformat()
        
        task_id = db.execute_write(
            """INSERT INTO tasks (title, description, due_date, priority, status, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (title, description, due_date, priority, "pending", now, now)
        )
        
        return cls(id=task_id, title=title, description=description, due_date=due_date,
                  priority=priority, status="pending", created_at=now, updated_at=now)
    
    @classmethod
    def get_by_id(cls, task_id: int) -> Optional['Task']:
        """Get a task by ID (with Redis caching)"""
        db = get_database()
        redis_client = db.get_redis()
        
        # Check Redis cache first
        if redis_client:
            cached_task = redis_client.get_cached_task(task_id)
            if cached_task:
                return cls(**cached_task)
        
        # Query database
        results = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        
        if not results:
            return None
        
        row = results[0]
        task = cls(**row)
        
        # Cache in Redis
        if redis_client:
            redis_client.cache_task(task_id, task.to_dict())
        
        return task
    
    @classmethod
    def get_all(cls, status: Optional[str] = None) -> List['Task']:
        """Get all tasks, optionally filtered by status (with Redis caching)"""
        db = get_database()
        redis_client = db.get_redis()
        
        # Check Redis cache for all tasks (only if no status filter)
        if not status and redis_client:
            cached_tasks = redis_client.get_cached_tasks()
            if cached_tasks:
                return [cls(**task) for task in cached_tasks]
        
        # Query database
        if status:
            results = db.execute("SELECT * FROM tasks WHERE status = ? ORDER BY created_at DESC", (status,))
        else:
            results = db.execute("SELECT * FROM tasks ORDER BY created_at DESC")
        
        tasks = [cls(**row) for row in results]
        
        # Cache in Redis (only if no status filter)
        if not status and redis_client:
            redis_client.cache_tasks([task.to_dict() for task in tasks])
        
        return tasks
    
    def update(self):
        """Update task in database"""
        if not self.id:
            raise ValueError("Cannot update task without ID")
        
        db = get_database()
        self.updated_at = datetime.now().isoformat()
        
        db.execute_write(
            """UPDATE tasks SET title = ?, description = ?, due_date = ?, priority = ?, 
               status = ?, updated_at = ? WHERE id = ?""",
            (self.title, self.description, self.due_date, self.priority, self.status,
             self.updated_at, self.id)
        )
    
    def delete(self):
        """Delete task from database"""
        if not self.id:
            raise ValueError("Cannot delete task without ID")
        
        db = get_database()
        db.execute_write("DELETE FROM tasks WHERE id = ?", (self.id,))
    
    def complete(self, duration_minutes: Optional[float] = None,
                 focus_score: Optional[int] = None, notes: Optional[str] = None):
        """Mark task as completed and log completion details"""
        self.status = "completed"
        self.update()
        
        # Log completion details (TaskCompletion is defined later in this file)
        # We'll import it lazily to avoid circular import
        if self.id:
            # Import here to avoid circular dependency
            import sys
            current_module = sys.modules[__name__]
            TaskCompletion = getattr(current_module, 'TaskCompletion', None)
            if TaskCompletion:
                TaskCompletion.create(
                    task_id=self.id,
                    duration_minutes=duration_minutes,
                    focus_score=focus_score,
                    notes=notes
                )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class MoodEntry:
    """Mood entry model"""
    
    def __init__(self, id: Optional[int] = None, mood_score: int = 5, mood_text: str = "",
                 notes: str = "", created_at: Optional[str] = None):
        self.id = id
        self.mood_score = mood_score  # 1-10 scale
        self.mood_text = mood_text
        self.notes = notes
        self.created_at = created_at or datetime.now().isoformat()
    
    @classmethod
    def create(cls, mood_score: int, mood_text: str = "", notes: str = "") -> 'MoodEntry':
        """Create a new mood entry"""
        db = get_database()
        now = datetime.now().isoformat()
        
        # Validate mood score
        mood_score = max(1, min(10, mood_score))
        
        entry_id = db.execute_write(
            """INSERT INTO mood_entries (mood_score, mood_text, notes, created_at)
               VALUES (?, ?, ?, ?)""",
            (mood_score, mood_text, notes, now)
        )
        
        return cls(id=entry_id, mood_score=mood_score, mood_text=mood_text,
                   notes=notes, created_at=now)
    
    @classmethod
    def get_recent(cls, limit: int = 10) -> List['MoodEntry']:
        """Get recent mood entries"""
        db = get_database()
        results = db.execute(
            "SELECT * FROM mood_entries ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        return [cls(**row) for row in results]
    
    @classmethod
    def get_today(cls) -> Optional['MoodEntry']:
        """Get today's mood entry (with Redis caching)"""
        db = get_database()
        redis_client = db.get_redis()
        
        # Check Redis cache first
        if redis_client:
            cached_mood = redis_client.get_cached_today_mood()
            if cached_mood:
                return cls(**cached_mood)
        
        # Query database
        today = datetime.now().date().isoformat()
        # MySQL uses DATE() function differently, use LIKE for compatibility
        results = db.execute(
            "SELECT * FROM mood_entries WHERE created_at LIKE ? ORDER BY created_at DESC LIMIT 1",
            (f"{today}%",)
        )
        
        mood = cls(**results[0]) if results else None
        
        # Cache in Redis
        if mood and redis_client:
            redis_client.cache_today_mood(mood.to_dict())
        
        return mood
    
    @classmethod
    def get_by_date_range(cls, start_date: str, end_date: str) -> List['MoodEntry']:
        """Get mood entries within a date range"""
        db = get_database()
        # Use string comparison for compatibility with both SQLite and MySQL
        # Dates are stored as ISO format strings (YYYY-MM-DDTHH:MM:SS)
        results = db.execute(
            """SELECT * FROM mood_entries 
               WHERE created_at >= ? AND created_at <= ?
               ORDER BY created_at DESC""",
            (start_date, f"{end_date} 23:59:59")
        )
        return [cls(**row) for row in results]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert mood entry to dictionary"""
        return {
            "id": self.id,
            "mood_score": self.mood_score,
            "mood_text": self.mood_text,
            "notes": self.notes,
            "created_at": self.created_at
        }


class JournalEntry:
    """Journal entry model"""
    
    def __init__(self, id: Optional[int] = None, content: str = "", entry_type: str = "general",
                 created_at: Optional[str] = None):
        self.id = id
        self.content = content
        self.entry_type = entry_type  # general, reflection, voice_command, ai_conversation
        self.created_at = created_at or datetime.now().isoformat()
    
    @classmethod
    def create(cls, content: str, entry_type: str = "general") -> 'JournalEntry':
        """Create a new journal entry"""
        db = get_database()
        now = datetime.now().isoformat()
        
        entry_id = db.execute_write(
            """INSERT INTO journal_entries (content, entry_type, created_at)
               VALUES (?, ?, ?)""",
            (content, entry_type, now)
        )
        
        return cls(id=entry_id, content=content, entry_type=entry_type, created_at=now)
    
    @classmethod
    def get_recent(cls, limit: int = 20, entry_type: Optional[str] = None) -> List['JournalEntry']:
        """Get recent journal entries"""
        db = get_database()
        
        if entry_type:
            results = db.execute(
                "SELECT * FROM journal_entries WHERE entry_type = ? ORDER BY created_at DESC LIMIT ?",
                (entry_type, limit)
            )
        else:
            results = db.execute(
                "SELECT * FROM journal_entries ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
        
        return [cls(**row) for row in results]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert journal entry to dictionary"""
        return {
            "id": self.id,
            "content": self.content,
            "entry_type": self.entry_type,
            "created_at": self.created_at
        }


class Habit:
    """Habit model with CRUD operations and streak tracking"""
    
    def __init__(self, id: Optional[int] = None, name: str = "", description: str = "",
                 frequency: str = "daily", streak_count: int = 0,
                 created_at: Optional[str] = None, updated_at: Optional[str] = None):
        self.id = id
        self.name = name
        self.description = description
        self.frequency = frequency  # daily, weekly, etc.
        self.streak_count = streak_count
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()
    
    @classmethod
    def create(cls, name: str, description: str = "", frequency: str = "daily") -> 'Habit':
        """Create a new habit"""
        db = get_database()
        now = datetime.now().isoformat()
        
        habit_id = db.execute_write(
            """INSERT INTO habits (name, description, frequency, streak_count, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (name, description, frequency, 0, now, now)
        )
        
        return cls(id=habit_id, name=name, description=description, frequency=frequency,
                   streak_count=0, created_at=now, updated_at=now)
    
    @classmethod
    def get_by_id(cls, habit_id: int) -> Optional['Habit']:
        """Get a habit by ID (with Redis caching)"""
        db = get_database()
        redis_client = db.get_redis()
        
        # Check Redis cache first (1 hour TTL for habit streaks)
        cache_key = f"habit:{habit_id}:streak"
        if redis_client:
            cached_habit = redis_client.get(cache_key)
            if cached_habit:
                return cls(**cached_habit)
        
        # Query database
        results = db.execute("SELECT * FROM habits WHERE id = ?", (habit_id,))
        
        if not results:
            return None
        
        row = results[0]
        habit = cls(**row)
        
        # Cache in Redis (1 hour TTL)
        if redis_client:
            redis_client.set(cache_key, habit.to_dict(), ttl=3600)
        
        return habit
    
    @classmethod
    def get_all(cls) -> List['Habit']:
        """Get all habits"""
        db = get_database()
        results = db.execute("SELECT * FROM habits ORDER BY created_at DESC")
        return [cls(**row) for row in results]
    
    def update(self):
        """Update habit in database (invalidates Redis cache)"""
        if not self.id:
            raise ValueError("Cannot update habit without ID")
        
        db = get_database()
        redis_client = db.get_redis()
        
        self.updated_at = datetime.now().isoformat()
        
        db.execute_write(
            """UPDATE habits SET name = ?, description = ?, frequency = ?, 
               streak_count = ?, updated_at = ? WHERE id = ?""",
            (self.name, self.description, self.frequency, self.streak_count,
             self.updated_at, self.id)
        )
        
        # Invalidate Redis cache
        if redis_client:
            redis_client.delete(f"habit:{self.id}:streak")
    
    def increment_streak(self):
        """Increment habit streak count"""
        self.streak_count += 1
        self.update()
    
    def reset_streak(self):
        """Reset habit streak count to 0"""
        self.streak_count = 0
        self.update()
    
    def get_streak(self) -> int:
        """Get current streak count (with Redis caching)"""
        db = get_database()
        redis_client = db.get_redis()
        
        if not self.id:
            return 0
        
        # Check Redis cache first
        cache_key = f"habit:{self.id}:streak"
        if redis_client:
            cached_streak = redis_client.get(cache_key)
            if cached_streak is not None:
                return cached_streak
        
        # Get from database
        habit = Habit.get_by_id(self.id)
        streak = habit.streak_count if habit else 0
        
        # Cache in Redis (1 hour TTL)
        if redis_client:
            redis_client.set(cache_key, streak, ttl=3600)
        
        return streak
    
    def delete(self):
        """Delete habit from database"""
        if not self.id:
            raise ValueError("Cannot delete habit without ID")
        
        db = get_database()
        redis_client = db.get_redis()
        
        db.execute_write("DELETE FROM habits WHERE id = ?", (self.id,))
        
        # Invalidate Redis cache
        if redis_client:
            redis_client.delete(f"habit:{self.id}:streak")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert habit to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "frequency": self.frequency,
            "streak_count": self.streak_count,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class ProductivityEntry:
    """Productivity entry model - tracks daily productivity metrics"""
    
    def __init__(self, id: Optional[int] = None, date: str = "", productivity_score: float = 0.0,
                 tasks_completed: int = 0, tasks_total: int = 0, avg_mood_score: Optional[float] = None,
                 focus_hours: float = 0.0, notes: str = "", created_at: Optional[str] = None,
                 updated_at: Optional[str] = None):
        self.id = id
        self.date = date
        self.productivity_score = productivity_score  # 0-100 scale
        self.tasks_completed = tasks_completed
        self.tasks_total = tasks_total
        self.avg_mood_score = avg_mood_score
        self.focus_hours = focus_hours
        self.notes = notes
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()
    
    @classmethod
    def create(cls, date: str, productivity_score: float, tasks_completed: int = 0,
               tasks_total: int = 0, avg_mood_score: Optional[float] = None,
               focus_hours: float = 0.0, notes: str = "") -> 'ProductivityEntry':
        """Create or update a productivity entry for a date"""
        db = get_database()
        now = datetime.now().isoformat()
        
        # Check if entry exists for this date
        existing = cls.get_by_date(date)
        
        if existing:
            # Update existing entry
            existing.productivity_score = productivity_score
            existing.tasks_completed = tasks_completed
            existing.tasks_total = tasks_total
            existing.avg_mood_score = avg_mood_score
            existing.focus_hours = focus_hours
            existing.notes = notes
            existing.updated_at = now
            existing.update()
            return existing
        
        # Create new entry
        entry_id = db.execute_write(
            """INSERT INTO productivity_entries 
               (date, productivity_score, tasks_completed, tasks_total, avg_mood_score, 
                focus_hours, notes, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (date, productivity_score, tasks_completed, tasks_total, avg_mood_score,
             focus_hours, notes, now, now)
        )
        
        return cls(id=entry_id, date=date, productivity_score=productivity_score,
                   tasks_completed=tasks_completed, tasks_total=tasks_total,
                   avg_mood_score=avg_mood_score, focus_hours=focus_hours,
                   notes=notes, created_at=now, updated_at=now)
    
    @classmethod
    def get_by_date(cls, date: str) -> Optional['ProductivityEntry']:
        """Get productivity entry for a specific date"""
        db = get_database()
        results = db.execute(
            "SELECT * FROM productivity_entries WHERE date = ? LIMIT 1",
            (date,)
        )
        return cls(**results[0]) if results else None
    
    @classmethod
    def get_today(cls) -> Optional['ProductivityEntry']:
        """Get today's productivity entry (with Redis caching)"""
        today = datetime.now().date().isoformat()
        db = get_database()
        redis_client = db.get_redis()
        
        # Check Redis cache first
        if redis_client:
            cached_prod = redis_client.get_cached_productivity(today)
            if cached_prod:
                return cls(**cached_prod)
        
        # Query database
        entry = cls.get_by_date(today)
        
        # Cache in Redis
        if entry and redis_client:
            redis_client.cache_productivity(today, entry.to_dict())
        
        return entry
    
    @classmethod
    def get_recent(cls, limit: int = 30) -> List['ProductivityEntry']:
        """Get recent productivity entries"""
        db = get_database()
        results = db.execute(
            "SELECT * FROM productivity_entries ORDER BY date DESC LIMIT ?",
            (limit,)
        )
        return [cls(**row) for row in results]
    
    def update(self):
        """Update productivity entry in database"""
        if not self.id:
            raise ValueError("Cannot update productivity entry without ID")
        
        db = get_database()
        self.updated_at = datetime.now().isoformat()
        
        db.execute_write(
            """UPDATE productivity_entries SET productivity_score = ?, tasks_completed = ?,
               tasks_total = ?, avg_mood_score = ?, focus_hours = ?, notes = ?, updated_at = ?
               WHERE id = ?""",
            (self.productivity_score, self.tasks_completed, self.tasks_total,
             self.avg_mood_score, self.focus_hours, self.notes, self.updated_at, self.id)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert productivity entry to dictionary"""
        return {
            "id": self.id,
            "date": self.date,
            "productivity_score": self.productivity_score,
            "tasks_completed": self.tasks_completed,
            "tasks_total": self.tasks_total,
            "avg_mood_score": self.avg_mood_score,
            "focus_hours": self.focus_hours,
            "notes": self.notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class TaskCompletion:
    """Task completion logging model"""
    
    def __init__(self, id: Optional[int] = None, task_id: int = 0,
                 completed_at: Optional[str] = None, duration_minutes: Optional[float] = None,
                 focus_score: Optional[int] = None, notes: Optional[str] = None,
                 created_at: Optional[str] = None):
        self.id = id
        self.task_id = task_id
        self.completed_at = completed_at or datetime.now().isoformat()
        self.duration_minutes = duration_minutes
        self.focus_score = focus_score  # 1-10 scale
        self.notes = notes
        self.created_at = created_at or datetime.now().isoformat()
    
    @classmethod
    def create(cls, task_id: int, duration_minutes: Optional[float] = None,
               focus_score: Optional[int] = None, notes: Optional[str] = None) -> 'TaskCompletion':
        """Create a new task completion log"""
        db = get_database()
        now = datetime.now().isoformat()
        
        completion_id = db.execute_write(
            """INSERT INTO task_completions (task_id, completed_at, duration_minutes, 
               focus_score, notes, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (task_id, now, duration_minutes, focus_score, notes, now)
        )
        
        return cls(id=completion_id, task_id=task_id, completed_at=now,
                  duration_minutes=duration_minutes, focus_score=focus_score,
                  notes=notes, created_at=now)
    
    @classmethod
    def get_by_task_id(cls, task_id: int) -> List['TaskCompletion']:
        """Get all completions for a task"""
        db = get_database()
        results = db.execute(
            "SELECT * FROM task_completions WHERE task_id = ? ORDER BY completed_at DESC",
            (task_id,)
        )
        return [cls(**row) for row in results]
    
    @classmethod
    def get_by_date(cls, date: str) -> List['TaskCompletion']:
        """Get all completions for a specific date"""
        db = get_database()
        # Use LIKE for compatibility with both SQLite and MySQL
        results = db.execute(
            """SELECT * FROM task_completions 
               WHERE completed_at LIKE ? 
               ORDER BY completed_at DESC""",
            (f"{date}%",)
        )
        return [cls(**row) for row in results]
    
    @classmethod
    def get_recent(cls, limit: int = 50) -> List['TaskCompletion']:
        """Get recent task completions"""
        db = get_database()
        results = db.execute(
            "SELECT * FROM task_completions ORDER BY completed_at DESC LIMIT ?",
            (limit,)
        )
        return [cls(**row) for row in results]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task completion to dictionary"""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "completed_at": self.completed_at,
            "duration_minutes": self.duration_minutes,
            "focus_score": self.focus_score,
            "notes": self.notes,
            "created_at": self.created_at
        }


class FocusSession:
    """Focus session tracking model"""
    
    def __init__(self, id: Optional[int] = None, started_at: Optional[str] = None,
                 ended_at: Optional[str] = None, duration_minutes: Optional[float] = None,
                 task_id: Optional[int] = None, notes: Optional[str] = None,
                 created_at: Optional[str] = None):
        self.id = id
        self.started_at = started_at or datetime.now().isoformat()
        self.ended_at = ended_at
        self.duration_minutes = duration_minutes
        self.task_id = task_id
        self.notes = notes
        self.created_at = created_at or datetime.now().isoformat()
    
    @classmethod
    def start(cls, task_id: Optional[int] = None, notes: Optional[str] = None) -> 'FocusSession':
        """Start a new focus session"""
        db = get_database()
        now = datetime.now().isoformat()
        
        session_id = db.execute_write(
            """INSERT INTO focus_sessions (started_at, task_id, notes, created_at)
               VALUES (?, ?, ?, ?)""",
            (now, task_id, notes, now)
        )
        
        return cls(id=session_id, started_at=now, task_id=task_id,
                  notes=notes, created_at=now)
    
    def end(self, notes: Optional[str] = None):
        """End a focus session and calculate duration"""
        if not self.id:
            raise ValueError("Cannot end session without ID")
        
        db = get_database()
        now = datetime.now().isoformat()
        self.ended_at = now
        
        # Calculate duration
        start_time = datetime.fromisoformat(self.started_at)
        end_time = datetime.fromisoformat(now)
        duration = (end_time - start_time).total_seconds() / 60.0  # minutes
        self.duration_minutes = duration
        
        if notes:
            self.notes = notes
        
        db.execute_write(
            """UPDATE focus_sessions SET ended_at = ?, duration_minutes = ?, notes = ?
               WHERE id = ?""",
            (self.ended_at, self.duration_minutes, self.notes, self.id)
        )
    
    @classmethod
    def get_active(cls) -> Optional['FocusSession']:
        """Get the currently active focus session (if any)"""
        db = get_database()
        results = db.execute(
            "SELECT * FROM focus_sessions WHERE ended_at IS NULL ORDER BY started_at DESC LIMIT 1",
            ()
        )
        if not results:
            return None
        return cls(**results[0])
    
    @classmethod
    def get_by_date(cls, date: str) -> List['FocusSession']:
        """Get all focus sessions for a specific date"""
        db = get_database()
        # Use LIKE for compatibility with both SQLite and MySQL
        results = db.execute(
            """SELECT * FROM focus_sessions 
               WHERE started_at LIKE ?
               ORDER BY started_at DESC""",
            (f"{date}%",)
        )
        return [cls(**row) for row in results]
    
    @classmethod
    def get_recent(cls, limit: int = 50) -> List['FocusSession']:
        """Get recent focus sessions"""
        db = get_database()
        results = db.execute(
            "SELECT * FROM focus_sessions ORDER BY started_at DESC LIMIT ?",
            (limit,)
        )
        return [cls(**row) for row in results]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert focus session to dictionary"""
        return {
            "id": self.id,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "duration_minutes": self.duration_minutes,
            "task_id": self.task_id,
            "notes": self.notes,
            "created_at": self.created_at
        }

