"""
MySQL Database Client - Connection wrapper for MySQL database
Supports connection pooling and error handling
"""
import os
import json
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import pymysql
from pymysql.cursors import DictCursor
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

load_dotenv()


class MySQLDatabase:
    """MySQL database wrapper with encryption support"""
    
    def __init__(self, 
                 host: Optional[str] = None,
                 port: int = 3306,
                 user: Optional[str] = None,
                 password: Optional[str] = None,
                 database: Optional[str] = None,
                 password_encryption: Optional[str] = None):
        """
        Initialize MySQL database connection
        
        Args:
            host: MySQL host (defaults to MYSQL_HOST env var)
            port: MySQL port (defaults to 3306)
            user: MySQL user (defaults to MYSQL_USER env var)
            password: MySQL password (defaults to MYSQL_PASSWORD env var)
            database: Database name (defaults to MYSQL_DATABASE env var)
            password_encryption: Password for encryption key derivation
        """
        self.host = host or os.getenv("MYSQL_HOST", "localhost")
        self.port = int(os.getenv("MYSQL_PORT", port))
        self.user = user or os.getenv("MYSQL_USER", "root")
        self.password = password or os.getenv("MYSQL_PASSWORD", "")
        self.database = database or os.getenv("MYSQL_DATABASE", "neuromate")
        
        # Encryption setup
        if password_encryption:
            self.cipher = self._generate_cipher_from_password(password_encryption)
        else:
            self.cipher = self._load_or_generate_key()
        
        # Connection pool
        self.connection = None
        self._connect()
        self._init_database()
    
    def _generate_cipher_from_password(self, password: str) -> Fernet:
        """Generate Fernet cipher from password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'neuromate_salt',
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key)
    
    def _load_or_generate_key(self) -> Fernet:
        """Load encryption key from file or generate new one"""
        key_file = "db_key.key"
        
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
    
    def _connect(self):
        """Establish MySQL connection"""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                cursorclass=DictCursor,
                charset='utf8mb4',
                autocommit=False
            )
        except pymysql.Error as e:
            print(f"Error connecting to MySQL: {e}")
            raise
    
    def _reconnect(self):
        """Reconnect if connection is lost"""
        try:
            self.connection.ping(reconnect=True)
        except:
            self._connect()
    
    def _init_database(self):
        """Initialize database schema"""
        try:
            cursor = self.connection.cursor()
            
            # Create tables with MySQL syntax
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(500) NOT NULL,
                    description TEXT,
                    due_date VARCHAR(50),
                    priority INT DEFAULT 5,
                    status VARCHAR(50) DEFAULT 'pending',
                    created_at VARCHAR(100) NOT NULL,
                    updated_at VARCHAR(100) NOT NULL,
                    encrypted_data BLOB,
                    INDEX idx_status (status),
                    INDEX idx_due_date (due_date),
                    INDEX idx_priority (priority)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mood_entries (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    mood_score INT NOT NULL,
                    mood_text VARCHAR(200),
                    notes TEXT,
                    created_at VARCHAR(100) NOT NULL,
                    encrypted_data BLOB,
                    INDEX idx_created_at (created_at),
                    INDEX idx_mood_score (mood_score)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS journal_entries (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    content TEXT NOT NULL,
                    entry_type VARCHAR(50) DEFAULT 'general',
                    created_at VARCHAR(100) NOT NULL,
                    encrypted_data BLOB,
                    INDEX idx_entry_type (entry_type),
                    INDEX idx_created_at (created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS habits (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    description TEXT,
                    frequency VARCHAR(50) DEFAULT 'daily',
                    streak_count INT DEFAULT 0,
                    created_at VARCHAR(100) NOT NULL,
                    updated_at VARCHAR(100) NOT NULL,
                    encrypted_data BLOB,
                    INDEX idx_name (name),
                    INDEX idx_frequency (frequency)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS productivity_entries (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    date VARCHAR(50) NOT NULL UNIQUE,
                    productivity_score DECIMAL(5,2) NOT NULL,
                    tasks_completed INT DEFAULT 0,
                    tasks_total INT DEFAULT 0,
                    avg_mood_score DECIMAL(4,2),
                    focus_hours DECIMAL(5,2) DEFAULT 0,
                    notes TEXT,
                    created_at VARCHAR(100) NOT NULL,
                    updated_at VARCHAR(100) NOT NULL,
                    encrypted_data BLOB,
                    INDEX idx_date (date),
                    INDEX idx_productivity_score (productivity_score),
                    INDEX idx_avg_mood_score (avg_mood_score)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS task_completions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    task_id INT NOT NULL,
                    completed_at VARCHAR(100) NOT NULL,
                    duration_minutes DECIMAL(6,2),
                    focus_score INT,
                    notes TEXT,
                    created_at VARCHAR(100) NOT NULL,
                    INDEX idx_task_id (task_id),
                    INDEX idx_completed_at (completed_at),
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS focus_sessions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    started_at VARCHAR(100) NOT NULL,
                    ended_at VARCHAR(100),
                    duration_minutes DECIMAL(6,2),
                    task_id INT,
                    notes TEXT,
                    created_at VARCHAR(100) NOT NULL,
                    INDEX idx_started_at (started_at),
                    INDEX idx_task_id (task_id),
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
            
            self.connection.commit()
            cursor.close()
        except pymysql.Error as e:
            print(f"Error initializing database: {e}")
            self.connection.rollback()
            raise
    
    def execute(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results
        
        Args:
            query: SQL SELECT query (MySQL syntax)
            params: Query parameters
            
        Returns:
            List of dictionaries representing rows
        """
        # Convert SQLite syntax to MySQL if needed
        query = self._convert_query(query)
        # Convert ? placeholders to %s for MySQL
        query = query.replace('?', '%s')
        
        try:
            self._reconnect()
            cursor = self.connection.cursor()
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
                        decrypted_data = json.loads(decrypted)
                        row_dict.update(decrypted_data)
                    except Exception as e:
                        print(f"Warning: Could not decrypt data: {e}")
                # Remove encrypted_data field
                row_dict.pop('encrypted_data', None)
                results.append(row_dict)
            
            cursor.close()
            return results
        except pymysql.Error as e:
            print(f"Error executing query: {e}")
            raise
    
    def execute_write(self, query: str, params: tuple = ()) -> int:
        """
        Execute an INSERT/UPDATE/DELETE query
        
        Args:
            query: SQL write query (MySQL syntax)
            params: Query parameters
            
        Returns:
            Last inserted row ID (for INSERT) or affected rows count
        """
        # Convert SQLite syntax to MySQL if needed
        query = self._convert_query(query)
        # Convert ? placeholders to %s for MySQL
        query = query.replace('?', '%s')
        
        try:
            self._reconnect()
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            
            last_id = cursor.lastrowid
            affected = cursor.rowcount
            
            cursor.close()
            return last_id if last_id else affected
        except pymysql.Error as e:
            print(f"Error executing write query: {e}")
            self.connection.rollback()
            raise
    
    def _convert_query(self, query: str) -> str:
        """Convert SQLite syntax to MySQL syntax"""
        # Replace SQLite-specific syntax
        query = query.replace('INTEGER PRIMARY KEY AUTOINCREMENT', 'INT AUTO_INCREMENT PRIMARY KEY')
        query = query.replace('TEXT', 'TEXT')
        query = query.replace('REAL', 'DECIMAL(10,2)')
        query = query.replace('BLOB', 'BLOB')
        
        # Handle DATE() function - MySQL uses DATE() differently
        # For now, keep as is since we're using VARCHAR for dates
        
        return query
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None


# Global MySQL instance
_mysql_instance: Optional[MySQLDatabase] = None


def get_mysql_database(**kwargs) -> MySQLDatabase:
    """Get or create global MySQL database instance"""
    global _mysql_instance
    if _mysql_instance is None:
        _mysql_instance = MySQLDatabase(**kwargs)
    return _mysql_instance

