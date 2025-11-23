"""
Database initialization - Ensures database is set up when imported
"""
from .database import get_database

# Initialize database on import
_db = get_database()

# This ensures the database tables are created when models are imported
# The database initialization happens in EncryptedDatabase.__init__

