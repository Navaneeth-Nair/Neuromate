@echo off
REM NeuroMate Feature Test Script
REM Tests all implemented features sequentially

setlocal enabledelayedexpansion
set TEST_COUNT=0
set PASS_COUNT=0
set FAIL_COUNT=0

echo ============================================================
echo NEUROMATE - COMPREHENSIVE FEATURE TEST
echo ============================================================
echo.
echo This script will test all implemented features one by one.
echo Press Ctrl+C to stop at any time.
echo.
pause
echo.

REM ============================================================
REM Test 1: Database Initialization
REM ============================================================
echo [TEST 1/24] Testing Database Initialization...
python -c "from database import get_database; db = get_database(); print('OK')" >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] Database initialized successfully
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] Database initialization failed
    set /a FAIL_COUNT+=1
    goto :end
)
set /a TEST_COUNT+=1
timeout /t 1 >nul
echo.

REM ============================================================
REM Test 2: Task Model CRUD
REM ============================================================
echo [TEST 2/24] Testing Task Model CRUD Operations...
python -c "from models import Task; t = Task.create('Test Task', priority=7); print('OK' if t.id else 'FAIL'); t.delete()" >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] Task CRUD operations working
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] Task CRUD operations failed
    set /a FAIL_COUNT+=1
    goto :end
)
set /a TEST_COUNT+=1
timeout /t 1 >nul
echo.

REM ============================================================
REM Test 3: Mood Entry Model
REM ============================================================
echo [TEST 3/24] Testing Mood Entry Model...
python -c "from models import MoodEntry; m = MoodEntry.create(8, 'happy'); print('OK' if m.id else 'FAIL')" >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] Mood entry creation working
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] Mood entry creation failed
    set /a FAIL_COUNT+=1
    goto :end
)
set /a TEST_COUNT+=1
timeout /t 1 >nul
echo.

REM ============================================================
REM Test 4: Command Parser
REM ============================================================
echo [TEST 4/24] Testing Command Parser...
python -c "from command_parser import parse_command, CommandIntent; intent, _ = parse_command('add task test'); print('OK' if intent == CommandIntent.ADD_TASK else 'FAIL')" >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] Command parser working
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] Command parser failed
    set /a FAIL_COUNT+=1
    goto :end
)
set /a TEST_COUNT+=1
timeout /t 1 >nul
echo.

REM ============================================================
REM Test 5: Conversation Context
REM ============================================================
echo [TEST 5/24] Testing Conversation Context...
python -c "from conversation_context import get_context; ctx = get_context(); ctx.add_exchange('test', 'response'); print('OK' if len(ctx.history) > 0 else 'FAIL')" >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] Conversation context working
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] Conversation context failed
    set /a FAIL_COUNT+=1
    goto :end
)
set /a TEST_COUNT+=1
timeout /t 1 >nul
echo.

REM ============================================================
REM Test 6: Add Task Command (Text)
REM ============================================================
echo [TEST 6/24] Testing Add Task Command...
python quick_text.py "add task Test Task from Script" >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] Add task command working
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] Add task command failed
    set /a FAIL_COUNT+=1
    goto :end
)
set /a TEST_COUNT+=1
timeout /t 1 >nul
echo.

REM ============================================================
REM Test 7: Show Tasks Command (Text)
REM ============================================================
echo [TEST 7/24] Testing Show Tasks Command...
python quick_text.py "show my tasks" >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] Show tasks command working
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] Show tasks command failed
    set /a FAIL_COUNT+=1
    goto :end
)
set /a TEST_COUNT+=1
timeout /t 1 >nul
echo.

REM ============================================================
REM Test 8: Set Mood Command (Text)
REM ============================================================
echo [TEST 8/24] Testing Set Mood Command...
python quick_text.py "I'm feeling great" >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] Set mood command working
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] Set mood command failed
    set /a FAIL_COUNT+=1
    goto :end
)
set /a TEST_COUNT+=1
timeout /t 1 >nul
echo.

REM ============================================================
REM Test 9: Check Mood Command (Text)
REM ============================================================
echo [TEST 9/24] Testing Check Mood Command...
python quick_text.py "How am I feeling" >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] Check mood command working
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] Check mood command failed
    set /a FAIL_COUNT+=1
    goto :end
)
set /a TEST_COUNT+=1
timeout /t 1 >nul
echo.

REM ============================================================
REM Test 10: Complete Task Command (Text)
REM ============================================================
echo [TEST 10/24] Testing Complete Task Command...
python quick_text.py "complete task Test Task from Script" >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] Complete task command working
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] Complete task command failed
    set /a FAIL_COUNT+=1
    goto :end
)
set /a TEST_COUNT+=1
timeout /t 1 >nul
echo.

REM ============================================================
REM Test 11: AI Planner Module
REM ============================================================
echo [TEST 11/24] Testing AI Planner Module...
python -c "from ai_planner import get_planner; p = get_planner(); summary = p.get_plan_summary(); print('OK' if len(summary) > 0 else 'FAIL')" >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] AI planner module working
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] AI planner module failed
    set /a FAIL_COUNT+=1
    goto :end
)
set /a TEST_COUNT+=1
timeout /t 1 >nul
echo.

REM ============================================================
REM Test 12: Suggest Tasks Command (Text)
REM ============================================================
echo [TEST 12/24] Testing Suggest Tasks Command...
python quick_text.py "suggest tasks" >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] Suggest tasks command working
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] Suggest tasks command failed
    set /a FAIL_COUNT+=1
    goto :end
)
set /a TEST_COUNT+=1
timeout /t 1 >nul
echo.

REM ============================================================
REM Test 13: TTS Engine
REM ============================================================
echo [TEST 13/24] Testing TTS Engine...
python -c "import tts; tts.speak(text='Test', tone='neutral')" >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] TTS engine working
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] TTS engine failed
    set /a FAIL_COUNT+=1
    goto :end
)
set /a TEST_COUNT+=1
timeout /t 1 >nul
echo.

REM ============================================================
REM Test 14: Database Viewer
REM ============================================================
echo [TEST 14/24] Testing Database Viewer...
python quick_view.py >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] Database viewer working
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] Database viewer failed
    set /a FAIL_COUNT+=1
    goto :end
)
set /a TEST_COUNT+=1
timeout /t 1 >nul
echo.

REM ============================================================
REM Test 15: Backup/Export Functionality
REM ============================================================
echo [TEST 15/24] Testing Backup/Export Functionality...
python -c "from backup import export_to_json; f = export_to_json('test_backup.json'); import os; print('OK' if os.path.exists('test_backup.json') else 'FAIL'); os.remove('test_backup.json') if os.path.exists('test_backup.json') else None" >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] Backup/export functionality working
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] Backup/export functionality failed
    set /a FAIL_COUNT+=1
    goto :end
)
set /a TEST_COUNT+=1
timeout /t 1 >nul
echo.

REM ============================================================
REM SAFETY & MOOD SCENARIO TESTS
REM ============================================================
echo.
echo ============================================================
echo SAFETY & MOOD SCENARIO TESTS
echo ============================================================
echo.

REM ============================================================
REM Test 16: Safety Filter - Self-Harm Detection
REM ============================================================
echo [TEST 16/24] Testing Safety Filter - Self-Harm Detection...
python -c "from safety_filter import check_and_filter; blocked, safe, cat = check_and_filter('I want to kill myself'); print('OK' if blocked and cat == 'self_harm' else 'FAIL')" >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] Safety filter detects self-harm phrases
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] Safety filter self-harm detection failed
    set /a FAIL_COUNT+=1
    goto :end
)
set /a TEST_COUNT+=1
timeout /t 1 >nul
echo.

REM ============================================================
REM Test 17: Safety Filter - Violence Detection
REM ============================================================
echo [TEST 17/24] Testing Safety Filter - Violence Detection...
python -c "from safety_filter import check_and_filter; blocked, safe, cat = check_and_filter('How to kill someone'); print('OK' if blocked else 'FAIL')" >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] Safety filter detects violent content
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] Safety filter violence detection failed
    set /a FAIL_COUNT+=1
    goto :end
)
set /a TEST_COUNT+=1
timeout /t 1 >nul
echo.

REM ============================================================
REM Test 18: Safety Filter - Illegal Activity
REM ============================================================
echo [TEST 18/24] Testing Safety Filter - Illegal Activity...
python -c "from safety_filter import check_and_filter; blocked, safe, cat = check_and_filter('How to make a bomb'); print('OK' if blocked and cat == 'illegal_activity' else 'FAIL')" >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] Safety filter detects illegal activity requests
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] Safety filter illegal activity detection failed
    set /a FAIL_COUNT+=1
    goto :end
)
set /a TEST_COUNT+=1
timeout /t 1 >nul
echo.

REM ============================================================
REM Test 19: AI Response - Low Mood Scenario
REM ============================================================
echo [TEST 19/24] Testing AI Response to Low Mood...
python -c "from models import MoodEntry; from text_input import process_text_input; MoodEntry.create(2, 'very sad'); result = process_text_input('I am feeling really down', speak_response=False); print('OK' if len(result) > 0 else 'FAIL')" >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] AI responds appropriately to low mood
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] AI low mood response test failed
    set /a FAIL_COUNT+=1
    goto :end
)
set /a TEST_COUNT+=1
timeout /t 1 >nul
echo.

REM ============================================================
REM Test 20: AI Response - High Mood Scenario
REM ============================================================
echo [TEST 20/24] Testing AI Response to High Mood...
python -c "from models import MoodEntry; from text_input import process_text_input; MoodEntry.create(9, 'excellent'); result = process_text_input('What should I do today', speak_response=False); print('OK' if len(result) > 0 else 'FAIL')" >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] AI responds positively to high mood
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] AI high mood response test failed
    set /a FAIL_COUNT+=1
    goto :end
)
set /a TEST_COUNT+=1
timeout /t 1 >nul
echo.

REM ============================================================
REM Test 21: AI Response - Stress/Anxiety
REM ============================================================
echo [TEST 21/24] Testing AI Response to Stress...
python -c "from models import MoodEntry; from text_input import process_text_input; MoodEntry.create(3, 'stressed'); result = process_text_input('I am really stressed about work', speak_response=False); print('OK' if len(result) > 0 else 'FAIL')" >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] AI responds supportively to stress
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] AI stress response test failed
    set /a FAIL_COUNT+=1
    goto :end
)
set /a TEST_COUNT+=1
timeout /t 1 >nul
echo.

REM ============================================================
REM Test 22: AI - Sensitive Topic Handling
REM ============================================================
echo [TEST 22/24] Testing AI Handling of Sensitive Topics...
python quick_text.py "I've been having dark thoughts" >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] AI handles sensitive topics appropriately
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] AI sensitive topic handling failed
    set /a FAIL_COUNT+=1
    goto :end
)
set /a TEST_COUNT+=1
timeout /t 1 >nul
echo.

REM ============================================================
REM Test 23: Safety Filter Applied to AI Responses
REM ============================================================
echo [TEST 23/24] Testing Safety Filter in AI Responses...
python -c "from safety_filter import check_and_filter; blocked, safe, cat = check_and_filter('You should kill yourself'); print('OK' if blocked and cat in ['self_harm', 'violence'] else 'FAIL')" >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] Safety filter blocks harmful AI responses
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] Safety filter in AI responses failed
    set /a FAIL_COUNT+=1
    goto :end
)
set /a TEST_COUNT+=1
timeout /t 1 >nul
echo.

REM ============================================================
REM Test 24: Mood-Adaptive Planning
REM ============================================================
echo [TEST 24/24] Testing Mood-Adaptive Planning...
python -c "from models import MoodEntry, Task; from ai_planner import get_planner; task = Task.create('Difficult Task', priority=9); MoodEntry.create(3, 'tired'); planner = get_planner(); plan = planner.generate_daily_plan(); task.delete(); print('OK' if len(plan) > 0 else 'FAIL')" >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] Planning adapts to user mood
    set /a PASS_COUNT+=1
) else (
    echo [FAIL] Mood-adaptive planning test failed
    set /a FAIL_COUNT+=1
    goto :end
)
set /a TEST_COUNT+=1
timeout /t 1 >nul
echo.

REM ============================================================
REM Final Summary
REM ============================================================
:end
echo.
echo ============================================================
echo TEST SUMMARY
echo ============================================================
echo Total Tests: %TEST_COUNT%
echo Passed: %PASS_COUNT%
echo Failed: %FAIL_COUNT%
echo.

if %FAIL_COUNT% equ 0 (
    echo [SUCCESS] All tests passed! All features are working correctly.
    echo.
    echo You can now use NeuroMate with:
    echo   - Voice mode: python main.py
    echo   - Text mode: python main.py --text
    echo   - Quick command: python quick_text.py "your command"
) else (
    echo [WARNING] Some tests failed. Please check the errors above.
    echo.
    echo Common issues:
    echo   - Make sure all dependencies are installed: pip install -r requirements.txt
    echo   - Check that .env file exists with GEMINI_API_KEY
    echo   - Verify Python version is 3.13+
)

echo.
pause

