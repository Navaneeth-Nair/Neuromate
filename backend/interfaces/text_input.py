"""
Text Input Mode - Allows typing commands instead of voice input

This module can be executed directly (python backend/interfaces/text_input.py)
or as a package module (python -m backend.interfaces.text_input). When run
directly Python's import system doesn't automatically put the project root
on sys.path, so importing the `backend` package can raise
ModuleNotFoundError. To be robust we try the normal imports first and if
they fail we insert the project root into sys.path and retry.
"""
import sys
import pathlib

try:
    # Normal package import (works when running as a package)
    from backend.modules import command_handler
    from backend.modules import tts as speak
    from backend.modules.conversation_context import get_context
except ModuleNotFoundError:
    # Likely running the file directly; add project root to sys.path
    # File is at: <project_root>/backend/interfaces/text_input.py
    project_root = pathlib.Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(project_root))
    from backend.modules import command_handler
    from backend.modules import tts as speak
    from backend.modules.conversation_context import get_context


def process_text_input(text: str, speak_response: bool = True) -> str:
    """
    Process a text command
    
    Args:
        text: The text command to process
        speak_response: Whether to speak the response (default: True)
        
    Returns:
        Response text
    """
    if not text or not text.strip():
        return ""
    
    text = text.strip()
    
    # Save to client_question.txt for compatibility with ai_chat
    with open("data/client_question.txt", "w", encoding="utf-8") as f:
        f.write(text)
    
    # Handle command
    response_text = command_handler.handle_command(text)
    
    # Speak response if requested
    if speak_response and response_text:
        # Ensure response is written to file first
        try:
            with open("data/response.txt", 'w', encoding='utf-8') as f:
                f.write(response_text)
            print(f"[DEBUG] Response written to response.txt ({len(response_text)} chars)")
        except Exception as e:
            print(f"Warning: Could not write response to file: {e}")
        
        # Speak the response
        # IMPORTANT: Use block_keys=True to ensure TTS actually plays audio
        # We'll handle key unblocking after TTS completes
        print(f"[DEBUG] Calling TTS to speak response...")
        print(f"[DEBUG] Response text: '{response_text}'")
        try:
            # Verify TTS engine is ready (use the imported speak alias)
            engine = getattr(speak, "_tts_engine", None)
            if engine is None:
                raise RuntimeError("TTS engine not initialized (speak._tts_engine missing)")

            volume = engine.engine.getProperty("volume")
            rate = engine.engine.getProperty("rate")
            print(f"[DEBUG] TTS Engine - Volume: {volume}, Rate: {rate}")

            if volume == 0:
                print("[WARNING] TTS volume is 0! Setting to 1.0")
                engine.engine.setProperty("volume", 1.0)

            # Call TTS
            speak.speak(text=response_text, block_keys=True)
            print(f"[DEBUG] TTS call completed.")
        except Exception as e:
            print(f"[ERROR] Error calling TTS: {e}")
            import traceback
            traceback.print_exc()
        
        # CRITICAL: Force unblock keys multiple times after TTS completes
        # This is essential for text input mode to continue working
        import keyboard
        import time
        import sys
        try:
            # Multiple unblock attempts to ensure it works
            # Keyboard library can be finicky, so we try many times
            for attempt in range(10):
                try:
                    keyboard.unblock_key('enter')
                    keyboard.unblock_key('esc')
                except:
                    pass
                if attempt < 9:  # Don't sleep after last attempt
                    time.sleep(0.05)
            
            # Extra delay to ensure Windows processes the unblock
            time.sleep(0.5)
            
            # Flush stdout to ensure prompt is ready
            sys.stdout.flush()
            print(f"[DEBUG] Keys unblocked ({len(response_text)} chars spoken).")
        except Exception as e:
            print(f"[WARNING] Error unblocking keys: {e}")
            import traceback
            traceback.print_exc()
    
    return response_text


def text_mode(speak_responses: bool = True):
    """
    Interactive text input mode
    
    Args:
        speak_responses: Whether to speak responses (default: True)
    """
    print("\n" + "="*60)
    print("NEUROMATE - TEXT INPUT MODE")
    print("="*60)
    print("\nType your commands here. Type 'quit' or 'exit' to stop.")
    print("Type 'help' for available commands.\n")
    
    while True:
        try:
            # CRITICAL: Ensure ENTER key is unblocked before input()
            # This ensures input() can receive ENTER key presses
            import keyboard
            try:
                keyboard.unblock_key('enter')
                keyboard.unblock_key('esc')
            except:
                pass
            
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle exit commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break
            
            # Handle help
            if user_input.lower() == 'help':
                print_help()
                continue
            
            # Handle mode toggle
            if user_input.lower() == 'toggle speech':
                speak_responses = not speak_responses
                print(f"\nSpeech responses: {'ON' if speak_responses else 'OFF'}")
                continue
            
            # Process command
            print("\nProcessing...")
            response = process_text_input(user_input, speak_response=speak_responses)
            
            if response:
                print(f"\nTeto: {response}\n")
            else:
                print("\n(No response)\n")
            
            # CRITICAL: Ensure ENTER key is unblocked after processing
            # This allows the next input() call to work properly
            import keyboard
            import time
            try:
                keyboard.unblock_key('enter')
                keyboard.unblock_key('esc')
                time.sleep(0.1)  # Small delay to ensure unblock takes effect
            except:
                pass
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except EOFError:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")


def print_help():
    """Print help information"""
    help_text = """
Available Commands:

Task Management:
  - "add task [name]" - Create a new task
  - "show my tasks" - List all pending tasks
  - "complete task [name]" - Mark task as done
  - "delete task [name]" - Remove a task

Mood Tracking:
  - "I'm feeling [mood]" - Log your mood
  - "How am I feeling?" - Check today's mood

Planning:
  - "What's my plan for today?" - Get daily plan
  - "What should I do?" - Get daily plan
  - "Suggest tasks" - Get prioritized task list
  - "What should I focus on?" - Get recommendations

Utilities:
  - "repeat" - Repeat last response
  - "undo" - Undo last action
  - "toggle speech" - Turn speech on/off
  - "help" - Show this help
  - "quit" or "exit" - Exit text mode

You can also ask general questions - Teto will respond!
"""
    print(help_text)


if __name__ == "__main__":
    text_mode()

