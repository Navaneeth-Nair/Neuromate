"""
Quick Text Command - Process a single text command
"""
import sys
from .text_input import process_text_input


def main():
    if len(sys.argv) < 2:
        print("Usage: python quick_text.py 'your command here' [--speak]")
        print("Example: python quick_text.py 'add task finish project'")
        print("Example: python quick_text.py 'show my tasks' --speak")
        sys.exit(1)
    
    # Check for --speak flag
    speak_response = '--speak' in sys.argv or '-s' in sys.argv
    # Remove flags from command
    command_parts = [arg for arg in sys.argv[1:] if arg not in ['--speak', '-s']]
    command = " ".join(command_parts)
    
    print(f"Command: {command}")
    if speak_response:
        print("(Speech enabled)")
    print()
    
    response = process_text_input(command, speak_response=speak_response)
    
    if response:
        print(f"Response: {response}")
    else:
        print("No response generated.")


if __name__ == "__main__":
    main()

