#!/usr/bin/env python3
import socket
import struct
import time
import dotenv
import os
from pathlib import Path
import sys
import warnings
import threading
import queue
import winsound
import tempfile
import logging
import io

# Suppress noisy loggers before any imports that trigger them
warnings.filterwarnings("ignore")
for _logger_name in ("comtypes", "comtypes.client._code_cache", "fairseq",
                      "fairseq.tasks", "torch", "numba"):
    logging.getLogger(_logger_name).setLevel(logging.ERROR)

# Import rvc_convert from local src/rvc-tts-pipe (uses fairseq, not faiss)
_rvc_pipe_dir = str(Path(__file__).resolve().parent.parent / "src" / "rvc-tts-pipe")
_rvc_dir = str(Path(__file__).resolve().parent.parent / "src" / "rvc")
for _d in (_rvc_pipe_dir, _rvc_dir):
    if _d not in sys.path:
        sys.path.insert(0, _d)
from rvc_infer import rvc_convert, rvc_init

try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

# Repo-root .env (works regardless of current working directory)
dotenv.load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# ==============================================================================
# Pyttsx3 Threaded Pipeline
# ==============================================================================
class SimpleTTSPipeline:
    """A threaded TTS pipeline to prevent audio from blocking the main chat interface."""
    def __init__(self, auto_play=True):
        self.q = queue.Queue()
        self.auto_play = auto_play
        self.running = True
        self.task_counter = 0
        
        # Start background worker thread
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()

    def _worker(self):
        """Worker thread that initializes and runs the pyttsx3 engine."""
        # pyttsx3 must be initialized in the thread where it will run
        try:
            engine = pyttsx3.init()
            # Use a female voice for cleaner RVC input
            voices = engine.getProperty('voices')
            for v in voices:
                if 'female' in v.name.lower() or 'zira' in v.name.lower():
                    engine.setProperty('voice', v.id)
                    break
            else:
                # Fallback: second voice is usually female on Windows
                if len(voices) >= 2:
                    engine.setProperty('voice', voices[1].id)
        except Exception as e:
            print(f"\n[TTS Engine Error] Failed to initialize pyttsx3: {e}")
            return

        # Resolve paths relative to this script's directory (where teto.pth lives)
        client_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(client_dir, "teto.pth")

        # Pre-load RVC models once so first inference is fast
        try:
            prev_cwd = os.getcwd()
            os.chdir(client_dir)
            _real_stdout, _real_stderr = sys.stdout, sys.stderr
            sys.stdout = io.StringIO()
            sys.stderr = io.StringIO()
            try:
                rvc_init(model_path)
            finally:
                sys.stdout, sys.stderr = _real_stdout, _real_stderr
                os.chdir(prev_cwd)
        except Exception as e:
            print(f"[RVC] Model pre-load failed: {e}")

        while self.running:
            try:
                text = self.q.get(timeout=0.5)
                if text is None:  # Shutdown signal
                    break
                
                # 1. Save pyttsx3 output to a temporary WAV file
                tmp_wav = os.path.join(client_dir, "_tts_temp.wav")
                engine.save_to_file(text, tmp_wav)
                engine.runAndWait()

                # 2. Run RVC voice conversion with teto.pth
                try:
                    # rvc_convert relies on os.getcwd() for hubert_base.pt,
                    # rmvpe.pt and output dir – ensure we're in client_dir.
                    prev_cwd = os.getcwd()
                    os.chdir(client_dir)
                    # Suppress all RVC internal prints so they don't
                    # pollute the chat interface.
                    _real_stdout, _real_stderr = sys.stdout, sys.stderr
                    sys.stdout = io.StringIO()
                    sys.stderr = io.StringIO()
                    try:
                        output_path = rvc_convert(
                            model_path=model_path,
                            input_path=tmp_wav,
                        )
                    finally:
                        sys.stdout, sys.stderr = _real_stdout, _real_stderr
                        os.chdir(prev_cwd)

                    # 3. Play the converted WAV
                    winsound.PlaySound(output_path, winsound.SND_FILENAME)
                except Exception as rvc_err:
                    print(f"\n[RVC Error] {rvc_err}")
                finally:
                    # Clean up the temp pyttsx3 wav
                    if os.path.exists(tmp_wav):
                        os.remove(tmp_wav)

                self.q.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"\n[TTS Worker Error] {e}")

    def speak(self, text):
        """Queue the full text chunk to be spoken."""
        if not self.auto_play or not text.strip():
            return -1
        
        self.task_counter += 1
        self.q.put(text)
        return self.task_counter

    def shutdown(self):
        """Cleanly shut down the TTS worker thread."""
        self.running = False
        self.q.put(None)
        self.thread.join(timeout=2)

# ==============================================================================
# Client Logic
# ==============================================================================

_tts_pipeline = None

def init_tts(enable_tts: bool = True, auto_play: bool = True):
    """Initialize TTS Pipeline."""
    global _tts_pipeline
    
    if not enable_tts:
        print("ℹ  TTS disabled")
        return None
    
    if pyttsx3 is None:
        print(" TTS not available (install pyttsx3 for TTS support)")
        return None

    try:
        _tts_pipeline = SimpleTTSPipeline(auto_play=auto_play)
        print(" TTS Pipeline initialized")
        return _tts_pipeline
    except Exception as e:
        print(f" TTS initialization failed: {e}")
        return None

def get_speech_online():
    """Get speech using online speech recognition."""
    try:
        if sr is None:
            print(" speech_recognition not installed")
            return None
            
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print(" Listening...")
            audio = recognizer.listen(source, timeout=10)
        
        try:
            text = recognizer.recognize_google(audio)
            print(f"  > {text}")
            return text
        except sr.UnknownValueError:
            print(" Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f" Speech recognition error: {e}")
            return None
            
    except Exception as e:
        print(f" Error: {e}")
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
    """Send question to Monika TCP server and stream response."""
    if host is None:
        host = os.getenv("SERVER_HOST", "127.0.0.1")
    if port is None:
        port = int(os.getenv("SERVER_PORT", "12345"))

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.settimeout(float(os.getenv("CLIENT_SOCKET_TIMEOUT_SECS", "310")))
        client_socket.connect((host, port))

        question_bytes = question.encode("utf-8")
        client_socket.sendall(struct.pack("<I", len(question_bytes)))
        client_socket.sendall(question_bytes)

        print("Assistant: ", end="", flush=True)
        full_response = ""
        buffer = ""
        
        while True:
            length_data = _recv_exact(client_socket, 4)
            if length_data is None:
                print(f"\nError: connection closed before response length (is server running on {host}:{port}?)")
                return None
            
            (length,) = struct.unpack("<I", length_data)
            
            if length == 0:
                if buffer:
                    print(buffer, end="", flush=True)
                break
            
            if length > 32 * 1024 * 1024:
                print(f"\nError: invalid frame length ({length})")
                return None

            frame_data = _recv_exact(client_socket, length)
            if frame_data is None or len(frame_data) < length:
                print("\nError: connection closed before full frame body")
                return None
            
            chunk = frame_data.decode("utf-8")
            full_response += chunk
            buffer += chunk
            
            parts = buffer.split(" ")
            
            for word in parts[:-1]:
                print(word + " ", end="", flush=True)
            
            buffer = parts[-1]

        print() 
        return full_response
        
    except socket.timeout:
        print("\nError: timed out waiting for the server (Ollama may be slow or unreachable).")
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
    print("Monika Client - Text & TTS Interface")
    print("=" * 50)
    _h = os.getenv("SERVER_HOST", "127.0.0.1")
    _p = int(os.getenv("SERVER_PORT", "12345"))
    print(f"TCP server (Monika): {_h}:{_p}")
    print("Replies are limited to about one paragraph (server prompt + token cap).")
    
    enable_tts = os.getenv("ENABLE_TTS", "1").lower() in ("1", "true", "yes")
    enable_voice = sr is not None and os.getenv("ENABLE_VOICE", "1").lower() in ("1", "true", "yes")
    
    tts = None
    if enable_tts:
        tts = init_tts(enable_tts=True, auto_play=True)
    
    print("\nCommands:")
    print("  'quit'    - Exit")
    if enable_voice:
        print("  'voice'   - Use voice input")
    print("  'text'    - Use text input")
    if tts:
        print("  'tts on'  - Enable text-to-speech")
        print("  'tts off' - Disable text-to-speech")
    print("  'help'    - Show this help\n")
    
    input_mode = "text"
    tts_enabled = enable_tts and tts is not None
    
    while True:
        try:
            if input_mode == "text":
                user_input = input("You: ").strip()
            else:
                user_input = get_speech_online()
                if user_input is None:
                    print("Failed to capture speech. Switching to text mode.")
                    input_mode = "text"
                    continue
                print(f"You: {user_input}")
            
            if user_input.lower() == 'quit':
                print("Goodbye!")
                break
            elif user_input.lower() == 'help':
                print("\nCommands:")
                print("  'quit'    - Exit")
                if enable_voice:
                    print("  'voice'   - Use voice input")
                print("  'text'    - Use text input")
                if tts:
                    print("  'tts on'  - Enable text-to-speech")
                    print("  'tts off' - Disable text-to-speech")
                print("  'help'    - Show this help\n")
                continue
            elif user_input.lower() == 'voice':
                if enable_voice:
                    input_mode = "voice"
                    print(" Switched to voice input")
                else:
                    print(" Voice not available (install SpeechRecognition)")
                continue
            elif user_input.lower() == 'text':
                input_mode = "text"
                print("Switched to text input")
                continue
            elif user_input.lower() == 'tts on':
                if tts:
                    tts_enabled = True
                    print(" Text-to-speech enabled")
                else:
                    print(" TTS not available")
                continue
            elif user_input.lower() == 'tts off':
                tts_enabled = False
                print(" Text-to-speech disabled")
                continue
            
            if not user_input:
                continue
            
            print("Waiting for response…")
            t0 = time.perf_counter()
            answer = send_question(user_input)
            elapsed = time.perf_counter() - t0
            
            if answer is not None:
                print(f"\n({elapsed:.2f}s)\n")
                
                if tts_enabled and tts:
                    try:
                        task_id = tts.speak(answer)
                        print(f" Speech queued (task {task_id})")
                    except Exception as e:
                        print(f" TTS error: {e}")
            else:
                print(f"Failed to get response after {elapsed:.2f}s\n")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")
    
    if tts:
        try:
            tts.shutdown()
        except:
            pass

if __name__ == "__main__":
    main()