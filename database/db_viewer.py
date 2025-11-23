"""
Database Viewer - View and inspect NeuroMate database contents
"""
from .models import Task, MoodEntry, JournalEntry
from .database import get_database
from datetime import datetime
import json


def view_tasks(status_filter=None):
    """View all tasks"""
    print("\n" + "="*60)
    print("TASKS")
    print("="*60)
    
    if status_filter:
        tasks = Task.get_all(status=status_filter)
        print(f"Filter: {status_filter.upper()}")
    else:
        tasks = Task.get_all()
    
    if not tasks:
        print("No tasks found.")
        return
    
    print(f"\nTotal: {len(tasks)} task(s)\n")
    
    for task in tasks:
        print(f"ID: {task.id}")
        print(f"  Title: {task.title}")
        if task.description:
            print(f"  Description: {task.description}")
        if task.due_date:
            print(f"  Due Date: {task.due_date}")
        print(f"  Priority: {task.priority}/10")
        print(f"  Status: {task.status.upper()}")
        print(f"  Created: {task.created_at}")
        print(f"  Updated: {task.updated_at}")
        print()


def view_mood_entries(limit=10):
    """View recent mood entries"""
    print("\n" + "="*60)
    print("MOOD ENTRIES")
    print("="*60)
    
    entries = MoodEntry.get_recent(limit=limit)
    
    if not entries:
        print("No mood entries found.")
        return
    
    print(f"\nShowing {len(entries)} most recent entries:\n")
    
    for entry in entries:
        print(f"ID: {entry.id}")
        print(f"  Mood Score: {entry.mood_score}/10")
        if entry.mood_text:
            print(f"  Mood Text: {entry.mood_text}")
        if entry.notes:
            print(f"  Notes: {entry.notes}")
        print(f"  Date: {entry.created_at}")
        print()


def view_journal_entries(limit=20, entry_type=None):
    """View recent journal entries"""
    print("\n" + "="*60)
    print("JOURNAL ENTRIES")
    print("="*60)
    
    entries = JournalEntry.get_recent(limit=limit, entry_type=entry_type)
    
    if not entries:
        print("No journal entries found.")
        return
    
    print(f"\nShowing {len(entries)} most recent entries:\n")
    
    for entry in entries:
        print(f"ID: {entry.id}")
        print(f"  Type: {entry.entry_type}")
        print(f"  Content: {entry.content[:100]}{'...' if len(entry.content) > 100 else ''}")
        print(f"  Date: {entry.created_at}")
        print()


def view_statistics():
    """View database statistics"""
    print("\n" + "="*60)
    print("DATABASE STATISTICS")
    print("="*60)
    
    all_tasks = Task.get_all()
    pending_tasks = [t for t in all_tasks if t.status == "pending"]
    completed_tasks = [t for t in all_tasks if t.status == "completed"]
    
    mood_entries = MoodEntry.get_recent(limit=1000)
    journal_entries = JournalEntry.get_recent(limit=1000)
    
    print(f"\nTasks:")
    print(f"  Total: {len(all_tasks)}")
    print(f"  Pending: {len(pending_tasks)}")
    print(f"  Completed: {len(completed_tasks)}")
    
    print(f"\nMood Entries: {len(mood_entries)}")
    if mood_entries:
        avg_mood = sum(e.mood_score for e in mood_entries) / len(mood_entries)
        print(f"  Average Mood: {avg_mood:.1f}/10")
    
    print(f"\nJournal Entries: {len(journal_entries)}")
    
    # Count by type
    if journal_entries:
        type_counts = {}
        for entry in journal_entries:
            type_counts[entry.entry_type] = type_counts.get(entry.entry_type, 0) + 1
        print(f"  By Type:")
        for entry_type, count in type_counts.items():
            print(f"    {entry_type}: {count}")


def view_all():
    """View all data"""
    view_statistics()
    view_tasks()
    view_mood_entries()
    view_journal_entries()


def interactive_menu():
    """Interactive menu for viewing database"""
    while True:
        print("\n" + "="*60)
        print("NEUROMATE DATABASE VIEWER")
        print("="*60)
        print("\n1. View All Tasks")
        print("2. View Pending Tasks")
        print("3. View Completed Tasks")
        print("4. View Mood Entries")
        print("5. View Journal Entries")
        print("6. View Voice Commands Only")
        print("7. View Statistics")
        print("8. View Everything")
        print("9. Export to JSON")
        print("0. Exit")
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == "1":
            view_tasks()
        elif choice == "2":
            view_tasks(status_filter="pending")
        elif choice == "3":
            view_tasks(status_filter="completed")
        elif choice == "4":
            limit = input("How many entries? (default 10): ").strip()
            limit = int(limit) if limit.isdigit() else 10
            view_mood_entries(limit=limit)
        elif choice == "5":
            limit = input("How many entries? (default 20): ").strip()
            limit = int(limit) if limit.isdigit() else 20
            view_journal_entries(limit=limit)
        elif choice == "6":
            view_journal_entries(entry_type="voice_command")
        elif choice == "7":
            view_statistics()
        elif choice == "8":
            view_all()
        elif choice == "9":
            from backup import export_to_json
            filename = export_to_json()
            print(f"\nExported to: {filename}")
        elif choice == "0":
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid choice. Please try again.")


if __name__ == "__main__":
    import sys
    
    # Ensure database is initialized
    import db_init
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "tasks":
            view_tasks()
        elif command == "mood":
            view_mood_entries()
        elif command == "journal":
            view_journal_entries()
        elif command == "stats":
            view_statistics()
        elif command == "all":
            view_all()
        else:
            print(f"Unknown command: {command}")
            print("Usage: python db_viewer.py [tasks|mood|journal|stats|all]")
    else:
        # Interactive mode
        interactive_menu()

