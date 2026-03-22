#!/usr/bin/env python3
import socket
import struct
import dotenv
import os
import json
import sys
import warnings

try:
    import pyaudio
    import vosk
except ImportError:
    pass

try:
    import speech_recognition as sr
except ImportError:
    pass

dotenv.load_dotenv()

# Initialize Vosk for offline STT
_vosk_model = None

def init_vosk():
    """Initialize Vosk model for offline speech recognition."""
    global _vosk_model
    try:
        if vosk.SetLogLevel(-1) is not None:
            pass  # Suppress Vosk logging
        
        # Check if model exists
        model_path = "model"
        if not os.path.exists(model_path):
            print("📥 Vosk model not found. Downloading...")
            print("   Visit: https://alphacephei.com/vosk/models")
            print("   Download a model and extract to ./model directory")
            return False
        
        _vosk_model = vosk.Model(model_path)
        print("✅ Offline STT (Vosk) initialized")
        return True
    except Exception as e:
        print(f"⚠️  Vosk offline STT unavailable: {e}")
        return False

def get_speech_offline():
    """Capture speech using Vosk offline engine."""
    try:
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4096)
        stream.start_stream()
        
        rec = vosk.KaldiRecognizer(_vosk_model, 16000)
        rec.SetWords(json.dumps(["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]))
        
        print("🎤 Listening (offline)...")
        partial_result = ""
        
        while True:
            data = stream.read(4096, exception_on_overflow=False)
            if len(data) == 0:
                break
            
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                if 'result' in result:
                    text = ' '.join([r['conf'] if 'conf' in r else r['result'] for r in result.get('result', []) if r.get('conf', 1.0) > 0.5])
                    stream.stop_stream()
                    stream.close()
                    p.terminate()
                    return text if text else result.get('result', [''])[0] if result.get('result') else ""
            else:
                partial = json.loads(rec.PartialResult())
                if 'partial' in partial:
                    print(f"  > {partial['partial']}")
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        return ""
        
    except Exception as e:
        print(f"❌ Offline STT error: {e}")
        return None

def get_speech_online():
    """Fallback to online speech recognition."""
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("🎤 Listening (online)...")
            audio = recognizer.listen(source, timeout=10)
        
        try:
            text = recognizer.recognize_google(audio)
            print(f"  > {text}")
            return text
        except sr.UnknownValueError:
            print("❌ Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"❌ Online STT error: {e}")
            return None
            
    except Exception as e:
        print(f"❌ Online STT error: {e}")
        return None

def get_speech_input():
    """Get speech input, trying offline first, then online fallback."""
    if _vosk_model:
        text = get_speech_offline()
        if text:
            return text
        print("Falling back to online STT...")
    
    # Fallback to online
    try:
        import speech_recognition
        return get_speech_online()
    except ImportError:
        print("❌ speech_recognition not installed for online fallback")
        return None

def send_question(question, host='100.86.220.9', port=11434):
    """Send question to server and receive answer."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, port))
        
        # Send question length and data
        question_bytes = question.encode('utf-8')
        client_socket.sendall(struct.pack('I', len(question_bytes)))
        client_socket.sendall(question_bytes)
        
        # Receive answer length
        length_data = client_socket.recv(4)
        if not length_data:
            return None
        length = struct.unpack('I', length_data)[0]
        
        # Receive answer
        answer_bytes = b''
        while len(answer_bytes) < length:
            chunk = client_socket.recv(min(4096, length - len(answer_bytes)))
            if not chunk:
                break
            answer_bytes += chunk
        
        answer = answer_bytes.decode('utf-8')
        return answer
        
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        client_socket.close()

def main():
    """Main client loop."""
    print("=" * 50)
    print("Monika Client - Speech & Text Interface")
    print("=" * 50)
    
    # Try to initialize offline STT
    offline_available = init_vosk()
    
    print("\nCommands:")
    print("  'quit'    - Exit")
    print("  'voice'   - Use voice input (STT)")
    print("  'text'    - Use text input")
    print("  'help'    - Show this help\n")
    
    input_mode = "text"
    
    while True:
        try:
            # Determine input based on mode
            if input_mode == "text":
                user_input = input("You: ").strip()
            else:
                user_input = get_speech_input()
                if user_input is None:
                    print("Failed to capture speech. Switching to text mode.")
                    input_mode = "text"
                    continue
                print(f"You: {user_input}")
            
            # Handle commands
            if user_input.lower() == 'quit':
                print("Goodbye!")
                break
            elif user_input.lower() == 'help':
                print("\nCommands:")
                print("  'quit'    - Exit")
                print("  'voice'   - Use voice input")
                print("  'text'    - Use text input")
                print("  'help'    - Show this help\n")
                continue
            elif user_input.lower() == 'voice':
                if offline_available or sr:
                    input_mode = "voice"
                    print("✅ Switched to voice input")
                else:
                    print("❌ Voice not available (install vosk or speech_recognition)")
                continue
            elif user_input.lower() == 'text':
                input_mode = "text"
                print("✅ Switched to text input")
                continue
            
            if not user_input:
                continue
            
            print("Waiting for response...")
            answer = send_question(user_input)
            if answer:
                print(f"Assistant: {answer}\n")
            else:
                print("Failed to get response\n")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    main()
