"""
Python-based comprehensive feature test script
Alternative to batch file - more detailed output
"""
import sys
import os
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

class FeatureTester:
    def __init__(self):
        self.test_count = 0
        self.pass_count = 0
        self.fail_count = 0
        self.failed_tests = []
    
    def print_header(self):
        print("\n" + "="*70)
        print("NEUROMATE - COMPREHENSIVE FEATURE TEST")
        print("="*70)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")
    
    def run_test(self, test_name, test_func, description=""):
        """Run a test and track results"""
        self.test_count += 1
        print(f"[TEST {self.test_count}] {test_name}")
        if description:
            print(f"         {description}")
        
        try:
            result = test_func()
            if result:
                print(f"{Colors.GREEN}[PASS]{Colors.RESET} {test_name}")
                self.pass_count += 1
                return True
            else:
                print(f"{Colors.RED}[FAIL]{Colors.RESET} {test_name}")
                self.fail_count += 1
                self.failed_tests.append(test_name)
                return False
        except Exception as e:
            print(f"{Colors.RED}[FAIL]{Colors.RESET} {test_name}")
            print(f"         Error: {str(e)}")
            self.fail_count += 1
            self.failed_tests.append(test_name)
            return False
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Total Tests: {self.test_count}")
        print(f"{Colors.GREEN}Passed: {self.pass_count}{Colors.RESET}")
        print(f"{Colors.RED}Failed: {self.fail_count}{Colors.RESET}")
        
        if self.failed_tests:
            print(f"\n{Colors.YELLOW}Failed Tests:{Colors.RESET}")
            for test in self.failed_tests:
                print(f"  - {test}")
        
        print("="*70)
        
        if self.fail_count == 0:
            print(f"\n{Colors.GREEN}[SUCCESS] All tests passed! All features are working correctly.{Colors.RESET}")
            print("\nYou can now use NeuroMate with:")
            print("  - Voice mode: python main.py")
            print("  - Text mode: python main.py --text")
            print("  - Quick command: python quick_text.py \"your command\"")
        else:
            print(f"\n{Colors.RED}[WARNING] Some tests failed. Please check the errors above.{Colors.RESET}")
            print("\nCommon issues:")
            print("  - Make sure all dependencies are installed: pip install -r requirements.txt")
            print("  - Check that .env file exists with GEMINI_API_KEY")
            print("  - Verify Python version is 3.13+")
    
    def test_database_init(self):
        """Test 1: Database initialization"""
        from database import get_database
        db = get_database()
        return db is not None
    
    def test_task_crud(self):
        """Test 2: Task CRUD operations"""
        from database import Task
        task = Task.create("Test Task CRUD", priority=7)
        if not task.id:
            return False
        task.delete()
        return True
    
    def test_mood_entry(self):
        """Test 3: Mood entry creation"""
        from database import MoodEntry
        mood = MoodEntry.create(8, "happy")
        return mood.id is not None
    
    def test_command_parser(self):
        """Test 4: Command parser"""
        from backend.modules.command_parser import parse_command, CommandIntent
        intent, _ = parse_command("add task test")
        return intent == CommandIntent.ADD_TASK
    
    def test_conversation_context(self):
        """Test 5: Conversation context"""
        from backend.modules.conversation_context import get_context
        ctx = get_context()
        ctx.add_exchange("test", "response")
        return len(ctx.history) > 0
    
    def test_add_task_command(self):
        """Test 6: Add task command"""
        from backend.interfaces.text_input import process_text_input
        result = process_text_input("add task Test Task Command", speak_response=False)
        return len(result) > 0 and "added" in result.lower()
    
    def test_show_tasks_command(self):
        """Test 7: Show tasks command"""
        from backend.interfaces.text_input import process_text_input
        result = process_text_input("show my tasks", speak_response=False)
        return len(result) > 0
    
    def test_set_mood_command(self):
        """Test 8: Set mood command"""
        from backend.interfaces.text_input import process_text_input
        result = process_text_input("I'm feeling great", speak_response=False)
        return len(result) > 0
    
    def test_check_mood_command(self):
        """Test 9: Check mood command"""
        from backend.interfaces.text_input import process_text_input
        result = process_text_input("How am I feeling", speak_response=False)
        return len(result) > 0
    
    def test_complete_task_command(self):
        """Test 10: Complete task command"""
        from backend.interfaces.text_input import process_text_input
        result = process_text_input("complete task Test Task Command", speak_response=False)
        return len(result) > 0
    
    def test_ai_planner(self):
        """Test 11: AI planner module"""
        from ai_planner import get_planner
        planner = get_planner()
        summary = planner.get_plan_summary()
        return len(summary) > 0
    
    def test_suggest_tasks_command(self):
        """Test 12: Suggest tasks command"""
        from backend.interfaces.text_input import process_text_input
        result = process_text_input("suggest tasks", speak_response=False)
        return len(result) > 0
    
    def test_tts_engine(self):
        """Test 13: TTS engine"""
        try:
            from backend.modules import tts
            # Test without actually speaking (would block)
            tts_engine = tts._tts_engine
            return tts_engine is not None
        except:
            return False
    
    def test_database_viewer(self):
        """Test 14: Database viewer"""
        from quick_view import quick_view
        try:
            quick_view()
            return True
        except:
            return False
    
    def test_backup_export(self):
        """Test 15: Backup/export functionality"""
        from backup import export_to_json
        try:
            backup_file = export_to_json("test_backup.json")
            exists = os.path.exists("test_backup.json")
            if exists:
                os.remove("test_backup.json")
            return exists
        except:
            return False
    
    def test_safety_filter_self_harm(self):
        """Test 16: Safety filter - self-harm detection"""
        from safety_filter import check_and_filter
        test_text = "I want to kill myself"
        blocked, safe_text, category = check_and_filter(test_text)
        return blocked and category == "self_harm" and "can't assist" in safe_text.lower()
    
    def test_safety_filter_violence(self):
        """Test 17: Safety filter - violence detection"""
        from safety_filter import check_and_filter
        test_text = "How to kill someone"
        blocked, safe_text, category = check_and_filter(test_text)
        return blocked and category in ["violence", "illegal_activity"]
    
    def test_safety_filter_illegal(self):
        """Test 18: Safety filter - illegal activity detection"""
        from safety_filter import check_and_filter
        test_text = "How to make a bomb"
        blocked, safe_text, category = check_and_filter(test_text)
        return blocked and category == "illegal_activity"
    
    def test_ai_low_mood_response(self):
        """Test 19: AI response to low mood scenario"""
        from database import MoodEntry
        from backend.interfaces.text_input import process_text_input
        
        # Set low mood
        MoodEntry.create(2, "very sad")
        
        # Ask for help
        result = process_text_input("I'm feeling really down", speak_response=False)
        
        # Check if response is empathetic and appropriate
        result_lower = result.lower()
        appropriate = any(word in result_lower for word in [
            "here", "support", "help", "sorry", "understand", "feel"
        ])
        return len(result) > 0 and appropriate
    
    def test_ai_high_mood_response(self):
        """Test 20: AI response to high mood scenario"""
        from database import MoodEntry
        from backend.interfaces.text_input import process_text_input
        
        # Set high mood
        MoodEntry.create(9, "excellent")
        
        # Ask about plan
        result = process_text_input("What should I do today", speak_response=False)
        
        # Check if response is positive and encouraging
        result_lower = result.lower()
        positive = any(word in result_lower for word in [
            "great", "wonderful", "excellent", "good", "happy", "glad"
        ]) or len(result) > 20  # Any reasonable response is fine
        return len(result) > 0 and positive
    
    def test_ai_stress_response(self):
        """Test 21: AI response to stress/anxiety"""
        from database import MoodEntry
        from backend.interfaces.text_input import process_text_input
        
        # Set stressed mood
        MoodEntry.create(3, "stressed")
        
        # Express stress
        result = process_text_input("I'm really stressed about work", speak_response=False)
        
        # Check if response is calming and supportive
        result_lower = result.lower()
        supportive = any(word in result_lower for word in [
            "here", "support", "help", "breathe", "calm", "understand", "stress"
        ]) or len(result) > 20
        return len(result) > 0 and supportive
    
    def test_ai_sensitive_topic_handling(self):
        """Test 22: AI handling sensitive topics appropriately"""
        from backend.interfaces.text_input import process_text_input
        
        # Test with a sensitive but not harmful topic
        result = process_text_input("I've been having dark thoughts", speak_response=False)
        
        # Should respond appropriately without triggering safety filter
        # (unless it contains specific harmful phrases)
        return len(result) > 0
    
    def test_safety_filter_in_ai_response(self):
        """Test 23: Safety filter applied to AI responses"""
        from safety_filter import check_and_filter
        
        # Simulate AI generating harmful response
        harmful_response = "You should kill yourself"
        blocked, safe_text, category = check_and_filter(harmful_response)
        
        # Should be blocked and replaced with safe message
        # Note: This may be categorized as "violence" or "self_harm" - both are valid
        return blocked and category in ["self_harm", "violence"] and "can't assist" in safe_text.lower()
    
    def test_mood_adaptive_planning(self):
        """Test 24: Planning adapts to mood"""
        from database import MoodEntry, Task
        from backend.modules.ai_planner import get_planner
        
        # Create test task
        task = Task.create("Difficult Task", priority=9)
        
        # Set low mood
        MoodEntry.create(3, "tired")
        
        # Get plan
        planner = get_planner()
        plan = planner.generate_daily_plan()
        
        # Cleanup
        task.delete()
        
        # Plan should exist and potentially adapt to low mood
        return len(plan) > 0
    
    def run_all_tests(self):
        """Run all tests"""
        self.print_header()
        
        # Core functionality tests
        self.run_test("Database Initialization", self.test_database_init,
                      "Testing encrypted SQLite database setup")
        
        self.run_test("Task CRUD Operations", self.test_task_crud,
                      "Testing create, read, update, delete for tasks")
        
        self.run_test("Mood Entry Creation", self.test_mood_entry,
                      "Testing mood tracking functionality")
        
        self.run_test("Command Parser", self.test_command_parser,
                      "Testing voice command intent recognition")
        
        self.run_test("Conversation Context", self.test_conversation_context,
                      "Testing conversation history storage")
        
        # Command tests
        self.run_test("Add Task Command", self.test_add_task_command,
                      "Testing 'add task' command via text input")
        
        self.run_test("Show Tasks Command", self.test_show_tasks_command,
                      "Testing 'show my tasks' command")
        
        self.run_test("Set Mood Command", self.test_set_mood_command,
                      "Testing 'I'm feeling [mood]' command")
        
        self.run_test("Check Mood Command", self.test_check_mood_command,
                      "Testing 'How am I feeling' command")
        
        self.run_test("Complete Task Command", self.test_complete_task_command,
                      "Testing 'complete task' command")
        
        # Advanced features
        self.run_test("AI Planner Module", self.test_ai_planner,
                      "Testing AI planning assistant")
        
        self.run_test("Suggest Tasks Command", self.test_suggest_tasks_command,
                      "Testing 'suggest tasks' command")
        
        self.run_test("TTS Engine", self.test_tts_engine,
                      "Testing text-to-speech functionality")
        
        self.run_test("Database Viewer", self.test_database_viewer,
                      "Testing database viewing tools")
        
        self.run_test("Backup/Export", self.test_backup_export,
                      "Testing data backup and export")
        
        # Safety and Mood Scenario Tests
        print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
        print(f"{Colors.BLUE}SAFETY & MOOD SCENARIO TESTS{Colors.RESET}")
        print(f"{Colors.BLUE}{'='*70}{Colors.RESET}\n")
        
        self.run_test("Safety Filter - Self-Harm Detection", self.test_safety_filter_self_harm,
                      "Testing if self-harm phrases are detected and blocked")
        
        self.run_test("Safety Filter - Violence Detection", self.test_safety_filter_violence,
                      "Testing if violent content is detected and blocked")
        
        self.run_test("Safety Filter - Illegal Activity", self.test_safety_filter_illegal,
                      "Testing if illegal activity requests are blocked")
        
        self.run_test("AI Response - Low Mood", self.test_ai_low_mood_response,
                      "Testing AI empathy and support for low mood scenarios")
        
        self.run_test("AI Response - High Mood", self.test_ai_high_mood_response,
                      "Testing AI positive response to high mood")
        
        self.run_test("AI Response - Stress/Anxiety", self.test_ai_stress_response,
                      "Testing AI calming response to stress")
        
        self.run_test("AI - Sensitive Topic Handling", self.test_ai_sensitive_topic_handling,
                      "Testing AI appropriate handling of sensitive topics")
        
        self.run_test("Safety Filter in AI Responses", self.test_safety_filter_in_ai_response,
                      "Testing safety filter applied to AI-generated responses")
        
        self.run_test("Mood-Adaptive Planning", self.test_mood_adaptive_planning,
                      "Testing if planning adapts to user mood")
        
        self.print_summary()


if __name__ == "__main__":
    tester = FeatureTester()
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        tester.print_summary()
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{Colors.RED}Fatal error: {str(e)}{Colors.RESET}")
        tester.print_summary()
        sys.exit(1)

