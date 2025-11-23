"""
Populate Sample Data - Creates sample data for testing dashboard and analytics
"""
from datetime import datetime, timedelta
from database import Task, MoodEntry, TaskCompletion, FocusSession, ProductivityEntry
from backend.modules.focus_tracker import get_focus_tracker
from backend.modules.productivity_tracker import get_productivity_tracker
import random

def populate_sample_data():
    """Populate database with sample data for the past 7 days"""
    print("Populating sample data...")
    
    # Get today's date
    today = datetime.now().date()
    
    # Sample tasks
    task_titles = [
        "Complete project proposal",
        "Review code changes",
        "Write documentation",
        "Team meeting preparation",
        "Update website content",
        "Fix bug in login system",
        "Design new feature",
        "Write unit tests",
        "Code review",
        "Deploy to staging"
    ]
    
    # Create tasks over the past week
    tasks_created = []
    for i in range(7):
        date = today - timedelta(days=i)
        # Create 2-4 tasks per day
        num_tasks = random.randint(2, 4)
        for j in range(num_tasks):
            task_title = random.choice(task_titles)
            priority = random.randint(3, 9)
            due_date = (date + timedelta(days=random.randint(0, 3))).isoformat()
            
            task = Task.create(
                title=f"{task_title} (Day {i+1})",
                description=f"Sample task created on {date.isoformat()}",
                priority=priority,
                due_date=due_date
            )
            tasks_created.append((task, date))
    
    print(f"Created {len(tasks_created)} tasks")
    
    # Complete some tasks and create completion logs
    completions_by_date = {}
    for task, created_date in tasks_created:
        # 60% chance of completion
        if random.random() < 0.6:
            # Complete on a random day after creation
            days_after = random.randint(0, 3)
            completion_date = created_date + timedelta(days=days_after)
            
            # Update task status
            task.status = "completed"
            task.updated_at = completion_date.isoformat() + "T" + datetime.now().strftime("%H:%M:%S")
            task.update()
            
            # Create completion log
            duration_minutes = random.randint(30, 180)
            focus_score = random.randint(5, 10)
            
            completion = TaskCompletion.create(
                task_id=task.id,
                duration_minutes=duration_minutes,
                focus_score=focus_score,
                notes=f"Completed on {completion_date.isoformat()}"
            )
            
            # Update completion timestamp to match completion date
            db = task.__class__.__module__
            from database import get_database
            db_instance = get_database()
            completion_date_str = completion_date.isoformat() + "T" + datetime.now().strftime("%H:%M:%S")
            db_instance.execute_write(
                "UPDATE task_completions SET completed_at = ? WHERE id = ?",
                (completion_date_str, completion.id)
            )
            
            if completion_date not in completions_by_date:
                completions_by_date[completion_date] = []
            completions_by_date[completion_date].append(completion)
    
    print(f"Created completion logs for {sum(len(v) for v in completions_by_date.values())} tasks")
    
    # Create mood entries for each day
    mood_entries = {}
    mood_texts = [
        ("happy", 8), ("excited", 9), ("content", 7), ("calm", 6),
        ("tired", 4), ("stressed", 3), ("anxious", 5), ("motivated", 8),
        ("focused", 7), ("relaxed", 6)
    ]
    
    for i in range(7):
        date = today - timedelta(days=i)
        mood_text, base_score = random.choice(mood_texts)
        mood_score = base_score + random.randint(-1, 1)
        mood_score = max(1, min(10, mood_score))
        
        mood_entry = MoodEntry.create(
            mood_score=mood_score,
            mood_text=mood_text,
            notes=f"Sample mood entry for {date.isoformat()}"
        )
        
        # Update created_at to match the date
        from database import get_database
        db_instance = get_database()
        date_str = date.isoformat() + "T" + datetime.now().strftime("%H:%M:%S")
        db_instance.execute_write(
            "UPDATE mood_entries SET created_at = ? WHERE id = ?",
            (date_str, mood_entry.id)
        )
        
        mood_entries[date] = mood_entry
    
    print(f"Created {len(mood_entries)} mood entries")
    
    # Create focus sessions for each day
    focus_tracker = get_focus_tracker()
    for i in range(7):
        date = today - timedelta(days=i)
        # 1-3 focus sessions per day
        num_sessions = random.randint(1, 3)
        
        for j in range(num_sessions):
            # Random start time during the day (9 AM to 6 PM)
            start_hour = random.randint(9, 18)
            start_minute = random.randint(0, 59)
            start_time = datetime.combine(date, datetime.min.time().replace(hour=start_hour, minute=start_minute))
            
            # Duration: 30 minutes to 2 hours
            duration_minutes = random.randint(30, 120)
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            # Create session
            session = FocusSession.start()
            
            # Update timestamps
            from database import get_database
            db_instance = get_database()
            start_str = start_time.isoformat()
            end_str = end_time.isoformat()
            
            db_instance.execute_write(
                "UPDATE focus_sessions SET started_at = ?, ended_at = ?, duration_minutes = ? WHERE id = ?",
                (start_str, end_str, duration_minutes, session.id)
            )
    
    print(f"Created focus sessions for the past 7 days")
    
    # Generate productivity entries for each day
    productivity_tracker = get_productivity_tracker()
    for i in range(7):
        date = today - timedelta(days=i)
        try:
            productivity_entry = productivity_tracker.calculate_daily_productivity(date.isoformat())
            print(f"Generated productivity entry for {date.isoformat()}: {productivity_entry.productivity_score:.1f}/100")
        except Exception as e:
            print(f"Error generating productivity for {date.isoformat()}: {e}")
    
    print("\n[SUCCESS] Sample data populated successfully!")
    print("\nSummary:")
    print(f"- Tasks created: {len(tasks_created)}")
    print(f"- Tasks completed: {sum(len(v) for v in completions_by_date.values())}")
    print(f"- Mood entries: {len(mood_entries)}")
    print(f"- Focus sessions: Multiple sessions across 7 days")
    print(f"- Productivity entries: 7 days")
    print("\nYou can now view the dashboard with: python -c 'from dashboard import get_dashboard; get_dashboard().display_full_dashboard()'")

if __name__ == "__main__":
    populate_sample_data()

