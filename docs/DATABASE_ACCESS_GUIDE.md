# How to Access and View NeuroMate Database

## Quick Methods

### Method 1: Quick View Script (Simplest)
```bash
python quick_view.py
```
Shows a quick summary of:
- Tasks (total, pending, completed)
- Today's mood
- Recent journal entries

### Method 2: Interactive Database Viewer (Recommended)
```bash
python db_viewer.py
```

This opens an interactive menu where you can:
1. View All Tasks
2. View Pending Tasks
3. View Completed Tasks
4. View Mood Entries
5. View Journal Entries
6. View Voice Commands Only
7. View Statistics
8. View Everything
9. Export to JSON
0. Exit

### Method 3: Command Line Arguments
```bash
# View tasks only
python db_viewer.py tasks

# View mood entries only
python db_viewer.py mood

# View journal entries only
python db_viewer.py journal

# View statistics only
python db_viewer.py stats

# View everything
python db_viewer.py all
```

## Direct SQLite Access

The database is stored as `neuromate.db` in your project directory. You can access it directly using SQLite:

### Using SQLite Command Line
```bash
sqlite3 neuromate.db
```

Then run SQL queries:
```sql
-- View all tasks
SELECT * FROM tasks;

-- View pending tasks
SELECT * FROM tasks WHERE status = 'pending';

-- View mood entries
SELECT * FROM mood_entries ORDER BY created_at DESC;

-- View journal entries
SELECT * FROM journal_entries ORDER BY created_at DESC LIMIT 10;

-- View statistics
SELECT 
    (SELECT COUNT(*) FROM tasks) as total_tasks,
    (SELECT COUNT(*) FROM tasks WHERE status = 'pending') as pending_tasks,
    (SELECT COUNT(*) FROM mood_entries) as mood_entries,
    (SELECT COUNT(*) FROM journal_entries) as journal_entries;
```

### Using Python Script
```python
from database import get_database

db = get_database()

# Query tasks
tasks = db.execute("SELECT * FROM tasks WHERE status = 'pending'")
for task in tasks:
    print(task)

# Query mood entries
moods = db.execute("SELECT * FROM mood_entries ORDER BY created_at DESC LIMIT 5")
for mood in moods:
    print(mood)
```

## Using Python Models (Programmatic Access)

### View Tasks
```python
from models import Task

# Get all tasks
tasks = Task.get_all()
for task in tasks:
    print(f"{task.title} - {task.status}")

# Get pending tasks only
pending = Task.get_all(status="pending")

# Get a specific task
task = Task.get_by_id(1)
print(task.title)
```

### View Mood Entries
```python
from models import MoodEntry

# Get today's mood
today_mood = MoodEntry.get_today()
if today_mood:
    print(f"Mood: {today_mood.mood_score}/10")

# Get recent mood entries
recent_moods = MoodEntry.get_recent(limit=10)
for mood in recent_moods:
    print(f"{mood.created_at}: {mood.mood_score}/10 - {mood.mood_text}")
```

### View Journal Entries
```python
from models import JournalEntry

# Get all journal entries
entries = JournalEntry.get_recent(limit=20)

# Get only voice commands
voice_commands = JournalEntry.get_recent(limit=20, entry_type="voice_command")

for entry in entries:
    print(f"[{entry.entry_type}] {entry.content}")
```

## Export Data

### Export to JSON
```python
from backup import export_to_json

# Export with auto-generated filename
backup_file = export_to_json()
print(f"Exported to: {backup_file}")

# Export to specific file
export_to_json("my_backup.json")
```

Or use the interactive viewer:
```bash
python db_viewer.py
# Choose option 9
```

## Database File Location

- **Database file**: `neuromate.db` (SQLite database)
- **Encryption key**: `db_key.key` (auto-generated, keep secure!)
- **Conversation history**: `conversation_history.json`
- **Backup files**: `neuromate_backup_YYYYMMDD_HHMMSS.json`

## Database Schema

### Tasks Table
- `id` - Primary key
- `title` - Task title
- `description` - Task description
- `due_date` - Due date (ISO format)
- `priority` - Priority (1-10)
- `status` - Status (pending, in_progress, completed, cancelled)
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

### Mood Entries Table
- `id` - Primary key
- `mood_score` - Mood score (1-10)
- `mood_text` - Mood description text
- `notes` - Additional notes
- `created_at` - Creation timestamp

### Journal Entries Table
- `id` - Primary key
- `content` - Journal entry content
- `entry_type` - Type (general, reflection, voice_command, ai_conversation)
- `created_at` - Creation timestamp

## Tips

1. **Regular Backups**: Use the export function regularly to backup your data
2. **Privacy**: The database file contains your personal data - keep it secure
3. **Viewing**: Use `db_viewer.py` for the easiest way to browse your data
4. **Debugging**: Use SQLite directly if you need to inspect raw data
5. **Data Growth**: Journal entries can grow large - consider periodic cleanup

## Example: View What Was Logged Today

```python
from models import Task, MoodEntry, JournalEntry
from datetime import datetime

today = datetime.now().date().isoformat()

# Tasks created today
tasks = Task.get_all()
today_tasks = [t for t in tasks if t.created_at.startswith(today)]
print(f"Tasks created today: {len(today_tasks)}")

# Mood entries today
mood = MoodEntry.get_today()
if mood:
    print(f"Today's mood: {mood.mood_score}/10")

# Journal entries today
entries = JournalEntry.get_recent(limit=1000)
today_entries = [e for e in entries if e.created_at.startswith(today)]
print(f"Journal entries today: {len(today_entries)}")
```

