"""
Database package - exports main database classes and models
"""
from .database import get_database, EncryptedDatabase
from .models import (
    Task, MoodEntry, JournalEntry, Habit, ProductivityEntry,
    TaskCompletion, FocusSession
)

# Try to import MySQL and Redis clients
try:
    from .mysql_client import get_mysql_database, MySQLDatabase
except ImportError:
    MySQLDatabase = None
    get_mysql_database = None

try:
    from .redis_client import get_redis_client, RedisClient
except ImportError:
    RedisClient = None
    get_redis_client = None

__all__ = [
    'get_database', 'EncryptedDatabase',
    'Task', 'MoodEntry', 'JournalEntry', 'Habit', 'ProductivityEntry',
    'TaskCompletion', 'FocusSession',
    'MySQLDatabase', 'get_mysql_database',
    'RedisClient', 'get_redis_client'
]

