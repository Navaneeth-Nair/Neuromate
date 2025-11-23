"""
Migration Script: SQLite to MySQL
Migrates all data from SQLite database to MySQL database
"""
import sqlite3
import os
from dotenv import load_dotenv
from .mysql_client import MySQLDatabase
from datetime import datetime

load_dotenv()


def migrate_sqlite_to_mysql(sqlite_path: str = "data/neuromate.db"):
    """
    Migrate data from SQLite to MySQL
    
    Args:
        sqlite_path: Path to SQLite database file
    """
    print("="*60)
    print("SQLite to MySQL Migration")
    print("="*60)
    
    # Check if SQLite database exists
    if not os.path.exists(sqlite_path):
        print(f"Error: SQLite database not found at {sqlite_path}")
        return False
    
    # Connect to SQLite
    print(f"\n1. Connecting to SQLite database: {sqlite_path}")
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    
    # Connect to MySQL
    print("2. Connecting to MySQL database...")
    try:
        mysql_db = MySQLDatabase()
        print("   ✓ MySQL connection established")
    except Exception as e:
        print(f"   ✗ Failed to connect to MySQL: {e}")
        print("\nPlease ensure:")
        print("  - MySQL server is running")
        print("  - Database credentials are set in .env file:")
        print("    MYSQL_HOST=localhost")
        print("    MYSQL_PORT=3306")
        print("    MYSQL_USER=your_user")
        print("    MYSQL_PASSWORD=your_password")
        print("    MYSQL_DATABASE=neuromate")
        sqlite_conn.close()
        return False
    
    # Tables to migrate
    tables = [
        'tasks',
        'mood_entries',
        'journal_entries',
        'habits',
        'productivity_entries'
    ]
    
    total_migrated = 0
    
    for table in tables:
        print(f"\n3. Migrating table: {table}")
        
        # Get all rows from SQLite
        sqlite_cursor.execute(f"SELECT * FROM {table}")
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            print(f"   No data to migrate")
            continue
        
        print(f"   Found {len(rows)} rows")
        
        # Get column names
        columns = [description[0] for description in sqlite_cursor.description]
        
        # Migrate each row
        migrated = 0
        for row in rows:
            try:
                # Convert row to dictionary
                row_dict = dict(row)
                
                # Build INSERT query
                placeholders = ', '.join(['%s'] * len(columns))
                columns_str = ', '.join(columns)
                
                # Handle AUTO_INCREMENT - exclude id for MySQL to auto-generate
                if 'id' in columns:
                    columns_str = ', '.join([c for c in columns if c != 'id'])
                    placeholders = ', '.join(['%s'] * (len(columns) - 1))
                    values = tuple(row_dict[c] for c in columns if c != 'id')
                else:
                    values = tuple(row_dict[c] for c in columns)
                
                query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
                
                # Execute insert
                mysql_db.execute_write(query, values)
                migrated += 1
                
            except Exception as e:
                print(f"   Warning: Failed to migrate row: {e}")
                continue
        
        print(f"   ✓ Migrated {migrated}/{len(rows)} rows")
        total_migrated += migrated
    
    # Close connections
    sqlite_conn.close()
    mysql_db.close()
    
    print("\n" + "="*60)
    print(f"Migration Complete!")
    print(f"Total rows migrated: {total_migrated}")
    print("="*60)
    
    return True


def verify_migration():
    """Verify migration by comparing row counts"""
    print("\n" + "="*60)
    print("Verifying Migration")
    print("="*60)
    
    # Connect to both databases
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_cursor = sqlite_conn.cursor()
    
    try:
        mysql_db = MySQLDatabase()
    except Exception as e:
        print(f"Failed to connect to MySQL: {e}")
        sqlite_conn.close()
        return
    
    tables = ['tasks', 'mood_entries', 'journal_entries', 'habits', 'productivity_entries']
    
    print("\nTable Row Counts:")
    print(f"{'Table':<25} {'SQLite':<10} {'MySQL':<10} {'Match':<10}")
    print("-" * 60)
    
    all_match = True
    for table in tables:
        # SQLite count
        sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
        sqlite_count = sqlite_cursor.fetchone()[0]
        
        # MySQL count
        mysql_result = mysql_db.execute(f"SELECT COUNT(*) as count FROM {table}")
        mysql_count = mysql_result[0]['count'] if mysql_result else 0
        
        match = "✓" if sqlite_count == mysql_count else "✗"
        if sqlite_count != mysql_count:
            all_match = False
        
        print(f"{table:<25} {sqlite_count:<10} {mysql_count:<10} {match:<10}")
    
    sqlite_conn.close()
    mysql_db.close()
    
    print("\n" + "="*60)
    if all_match:
        print("✓ All tables migrated successfully!")
    else:
        print("✗ Some tables have mismatched row counts")
    print("="*60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        verify_migration()
    else:
        print("\nThis script will migrate all data from SQLite to MySQL.")
        print("Make sure MySQL is running and configured in .env file.")
        print("\nPress Enter to continue or Ctrl+C to cancel...")
        try:
            input()
        except KeyboardInterrupt:
            print("\nMigration cancelled.")
            sys.exit(0)
        
        success = migrate_sqlite_to_mysql()
        
        if success:
            print("\nRun with --verify flag to verify migration:")
            print("  python migrate_to_mysql.py --verify")

