# NeuroMate Project Structure

This document describes the reorganized project structure.

## Directory Layout

```
neuroamte/
├── main.py                    # Entry point (voice/text mode)
├── requirements.txt            # Python dependencies
├── .env                       # Environment variables (API keys)
│
├── backend/                    # Backend package
│   ├── __init__.py
│   ├── modules/               # Core application modules
│   │   ├── __init__.py
│   │   ├── ai_chat.py         # AI conversation (Gemini API)
│   │   ├── ai_planner.py     # AI planning assistant
│   │   ├── analytics_engine.py # Analytics and aggregation
│   │   ├── command_handler.py # Command execution
│   │   ├── command_parser.py  # Voice command parsing
│   │   ├── conversation_context.py # Conversation history
│   │   ├── dashboard.py      # CLI dashboard
│   │   ├── focus_tracker.py   # Focus session tracking
│   │   ├── motivation_engine.py # Motivation & tone adaptation
│   │   ├── notification_system.py # Adaptive notifications
│   │   ├── productivity_tracker.py # Productivity tracking
│   │   ├── reflection_workflow.py # Reflection workflows
│   │   ├── safety_filter.py  # Content filtering
│   │   └── tts.py            # Text-to-speech engine
│   │
│   └── interfaces/           # User interface modules
│       ├── __init__.py
│       ├── quick_text.py     # Quick text command processor
│       ├── speechrecog.py    # Speech recognition & voice mode
│       └── text_input.py     # Text input mode interface
│
├── database/                  # Database layer
│   ├── __init__.py           # Package exports
│   ├── backup.py            # Backup/export functionality
│   ├── database.py          # Database wrapper (MySQL/SQLite)
│   ├── db_init.py           # Database initialization
│   ├── db_viewer.py         # Database viewer utility
│   ├── migrate_to_mysql.py  # SQLite to MySQL migration
│   ├── models.py            # Data models (Task, Mood, etc.)
│   ├── mysql_client.py      # MySQL client
│   ├── quick_view.py        # Quick database summary
│   └── redis_client.py      # Redis caching client
│
├── tests/                    # Test files
│   ├── __init__.py
│   ├── populate_sample_data.py # Sample data generator
│   ├── test_all_features.py # Comprehensive feature tests
│   └── test_db.py           # Database tests
│
├── data/                     # Runtime data files
│   ├── ai_context.txt       # AI personality definition
│   ├── client_question.txt  # User input buffer
│   ├── conversation_history.json # Conversation history
│   ├── db_key.key           # Encryption key
│   ├── filtered_response.txt # Filtered response log
│   ├── neuromate.db         # SQLite database
│   ├── neuromate_backup_*.json # Backup files
│   └── response.txt         # AI response buffer
│
└── docs/                     # Documentation
    ├── DATABASE_ACCESS_GUIDE.md
    ├── DEVELOPMENT_LOG.md
    ├── DEVELOPMENT_STATUS.md
    ├── MIGRATION_COMPLETE.md
    ├── MYSQL_REDIS_SETUP.md
    ├── PLANNING.txt
    ├── README.md
    ├── REDIS_USAGE.md
    └── TTS_WINDOWS_FIX.md
```

## Import Patterns

### From Root (main.py, tests)
```python
from database import Task, MoodEntry, get_database
from backend.modules import command_handler, tts
from backend.interfaces import speechrecog, text_input
```

### Within Backend Modules
```python
from .command_parser import parse_command
from database import Task, MoodEntry
from .ai_chat import response
```

### Within Database Package
```python
from .database import get_database
from .models import Task, MoodEntry
```

## File Paths

All runtime data files are now in the `data/` folder:
- `data/response.txt` - AI response buffer
- `data/client_question.txt` - User input buffer
- `data/ai_context.txt` - AI personality
- `data/conversation_history.json` - Conversation history
- `data/neuromate.db` - SQLite database
- `data/db_key.key` - Encryption key

## Running the Application

```bash
# Voice mode (default)
python main.py

# Text mode
python main.py --text

# Quick text command
python -m backend.interfaces.quick_text "add task test"
```

## Testing

```bash
# Run all tests
python tests/test_all_features.py

# Test database
python tests/test_db.py

# Populate sample data
python tests/populate_sample_data.py
```

## Key Changes

1. **Organized Structure**: Files are now grouped by function (database, backend modules, interfaces, tests, data, docs)
2. **Package Imports**: All modules use proper Python package imports
3. **Centralized Data**: All runtime data files are in `data/` folder
4. **Documentation**: All docs moved to `docs/` folder
5. **Maintainability**: Clear separation of concerns makes the codebase easier to navigate and maintain

## Migration Notes

- All imports have been updated to use the new structure
- File paths have been updated to point to `data/` folder
- Database path defaults to `data/neuromate.db`
- All functionality preserved - no features were lost in the reorganization

