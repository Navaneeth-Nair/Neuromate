#!/usr/bin/env python3
import socket
import struct
import time
import dotenv
import os
from pathlib import Path
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
    sr = None

# Repo-root .env (works regardless of current working directory)
dotenv.load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Initialize Vosk for offline STT
_vosk_model = None

def init_vosk():
    """Initialize Vosk model for offline speech recognition."""
    global _vosk_model
    try:
        import vosk
    except ImportError:
        print("  Vosk not installed (pip install vosk) — offline STT disabled")
        return False
    try:
        vosk.SetLogLevel(-1)

        # Check if model exists
        model_path = "model"
        if not os.path.exists(model_path):
            print(" Vosk model not found. Downloading...")
            print("   Visit: https://alphacephei.com/vosk/models")
            print("   Download a model and extract to ./model directory")
            return False
        
        _vosk_model = vosk.Model(model_path)
        print(" Offline STT (Vosk) initialized")
        return True
    except Exception as e:
        print(f"  Vosk offline STT unavailable: {e}")
        return False

def get_speech_offline():
    """Capture speech using Vosk offline engine."""
    try:
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4096)
        stream.start_stream()
        
        rec = vosk.KaldiRecognizer(_vosk_model, 16000)
        rec.SetWords(json.dumps(["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]))
        
        print(" Listening (offline)...")
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
        print(f" Offline STT error: {e}")
        return None

def get_speech_online():
    """Fallback to online speech recognition."""
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print(" Listening (online)...")
            audio = recognizer.listen(source, timeout=10)
        
        try:
            text = recognizer.recognize_google(audio)
            print(f"  > {text}")
            return text
        except sr.UnknownValueError:
            print(" Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f" Online STT error: {e}")
            return None
            
    except Exception as e:
        print(f" Online STT error: {e}")
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
        print(" speech_recognition not installed for online fallback")
        return None


def _recv_exact(sock, n):
    """Read exactly n bytes from TCP stream (recv may return partial data)."""
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            return None
        buf += chunk
    return buf


def send_question(question, host=None, port=None):
    """Send question to Monika TCP server and stream response.

    Uses SERVER_HOST and SERVER_PORT from the environment when not passed
    (defaults: 127.0.0.1:12345 — the Rust server port, not Ollama's 11434).
    
    The server streams the response as multiple length-prefixed frames:
      [4-byte length] [data]
      [4-byte length] [data]
      ...
      [4 bytes: 0]  ← EOF marker (empty frame)
    
    This function:
    - Collects full response for TTS processing
    - Displays words one-by-one for visual streaming effect
    """
    if host is None:
        host = os.getenv("SERVER_HOST", "127.0.0.1")
    if port is None:
        port = int(os.getenv("SERVER_PORT", "12345"))

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Slightly above server OLLAMA_HTTP_TIMEOUT_SECS so the server can finish first
        client_socket.settimeout(float(os.getenv("CLIENT_SOCKET_TIMEOUT_SECS", "310")))
        client_socket.connect((host, port))

        # Send question length and data (little-endian u32, matches server)
        question_bytes = question.encode("utf-8")
        client_socket.sendall(struct.pack("<I", len(question_bytes)))
        client_socket.sendall(question_bytes)

        # ── Stream and collect response ──────────────────────────────────────
        # Keep full chunks for TTS, display word-by-word
        print("Assistant: ", end="", flush=True)
        full_response = ""  # For TTS
        buffer = ""  # For word-by-word display
        
        while True:
            # Read 4-byte length prefix
            length_data = _recv_exact(client_socket, 4)
            if length_data is None:
                print(
                    "\nError: connection closed before response length "
                    f"(is the server running on {host}:{port}?)"
                )
                return None
            
            (length,) = struct.unpack("<I", length_data)
            
            # Empty frame (length=0) signals EOF
            if length == 0:
                # Print any remaining buffered content
                if buffer:
                    print(buffer, end="", flush=True)
                break
            
            # Sanity check
            if length > 32 * 1024 * 1024:
                print(f"\nError: invalid frame length ({length})")
                return None

            # Read exactly `length` bytes
            frame_data = _recv_exact(client_socket, length)
            if frame_data is None or len(frame_data) < length:
                print("\nError: connection closed before full frame body")
                return None
            
            # Decode the chunk
            chunk = frame_data.decode("utf-8")
            
            # Keep full chunk for TTS processing
            full_response += chunk
            
            # Add to display buffer
            buffer += chunk
            
            # Split by spaces and display word-by-word
            # Keep the last partial word in buffer in case it's incomplete
            parts = buffer.split(" ")
            
            # Print all complete words (all but the last part)
            for word in parts[:-1]:
                print(word + " ", end="", flush=True)
            
            # Keep the last part in buffer (might be incomplete word)
            buffer = parts[-1]

        print()  # Newline after streaming completes
        return full_response
        
    except socket.timeout:
        print(
            "\nError: timed out waiting for the server (Ollama may be slow or unreachable)."
        )
        return None
    except OSError as e:
        print(f"\nError: {e}")
        return None
    except Exception as e:
        print(f"\nError: {e}")
        return None
    finally:
        client_socket.close()

def main():
    """Main client loop."""
    print("=" * 50)
    print("Monika Client - Speech & Text Interface")
    print("=" * 50)
    _h = os.getenv("SERVER_HOST", "127.0.0.1")
    _p = int(os.getenv("SERVER_PORT", "12345"))
    print(f"TCP server (Monika): {_h}:{_p}  —  start `monika-server` here before chatting.")
    print(
        "Replies are limited to about one paragraph (server prompt + token cap)."
    )
    
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
                if offline_available or sr is not None:
                    input_mode = "voice"
                    print(" Switched to voice input")
                else:
                    print(" Voice not available (install vosk or speech_recognition)")
                continue
            elif user_input.lower() == 'text':
                input_mode = "text"
                print(" Switched to text input")
                continue
            
            if not user_input:
                continue
            
            print("Waiting for response…")
            t0 = time.perf_counter()
            answer = send_question(user_input)
            elapsed = time.perf_counter() - t0
            if answer is not None:
                print(f"\n({elapsed:.2f}s)\n")
                # answer is the full response that can be passed to TTS
            else:
                print(f"Failed to get response after {elapsed:.2f}s\n")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    main()