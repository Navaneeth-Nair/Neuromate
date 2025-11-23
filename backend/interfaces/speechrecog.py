#!/usr/bin/env python3
import speech_recognition as sr
import keyboard
import pyaudio
import wave
import tempfile
import os
from backend.modules import command_handler
from backend.modules import tts as speak

def record_while_key_held(filename="temp.wav", key="enter", rate=16000, chunk=1024):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk)

    frames = []
    print(f"\nHold '{key.upper()}' to record...")

    
    keyboard.wait(key)
    print("Recording... Release key to stop.")

    
    while keyboard.is_pressed(key):
        data = stream.read(chunk, exception_on_overflow=False)
        frames.append(data)

    print("Recording stopped.")
    stream.stop_stream()
    stream.close()
    p.terminate()

    
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
    return filename


def transcribe_audio(filename):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)
        print("\nYou said:", text)
        with open("data/client_question.txt", "w", encoding="utf-8") as f:
            f.write(text.strip())
        return text.strip()
    except sr.UnknownValueError:
        print(" Sorry, I couldn't understand what you said.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return None


def main():
    print(">>>Hold ENTER to record, release to stop. Press ESC to quit.\n")

    while True:
        if keyboard.is_pressed('esc'):
            print("Exiting...")
            break

        # Check if ENTER is pressed (user wants to record)
        if keyboard.is_pressed('enter'):
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                filename = tmp.name

            
            record_while_key_held(filename)
            text = transcribe_audio(filename)

            
            if os.path.exists(filename):
                os.unlink(filename)

            
            if text:
                # Handle command and get response
                # Note: Some commands (like get_plan) handle TTS internally
                print(f"\nProcessing command: {text}")
                response_text = command_handler.handle_command(text)
                
                # Always print response to console
                if response_text:
                    print(f"\nTeto: {response_text}\n")
                else:
                    print("\nNo response generated.\n")
                
                # If response wasn't spoken yet, speak it now
                # (Commands that handle their own TTS will have already spoken)
                if response_text:
                    # ALWAYS write response to file FIRST - this ensures it's saved
                    try:
                        with open("data/response.txt", 'w', encoding='utf-8') as f:
                            f.write(response_text)
                        print(f"[DEBUG] Response written to response.txt ({len(response_text)} chars)")
                        
                        # Verify it was written correctly
                        with open("data/response.txt", 'r', encoding='utf-8') as f:
                            verify_text = f.read()
                            if verify_text.strip() != response_text.strip():
                                print(f"[WARNING] Written text doesn't match! Expected {len(response_text)}, got {len(verify_text)}")
                            else:
                                print(f"[DEBUG] Verified: response.txt contains {len(verify_text)} chars")
                    except Exception as e:
                        print(f"[ERROR] Error writing response.txt: {e}")
                        import traceback
                        traceback.print_exc()
                    
                    # Speak the response - try reading from file first, then fallback to direct text
                    print("[DEBUG] Calling TTS to speak response...")
                    try:
                        # First try: read from file (ensures we have the saved version)
                        try:
                            with open("data/response.txt", 'r', encoding='utf-8') as f:
                                file_text = f.read().strip()
                            if file_text and file_text == response_text.strip():
                                print(f"[DEBUG] Reading from response.txt ({len(file_text)} chars)...")
                                speak.speak(text=file_text)
                            else:
                                print(f"[DEBUG] File content differs, using direct text...")
                                speak.speak(text=response_text)
                        except FileNotFoundError:
                            print("[DEBUG] response.txt not found, using direct text...")
                            speak.speak(text=response_text)
                        except Exception as read_error:
                            print(f"[DEBUG] Error reading file: {read_error}, using direct text...")
                            speak.speak(text=response_text)
                        
                        print("[DEBUG] TTS call completed successfully.")
                    except Exception as e:
                        print(f"[ERROR] Error calling TTS: {e}")
                        import traceback
                        traceback.print_exc()
                        # Final fallback: try reading from file again
                        try:
                            print("[DEBUG] Final fallback: reading from response.txt...")
                            with open("data/response.txt", 'r', encoding='utf-8') as f:
                                file_text = f.read().strip()
                            if file_text:
                                print(f"[DEBUG] Fallback: Found {len(file_text)} chars in file, speaking...")
                                speak.speak(text=file_text)
                            else:
                                print("[ERROR] Fallback: response.txt is empty")
                        except Exception as e2:
                            print(f"[ERROR] Fallback also failed: {e2}")
                            import traceback
                            traceback.print_exc()
                    
                    # Ensure keys are unblocked and wait a moment for state to reset
                    import time
                    try:
                        keyboard.unblock_key('enter')
                        keyboard.unblock_key('esc')
                    except:
                        pass
                    
                    # Wait for ENTER key to be released before accepting new input
                    # This prevents immediate re-triggering
                    print("\n>>> Ready for next input. Hold ENTER to record, release to stop. Press ESC to quit.\n")
                    
                    # Wait for ENTER to be released, then wait for next press
                    try:
                        # Wait for key to be released
                        while keyboard.is_pressed('enter'):
                            time.sleep(0.05)
                        # Small delay after release
                        time.sleep(0.2)
                    except:
                        pass 

if __name__ == "__main__":
    main()
