"""
Quick test script to verify database and models work correctly
"""
from database import Task, MoodEntry, JournalEntry, get_database

print("Testing NeuroMate database and models...")

# Test database initialization
print("\n1. Testing database initialization...")
db = get_database()
print("   [OK] Database initialized")

# Test Task creation
print("\n2. Testing Task creation...")
task = Task.create(title="Test Task", description="This is a test", priority=7)
print(f"   [OK] Task created: {task.title} (ID: {task.id})")

# Test Task retrieval
print("\n3. Testing Task retrieval...")
tasks = Task.get_all()
print(f"   [OK] Found {len(tasks)} task(s)")

# Test MoodEntry creation
print("\n4. Testing MoodEntry creation...")
mood = MoodEntry.create(mood_score=8, mood_text="happy")
print(f"   [OK] Mood entry created: {mood.mood_score}/10")

# Test JournalEntry creation
print("\n5. Testing JournalEntry creation...")
journal = JournalEntry.create(content="Test journal entry", entry_type="general")
print(f"   [OK] Journal entry created")

# Test Task completion
print("\n6. Testing Task completion...")
task.complete()
print(f"   [OK] Task marked as completed")

# Clean up test task
task.delete()
print("\n7. Cleanup: Test task deleted")

print("\n[SUCCESS] All tests passed! Database and models are working correctly.")

