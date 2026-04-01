#!/usr/bin/env python3

import socket
import struct
import time
import json
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

from encryption import Encryption

warnings.filterwarnings("ignore")
for _logger_name in (
    "comtypes",
    "comtypes.client._code_cache",
    "fairseq",
    "fairseq.tasks",
    "torch",
    "numba",
):
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
from rvc_infer import rvc_convert, rvc_init

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

_encryption = Encryption()


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
                rvc_init(MODEL_PATH)
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

                tmp_wav = os.path.join(CLIENT_DIR, "_tts_temp.wav")
                output_path = None

                try:
                    engine.save_to_file(text, tmp_wav)
                    engine.runAndWait()

                    prev = os.getcwd()
                    os.chdir(CLIENT_DIR)
                    _so, _se = sys.stdout, sys.stderr
                    sys.stdout, sys.stderr = io.StringIO(), io.StringIO()
                    try:
                        output_path = rvc_convert(
                            model_path=MODEL_PATH,
                            input_path=tmp_wav,
                        )
                    finally:
                        sys.stdout, sys.stderr = _so, _se
                        os.chdir(prev)
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


def ask_monika(question: str) -> str | None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        timeout = float(os.getenv("CLIENT_SOCKET_TIMEOUT_SECS", "310"))
        sock.settimeout(timeout)
        sock.connect((SERVER_HOST, SERVER_PORT))

        q_bytes = _encryption.encrypt_str(question)
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
            decrypted = _encryption.decrypt(frame)
            full += decrypted

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


_busy_lock = threading.Lock()


def handle_unity_connection(conn: socket.socket, addr, tts: TTSPipeline | None):
    log.info("Unity connected from %s", addr)

    if not _busy_lock.acquire(blocking=False):
        log.warning("Rejecting connection from %s: already processing a request.", addr)
        conn.close()
        return

    try:
        hdr = _recv_exact(conn, 4)
        if hdr is None:
            return
        (length,) = struct.unpack("<I", hdr)
        if length == 0 or length > 1 * 1024 * 1024:
            log.warning("Invalid speech length: %d", length)
            return
        raw = _recv_exact(conn, length)
        if raw is None:
            return
        speech_text = raw.decode("utf-8").strip()
        if not speech_text:
            return

        log.info("Player said: %s", speech_text)

        t0 = time.perf_counter()
        answer = ask_monika(speech_text)
        elapsed = time.perf_counter() - t0

        if answer is None:
            _send_json(conn, {"text": "[No response from AI]", "audio": ""})
            _send_end(conn)
            return

        log.info("AI replied in %.2fs: %s", elapsed, answer[:80])

        audio_path = ""
        if tts is not None and pyttsx3 is not None:
            done_event = threading.Event()
            result_holder = [None]

            def on_tts_done(wav_path):
                result_holder[0] = wav_path
                done_event.set()

            tts.speak(answer, on_tts_done)
            done_event.wait(timeout=120)
            if result_holder[0]:
                audio_path = str(result_holder[0])

        _send_json(conn, {"text": answer, "audio": audio_path})
        _send_end(conn)

        log.info("Response sent (audio=%s)", "yes" if audio_path else "no")

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
    log.info("Waiting for Unity connections...")

    try:
        while True:
            conn, addr = server.accept()
            t = threading.Thread(
                target=handle_unity_connection, args=(conn, addr, tts), daemon=True
            )
            t.start()
    except KeyboardInterrupt:
        log.info("Shutting down...")
    finally:
        server.close()
        if tts:
            tts.shutdown()


if __name__ == "__main__":
    main()
