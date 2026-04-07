import socket
import struct
import time
import json
import base64
import dotenv
import os
from pathlib import Path
import sys
import warnings
import threading
import queue
import tempfile
import logging
import io
import subprocess
import signal
import requests
from noise_cancel import process_audio
from playsound import playsound
warnings.filterwarnings("ignore")
for _logger_name in ("comtypes", "comtypes.client._code_cache", "fairseq",
                      "fairseq.tasks", "torch", "numba"):
    logging.getLogger(_logger_name).setLevel(logging.ERROR)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("monika-bridge")

_rvc_pipe_dir = str(Path(__file__).resolve().parent.parent / "src" / "rvc-tts-pipe")
_rvc_dir = str(Path(__file__).resolve().parent.parent / "src" / "rvc")
for _d in (_rvc_pipe_dir, _rvc_dir):
    if _d not in sys.path:
        sys.path.insert(0, _d)
from rvc_infer import rvc_convert

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

dotenv.load_dotenv(Path(__file__).resolve().parent.parent / ".env")

CLIENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(CLIENT_DIR, "teto.pth")

UNITY_HOST = os.getenv("UNITY_BRIDGE_HOST", "127.0.0.1")
UNITY_PORT = int(os.getenv("UNITY_BRIDGE_PORT", "12346"))

SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("SERVER_PORT", "12345"))

# Where Unity reads audio from at runtime (StreamingAssets is always accessible on disk)
STREAMING_ASSETS_PATH = os.getenv("UNITY_STREAMING_ASSETS_PATH", os.path.join(CLIENT_DIR, "output"))
VOICE_OUTPUT_PATH = os.path.join(STREAMING_ASSETS_PATH, "monika_response.wav").replace("\\", "/")
log.info("Voice output path: %s", VOICE_OUTPUT_PATH)

UNITY_CONNECTED = False
UNITY_CONNECTED_LOCK = threading.Lock()


def start_whisper_server():
    whisper_path = os.path.join(CLIENT_DIR, "stt_server.py")
    if not os.path.exists(whisper_path):
        log.warning("Whisper server script not found at %s. Skipping Whisper startup.", whisper_path)
        return None

    log.info("Starting Whisper server from %s", whisper_path)
    try:
        proc = subprocess.Popen(
            [sys.executable, whisper_path],
            cwd=CLIENT_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP") else 0,
        )
        log.info("Whisper server started (pid=%s)", proc.pid)
        return proc
    except Exception as e:
        log.error("Failed to start Whisper server: %s", e)
        return None


def stop_whisper_server(proc):
    if proc is None:
        return

    if proc.poll() is not None:
        log.info("Whisper server already stopped (pid=%s)", proc.pid)
        return

    log.info("Stopping Whisper server (pid=%s)", proc.pid)
    try:
        if os.name == "nt":
            proc.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            proc.terminate()
        proc.wait(timeout=10)
        log.info("Whisper server stopped")
    except Exception:
        log.warning("Whisper server did not stop gracefully; killing")
        proc.kill()


class TTSPipeline:

    def __init__(self):
        self._q: queue.Queue = queue.Queue()
        self._running = True
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def _worker(self):
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty("voices")
            for v in voices:
                if "female" in v.name.lower() or "zira" in v.name.lower():
                    engine.setProperty("voice", v.id)
                    break
            else:
                if len(voices) >= 2:
                    engine.setProperty("voice", voices[1].id)
        except Exception as e:
            log.error("pyttsx3 init failed: %s", e)
            return

        try:
            prev = os.getcwd()
            os.chdir(CLIENT_DIR)
            _so, _se = sys.stdout, sys.stderr
            sys.stdout, sys.stderr = io.StringIO(), io.StringIO()
            try:
                pass
            finally:
                sys.stdout, sys.stderr = _so, _se
                os.chdir(prev)
            log.info("RVC model pre-loaded")
        except Exception as e:
            log.warning("RVC pre-load failed: %s", e)

        while self._running:
            try:
                item = self._q.get(timeout=0.5)
                if item is None:
                    break
                text, callback = item

                # Use unique temp file to avoid "file is being used" deadlocks between requests
                fd, tmp_wav = tempfile.mkstemp(suffix=".wav", dir=CLIENT_DIR)
                os.close(fd) 
                
                output_path = None

                try:
                    log.info("[TTS] Step 1: Generating base speech for '%s...'", text[:30])
                    engine.save_to_file(text, tmp_wav)
                    engine.runAndWait()
                    log.info("[TTS] Step 1: Base speech generated successfully.")

                    # Generate a unique path in StreamingAssets to avoid file lock issues with Unity
                    unique_name = f"monika_resp_{int(time.time())}_{os.getpid()}.wav"
                    target_path = os.path.join(STREAMING_ASSETS_PATH, unique_name).replace("\\", "/")

                    try:
                        log.info("[RVC] Step 2: Starting inference for %s", unique_name)
                        # Call RVC directly without stdout redirection to avoid hiding errors
                        output_path = rvc_convert(
                            model_path=MODEL_PATH,
                            input_path=tmp_wav,
                        )
                        log.info("[RVC] Step 2: Inference finished successfully.")
                    except Exception as rvc_err:
                        log.error("[TTS] rvc_convert failed: %s", rvc_err)
                        output_path = None

                    log.info("[TTS] rvc_convert returned: %s", output_path)
                    
                    if output_path and os.path.exists(output_path):
                        try:
                            from pydub import AudioSegment
                            os.makedirs(STREAMING_ASSETS_PATH, exist_ok=True)
                            
                            log.info("[TTS] Resampling to 48kHz...")
                            audio = AudioSegment.from_wav(output_path)
                            audio = audio.set_frame_rate(48000)
                            audio.export(target_path, format="wav")
                            
                            if os.path.exists(output_path):
                                os.remove(output_path)
                            
                            output_path = target_path
                            log.info("[TTS] Audio resampled and saved to unique path: %s", target_path)

                            # --- WORKAROUND: Play sound from Python side ---
                            def play_async(p):
                                try:
                                    from playsound import playsound
                                    playsound(p)
                                except Exception as e:
                                    log.error("[TTS] playsound failed: %s", e)
                            
                            threading.Thread(target=play_async, args=(target_path,), daemon=True).start()
                        except Exception as resample_err:
                            log.error("[TTS] Resampling failed, falling back to copy: %s", resample_err)
                            try:
                                import shutil
                                shutil.copy2(output_path, target_path)
                                output_path = target_path
                            except:
                                output_path = ""
                    else:
                        log.error("[TTS] output_path is None or missing! RVC failed.")
                        output_path = ""

                except Exception as e:
                    log.error("TTS/RVC error: %s", e)
                finally:
                    if os.path.exists(tmp_wav):
                        os.remove(tmp_wav)

                callback(output_path)
                self._q.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                log.error("TTS worker error: %s", e)

    def speak(self, text: str, callback):
        self._q.put((text, callback))

    def shutdown(self):
        self._running = False
        self._q.put(None)
        self._thread.join(timeout=3)


def _recv_exact(sock: socket.socket, n: int):
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            return None
        buf += chunk
    return buf


def _recognize_with_whisper(raw: bytes, addr):
    
    try:
        speech_text = raw.decode("utf-8").strip()
    except Exception:
        speech_text = ""

    if speech_text:
        log.info("Unity payload interpreted as text from %s: %r", addr, speech_text)
        return speech_text
    
    raw = process_audio(raw)

    
    wav_io = io.BytesIO()
    if raw[:4] == b"RIFF" and raw[8:12] == b"WAVE":
        wav_io.write(raw)
        wav_io.seek(0)
        log.info("Unity payload from %s identified as WAV audio", addr)
    elif raw:
        
        import wave

        with wave.open(wav_io, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(48000)
            wf.writeframes(raw)
        wav_io.seek(0)
        log.info("Unity payload from %s interpreted as PCM16 mono 48kHz", addr)
    else:
        return ""

    try:
        response = requests.post(
            "http://127.0.0.1:5001/recognize",
            files={"audio": ("unity_audio.wav", wav_io, "audio/wav")},
            timeout=30,
        )
        response.raise_for_status()
        j = response.json()
    except Exception as e:
        log.error("Whisper recognition request failed for %s: %s", addr, e)
        return ""

    recognized = str(j.get("text", "")).strip()
    if not recognized:
        log.warning("Whisper did not recognize speech for %s (%s)", addr, j.get("warning", "no warning"))

    log.info("Whisper recognition for %s returned: %r", addr, recognized)
    return recognized


def ask_monika(question: str) -> str | None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        timeout = float(os.getenv("CLIENT_SOCKET_TIMEOUT_SECS", "310"))
        sock.settimeout(timeout)
        sock.connect((SERVER_HOST, SERVER_PORT))

        q_bytes = question.encode("utf-8")
        sock.sendall(struct.pack("<I", len(q_bytes)))
        sock.sendall(q_bytes)

        full = ""
        while True:
            hdr = _recv_exact(sock, 4)
            if hdr is None:
                log.error("Server closed connection before response")
                return None
            (length,) = struct.unpack("<I", hdr)
            if length == 0:
                break
            if length > 32 * 1024 * 1024:
                log.error("Invalid frame length: %d", length)
                return None
            frame = _recv_exact(sock, length)
            if frame is None or len(frame) < length:
                log.error("Incomplete frame")
                return None
            full += frame.decode("utf-8")

        return full
    except Exception as e:
        log.error("ask_monika error: %s", e)
        return None
    finally:
        sock.close()


def _send_frame(conn: socket.socket, data: bytes):
    conn.sendall(struct.pack("<I", len(data)))
    conn.sendall(data)


def _send_json(conn: socket.socket, payload: dict):
    _send_frame(conn, json.dumps(payload, ensure_ascii=False).encode("utf-8"))


def _send_end(conn: socket.socket):
    conn.sendall(struct.pack("<I", 0))


def _encode_audio_file_base64(audio_path: str) -> str:
    try:
        with open(audio_path, "rb") as f:
            return base64.b64encode(f.read()).decode("ascii")
    except Exception as e:
        log.error("Failed to base64-encode audio file '%s': %s", audio_path, e)
        return ""

_busy_lock = threading.Lock()

def handle_unity_connection(conn: socket.socket, addr, tts: TTSPipeline | None):
    global UNITY_CONNECTED

    with UNITY_CONNECTED_LOCK:
        if not UNITY_CONNECTED:
            UNITY_CONNECTED = True
            log.info("Unity connected from %s [first connection]", addr)
            print("[STATUS] Unity has connected!")
        else:
            log.info("Unity connected from %s", addr)
            print("[STATUS] Unity connection re-established")

    if not _busy_lock.acquire(blocking=False):
        log.warning("Rejecting connection from %s: already processing a request.", addr)
        conn.close()
        return

    try:
        hdr = _recv_exact(conn, 4)
        if hdr is None:
            log.warning("Connection from %s closed before header received", addr)
            return

        (length,) = struct.unpack("<I", hdr)
        log.info("Received frame header from %s: length=%d", addr, length)

        max_len = 5 * 1024 * 1024
        if length == 0 or length > max_len:
            log.warning("Invalid speech length from %s: %d (max %d)", addr, length, max_len)
            return

        raw = _recv_exact(conn, length)
        if raw is None:
            log.warning("Connection from %s closed while reading payload", addr)
            return

        has_audio_packet = bool(raw)
        log.info("Unity audio packet received from %s: %s (bytes=%d)", addr, "yes" if has_audio_packet else "no", len(raw))
        log.info("Received raw payload from %s (%d bytes): %s", addr, len(raw), raw[:64])

        speech_text = _recognize_with_whisper(raw, addr)
        if not speech_text:
            log.warning("No speech text extracted from Unity audio payload %s", addr)
            _send_json(conn, {"text": "", "audio": ""})
            _send_end(conn)
            return

        log.info("Player said: %s", speech_text)

        t0 = time.perf_counter()
        answer = ask_monika(speech_text)
        elapsed = time.perf_counter() - t0
        audio_payload = ""

        if answer is None:
            log.warning("Server not available, sending recognized speech text instead")
            answer = speech_text  
        else:
            log.info("AI replied in %.2fs: %s", elapsed, answer[:80])

            log.info("[TTS-CHECK] tts=%s, pyttsx3=%s", tts, pyttsx3)
            if tts is not None and pyttsx3 is not None:
                done_event = threading.Event()
                result_holder = [None]

                def on_tts_done(wav_path):
                    result_holder[0] = wav_path
                    done_event.set()

                tts.speak(answer, on_tts_done)
                done_event.wait(timeout=120)
                log.info("[TTS-CHECK] result_holder[0]=%s", result_holder[0])
                if result_holder[0]:
                    audio_payload = str(result_holder[0])

        _send_json(conn, {"text": answer, "audio": audio_payload})
        _send_end(conn)

        log.info("Unity response completed, audio in response: %s, audio_b64_len=%d", "yes" if audio_payload else "no", len(audio_payload) if audio_payload else 0)
        log.info("Response sent (audio=%s)", "yes" if audio_payload else "no")

    except Exception as e:
        log.error("Connection handler error: %s", e)
    finally:
        _busy_lock.release()
        conn.close()


def main():
    log.info("=" * 50)
    log.info("Monika Unity Bridge")
    log.info("=" * 50)
    log.info("Listening for Unity on %s:%d", UNITY_HOST, UNITY_PORT)
    log.info("Monika AI server at  %s:%d", SERVER_HOST, SERVER_PORT)

    
    whisper_proc = start_whisper_server()

    enable_tts = os.getenv("ENABLE_TTS", "1").lower() in ("1", "true", "yes")
    tts = None
    if enable_tts and pyttsx3 is not None:
        try:
            tts = TTSPipeline()
            log.info("TTS + RVC pipeline ready")
        except Exception as e:
            log.warning("TTS init failed: %s", e)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((UNITY_HOST, UNITY_PORT))
    server.listen(4)
    server.settimeout(1.0)
    log.info("Waiting for Unity connections...")

    stop_event = threading.Event()

    def _signal_handler(signum, frame):
        log.info("Received termination signal (%s), shutting down...", signum)
        stop_event.set()

    if hasattr(signal, "SIGINT"):
        signal.signal(signal.SIGINT, _signal_handler)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _signal_handler)

    try:
        while not stop_event.is_set():
            try:
                conn, addr = server.accept()
                log.info("Unity connection received from %s", addr)
                t = threading.Thread(
                    target=handle_unity_connection, args=(conn, addr, tts), daemon=True
                )
                t.start()
            except socket.timeout:
                continue
            except OSError as e:
                if stop_event.is_set():
                    break
                log.error("Socket error in accept loop: %s", e)
                break
    except KeyboardInterrupt:
        log.info("Keyboard interrupt received, shutting down...")
        stop_event.set()
    finally:
        log.info("Closing Unity server socket")
        try:
            server.close()
        except Exception:
            pass
        if tts:
            tts.shutdown()
        stop_whisper_server(whisper_proc)


if __name__ == "__main__":
    main()