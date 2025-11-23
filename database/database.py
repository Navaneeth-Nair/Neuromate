"""
Database Wrapper - Supports MySQL (primary) and SQLite (fallback)
Provides AES-256 encryption for sensitive data
"""
import sqlite3
import os
import json
from typing import Optional, List, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from dotenv import load_dotenv

load_dotenv()

# Try to import MySQL client
try:
    from .mysql_client import get_mysql_database, MySQLDatabase
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    MySQLDatabase = None

# Try to import Redis client
try:
    from .redis_client import get_redis_client, RedisClient
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    RedisClient = None


class EncryptedDatabase:
    """
    Database wrapper supporting MySQL (primary) and SQLite (fallback)
    Uses Redis for caching when available
    """
    
    def __init__(self, 
                 db_path: str = "data/neuromate.db", 
                 password: Optional[str] = None,
                 use_mysql: Optional[bool] = None,
                 use_redis: Optional[bool] = None):
        """
        Initialize database
        
        Args:
            db_path: SQLite database path (if using SQLite)
            password: Encryption password
            use_mysql: Force MySQL usage (None = auto-detect from env)
            use_redis: Force Redis usage (None = auto-detect)
        """
        self.db_path = db_path
        self.encrypted_db_path = db_path + ".encrypted"
        
        # Determine database type
        if use_mysql is None:
            use_mysql = os.getenv("USE_MYSQL", "false").lower() == "true" and MYSQL_AVAILABLE
        else:
            use_mysql = use_mysql and MYSQL_AVAILABLE
        
        self.use_mysql = use_mysql
        self.mysql_db = None
        
        # Determine Redis usage
        if use_redis is None:
            use_redis = os.getenv("USE_REDIS", "true").lower() == "true" and REDIS_AVAILABLE
        else:
            use_redis = use_redis and REDIS_AVAILABLE
        
        self.use_redis = use_redis
        self.redis_client = None
        
        # Generate or load encryption key
        if password:
            self.cipher = self._generate_cipher_from_password(password)
        else:
            self.cipher = self._load_or_generate_key()
        
        # Initialize database
        if self.use_mysql:
            try:
                self.mysql_db = get_mysql_database(password_encryption=password)
                print("Using MySQL database")
            except Exception as e:
                print(f"Failed to connect to MySQL: {e}")
                print("Falling back to SQLite")
                self.use_mysql = False
                self._init_sqlite_database()
        else:
            self._init_sqlite_database()
        
        # Initialize Redis if available
        if self.use_redis:
            try:
                self.redis_client = get_redis_client()
                if self.redis_client.is_connected():
                    print("Redis caching enabled")
                else:
                    print("Redis not available, continuing without cache")
                    self.use_redis = False
            except Exception as e:
                print(f"Redis initialization failed: {e}")
                self.use_redis = False
    
    def _generate_cipher_from_password(self, password: str) -> Fernet:
        """Generate Fernet cipher from password"""
        # Use PBKDF2HMAC to derive key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'neuromate_salt',  # In production, use random salt per database
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key)
    
    def _load_or_generate_key(self) -> Fernet:
        """Load encryption key from file or generate new one"""
        key_file = "data/db_key.key"
        
        if os.path.exists(key_file):
            try:
                with open(key_file, 'rb') as f:
                    key = f.read()
                return Fernet(key)
            except Exception as e:
                print(f"Warning: Could not load key file: {e}")
        
        # Generate new key
        key = Fernet.generate_key()
        try:
            with open(key_file, 'wb') as f:
                f.write(key)
            # Make key file readable only by owner
            os.chmod(key_file, 0o600)
        except Exception as e:
            print(f"Warning: Could not save key file: {e}")
        
        return Fernet(key)
    
    def _encrypt_data(self, data: str) -> bytes:
        """Encrypt string data"""
        return self.cipher.encrypt(data.encode('utf-8'))
    
    def _decrypt_data(self, encrypted_data: bytes) -> str:
        """Decrypt data to string"""
        return self.cipher.decrypt(encrypted_data).decode('utf-8')
    
    def _init_sqlite_database(self):
        """Initialize SQLite database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                due_date TEXT,
                priority INTEGER DEFAULT 5,
                status TEXT DEFAULT 'pending',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                encrypted_data BLOB
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mood_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mood_score INTEGER NOT NULL,
                mood_text TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                encrypted_data BLOB
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS journal_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                entry_type TEXT DEFAULT 'general',
                created_at TEXT NOT NULL,
                encrypted_data BLOB
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                frequency TEXT DEFAULT 'daily',
                streak_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                encrypted_data BLOB
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productivity_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                productivity_score REAL NOT NULL,
                tasks_completed INTEGER DEFAULT 0,
                tasks_total INTEGER DEFAULT 0,
                avg_mood_score REAL,
                focus_hours REAL DEFAULT 0,
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                encrypted_data BLOB
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                completed_at TEXT NOT NULL,
                duration_minutes REAL,
                focus_score INTEGER,
                notes TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS focus_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                duration_minutes REAL,
                task_id INTEGER,
                notes TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE SET NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def execute(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results
        
        Args:
            query: SQL SELECT query
            params: Query parameters
            
        Returns:
            List of dictionaries representing rows
        """
        if self.use_mysql and self.mysql_db:
            return self.mysql_db.execute(query, params)
        
        # SQLite fallback
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Convert rows to dictionaries
        results = []
        for row in rows:
            row_dict = dict(row)
            # Decrypt encrypted_data if present
            if 'encrypted_data' in row_dict and row_dict['encrypted_data']:
                try:
                    decrypted = self._decrypt_data(row_dict['encrypted_data'])
                    # Merge decrypted JSON with row data
                    decrypted_data = json.loads(decrypted)
                    row_dict.update(decrypted_data)
                except Exception as e:
                    print(f"Warning: Could not decrypt data: {e}")
            # Remove encrypted_data field
            row_dict.pop('encrypted_data', None)
            results.append(row_dict)
        
        conn.close()
        return results
    
    def execute_write(self, query: str, params: tuple = ()) -> int:
        """
        Execute an INSERT/UPDATE/DELETE query
        
        Args:
            query: SQL write query
            params: Query parameters
            
        Returns:
            Last inserted row ID (for INSERT) or affected rows count
        """
        if self.use_mysql and self.mysql_db:
            result = self.mysql_db.execute_write(query, params)
            # Invalidate Redis cache on write
            if self.use_redis and self.redis_client:
                self._invalidate_cache_for_query(query)
            return result
        
        # SQLite fallback
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(query, params)
        conn.commit()
        
        last_id = cursor.lastrowid
        affected = cursor.rowcount
        
        conn.close()
        
        # Invalidate Redis cache on write
        if self.use_redis and self.redis_client:
            self._invalidate_cache_for_query(query)
        
        return last_id if last_id else affected
    
    def _invalidate_cache_for_query(self, query: str):
        """Invalidate relevant Redis cache based on query"""
        if not self.use_redis or not self.redis_client:
            return
        
        query_lower = query.lower()
        if 'tasks' in query_lower:
            self.redis_client.invalidate_task_cache()
        if 'mood' in query_lower:
            self.redis_client.invalidate_mood_cache()
        if 'productivity' in query_lower:
            self.redis_client.invalidate_productivity_cache()
    
    def close(self):
        """Close database connections"""
        if self.use_mysql and self.mysql_db:
            self.mysql_db.close()
        if self.use_redis and self.redis_client:
            self.redis_client.close()
    
    def get_redis(self) -> Optional[RedisClient]:
        """Get Redis client instance"""
        return self.redis_client if self.use_redis else None


# Global database instance
_db_instance: Optional[EncryptedDatabase] = None


def get_database(password: Optional[str] = None, **kwargs) -> EncryptedDatabase:
    """
    Get or create global database instance
    
    Args:
        password: Encryption password
        **kwargs: Additional arguments (use_mysql, use_redis, etc.)
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = EncryptedDatabase(password=password, **kwargs)
    return _db_instance

