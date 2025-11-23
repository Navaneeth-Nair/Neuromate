"""
Quick database query script - Simple way to query the database
"""
from .models import Task, MoodEntry, JournalEntry
from . import db_init

def quick_view():
    """Quick overview of database contents"""
    print("\n" + "="*70)
    print("NEUROMATE DATABASE - QUICK VIEW")
    print("="*70)
    
    # Tasks
    tasks = Task.get_all()
    pending = [t for t in tasks if t.status == "pending"]
    print(f"\n[TASKS] Total: {len(tasks)} | Pending: {len(pending)} | Completed: {len([t for t in tasks if t.status == 'completed'])}")
    if pending:
        print("  Pending Tasks:")
        for task in pending[:5]:  # Show first 5
            print(f"    - {task.title} (Priority: {task.priority})")
        if len(pending) > 5:
            print(f"    ... and {len(pending) - 5} more")
    
    # Mood
    mood = MoodEntry.get_today()
    if mood:
        print(f"\n[MOOD] Today: {mood.mood_score}/10 - {mood.mood_text}")
    else:
        print("\n[MOOD] No mood entry today")
    
    # Recent journal entries
    journal = JournalEntry.get_recent(limit=5)
    print(f"\n[JOURNAL] Recent entries: {len(journal)}")
    for entry in journal[:3]:  # Show first 3
        content_preview = entry.content[:50] + "..." if len(entry.content) > 50 else entry.content
        print(f"  - [{entry.entry_type}] {content_preview}")
    
    print("\n" + "="*70)
    print("For detailed view, run: python db_viewer.py")
    print("="*70 + "\n")


if __name__ == "__main__":
    quick_view()

