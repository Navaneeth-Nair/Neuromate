"""
Backup and Export functionality for NeuroMate database
"""
import json
from datetime import datetime
from .models import Task, MoodEntry, JournalEntry
from .database import get_database


def export_to_json(output_file: str = None) -> str:
    """
    Export all data to JSON file
    
    Args:
        output_file: Output file path (default: neuromate_backup_YYYYMMDD_HHMMSS.json)
        
    Returns:
        Path to exported file
    """
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"data/neuromate_backup_{timestamp}.json"
    
    # Collect all data
    data = {
        "export_date": datetime.now().isoformat(),
        "version": "1.0",
        "tasks": [task.to_dict() for task in Task.get_all()],
        "mood_entries": [mood.to_dict() for mood in MoodEntry.get_recent(limit=1000)],
        "journal_entries": [entry.to_dict() for entry in JournalEntry.get_recent(limit=1000)]
    }
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Data exported to {output_file}")
    return output_file


def import_from_json(input_file: str, clear_existing: bool = False):
    """
    Import data from JSON backup file
    
    Args:
        input_file: Path to JSON backup file
        clear_existing: If True, clear existing data before importing
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if clear_existing:
        # Clear existing data (optional - be careful!)
        db = get_database()
        db.execute_write("DELETE FROM tasks")
        db.execute_write("DELETE FROM mood_entries")
        db.execute_write("DELETE FROM journal_entries")
    
    # Import tasks
    for task_data in data.get("tasks", []):
        Task.create(
            title=task_data.get("title", ""),
            description=task_data.get("description", ""),
            due_date=task_data.get("due_date"),
            priority=task_data.get("priority", 5)
        )
    
    # Import mood entries
    for mood_data in data.get("mood_entries", []):
        MoodEntry.create(
            mood_score=mood_data.get("mood_score", 5),
            mood_text=mood_data.get("mood_text", ""),
            notes=mood_data.get("notes", "")
        )
    
    # Import journal entries
    for journal_data in data.get("journal_entries", []):
        JournalEntry.create(
            content=journal_data.get("content", ""),
            entry_type=journal_data.get("entry_type", "general")
        )
    
    print(f"Data imported from {input_file}")


if __name__ == "__main__":
    # Example usage
    export_file = export_to_json()
    print(f"Backup created: {export_file}")

