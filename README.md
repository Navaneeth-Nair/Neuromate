# NeuroMate — Beta Network Branch

> **NeuroMate** is a local-first, privacy-focused AI companion built for real-time interaction inside a **Unity** game environment. It runs entirely on your own hardware — no cloud, no subscriptions, no data leaving your machine.

---

## What Is This Branch?

This is the **`beta-network-branch`** — a complete architectural pivot from the original web-based concept. Instead of a browser app, NeuroMate is now implemented as a **local AI network** connecting three core components:

```
Unity Frontend
     │  TCP (port 12346)
     ▼
Python Client Bridge  ──► pyttsx3 TTS + RVC Voice Conversion (teto.pth)
     │  TCP (port 12345)
     ▼
Rust AI Server (monika-server)
     │  HTTP (NDJSON streaming)
     ▼
Ollama  (local LLM — default: qwen2.5:7b)
```

All communication is framed over raw TCP sockets for minimal overhead and maximum speed.

---

## Architecture Overview

### `server/` — Rust AI Backend (`monika-server`)

The core of the system. A high-performance async Rust server built with **Tokio**.

| File | Role |
|------|------|
| `main.rs` | TCP listener, session management, request orchestration, performance profiling |
| `mood_engine.rs` | Per-session ELO-based mood tracking and sentiment analysis |
| `ollama_http.rs` | Persistent HTTP client pool for Ollama, warmup & heartbeat logic |
| `filter.rs` | Safety layer — sanitizes AI responses for harmful content |
| `logging.rs` | Async disk logging of every Q&A pair with full timing breakdowns |

**Key features:**
- **Streaming responses** — AI output is forwarded token-by-token to the client as it arrives from Ollama, minimising time-to-first-byte.
- **Model warmup & heartbeat** — On startup, the server optionally warms the LLM (`OLLAMA_WARMUP=1`) and sends periodic keep-alive pings (`OLLAMA_HEARTBEAT_SECS`, default 60s) to keep the model resident in VRAM.
- **Detailed bottleneck profiling** — Every request logs per-phase timing in milliseconds: TCP read → mood engine → Ollama HTTP send → stream drain → filter → EOF → disk write.
- **Session pool** — Tracks active client connections by address.

**Dependencies:** `tokio`, `reqwest`, `serde_json`, `chrono`, `once_cell`, `tokio-util`, `futures-util`, `dotenv`

---

### `client/` — Python Unity Bridge

Runs on the same machine as Unity. Bridges the game engine to the Rust server and handles voice synthesis locally.

| File | Role |
|------|------|
| `client.py` | TCP server for Unity + AI relay + TTS/RVC voice pipeline |
| `tortoise_api.py` | Alternative Tortoise TTS integration via Gradio API |

**Voice pipeline (`client.py`):**
1. Unity sends the player's speech (text) over TCP.
2. The bridge forwards it to the Rust server and waits for the AI reply.
3. The reply is passed to **pyttsx3** which generates a base WAV file.
4. The WAV is piped through **RVC (Retrieval-based Voice Conversion)** using a custom voice model (`teto.pth`) to produce a styled, character-consistent voice.
5. The final audio path + text are sent back to Unity as a JSON frame.

**Concurrency model:** A single `threading.Lock` ensures only one Unity request is processed at a time (TTS is stateful). Requests arriving while busy are rejected gracefully.

---

### `middleware/` — Rust Encryption Layer

A standalone Rust library crate providing end-to-end encryption utilities for securing the TCP communication channel.

| File | Role |
|------|------|
| `encryption.rs` | AES-256-GCM encrypt/decrypt with SHA-256 key derivation |
| `lib.rs` | Crate entry point |

**Details:**
- Cipher: **AES-256-GCM** (authenticated encryption)
- Key derivation: **SHA-256** hash of `MONIKA_SHARED_SECRET` env var
- Nonce: cryptographically random, prepended to ciphertext
- Configurable via `.env`: `MONIKA_SHARED_SECRET`, `MONIKA_NONCE_SIZE`, `MONIKA_CIPHER_TYPE`

---

## Mood Engine

The Rust server tracks the emotional state of each connected client using an **ELO-based rating system**:

- Each session starts at ELO `1600` (Neutral baseline).
- Every incoming message is sentiment-analysed (keyword-based positive/negative scoring).
- The ELO rating shifts up or down based on detected sentiment using a standard K=32 ELO update.
- After **62 hours** of inactivity, the rating resets (decay).
- The current mood label (`very negative` → `very positive`) is injected directly into the Ollama prompt as context.

| ELO Range | Mood Label |
|-----------|------------|
| < 1200 | Very Negative |
| 1200–1400 | Negative |
| 1400–1800 | Neutral |
| 1800–2000 | Positive |
| > 2000 | Very Positive |

---

## Getting Started

### Prerequisites

| Tool | Purpose |
|------|---------|
| [Rust + Cargo](https://rustup.rs/) | Build the server and middleware |
| [Python 3.10+](https://python.org) | Run the client bridge |
| [Ollama](https://ollama.com/) | Local LLM inference backend |
| Unity (any recent version) | Frontend game engine |

---

### 1. Clone the Branch

```bash
git clone -b beta-network-branch https://github.com/Navaneeth-Nair/Neuromate.git
cd Neuromate
```

---

### 3. Pull the Ollama Model

```bash
ollama pull qwen2.5:7b
```

---

### 4. Build & Run the Rust Server

```bash
cd server
cargo build --release
cargo run --release
```

The server listens on `SERVER_HOST:SERVER_PORT` (default `127.0.0.1:12345`).

---

### 5. Install Python Dependencies & Run the Bridge

```bash
cd client
pip install python-dotenv pyttsx3 requests sounddevice soundfile gradio_client PyYAML
python client.py
```

The bridge listens for Unity on `UNITY_BRIDGE_HOST:UNITY_BRIDGE_PORT` (default `127.0.0.1:12346`).

> **Note:** Place your RVC voice model (`teto.pth`) inside the `client/` directory.  
> Ensure the `rvc-tts-pipe` and `rvc` source directories exist at `src/rvc-tts-pipe/` and `src/rvc/` relative to the repo root.

---

### 6. Connect from Unity

From your Unity C# scripts, open a TCP connection to `127.0.0.1:12346`.

**Protocol (framed binary):**
- Send: `[4-byte little-endian uint32 length][UTF-8 text bytes]`
- Receive frames until a `[4-byte zero length]` EOF frame:
  - Each frame: `[4-byte length][JSON bytes]` → `{"text": "...", "audio": "/path/to/audio.wav"}`

---

## Project Structure

```
Neuromate/
├── .env                    # Local config (not committed)
├── README.md
│
├── server/                 # Rust AI server (monika-server)
│   ├── Cargo.toml
│   └── src/
│       ├── main.rs         # TCP server, request handler, streaming orchestration
│       ├── mood_engine.rs  # ELO mood tracking + sentiment analysis
│       ├── ollama_http.rs  # Ollama HTTP client, warmup, RTT logging
│       ├── filter.rs       # Response safety filter
│       └── logging.rs      # Async disk logger with timing breakdowns
│
├── client/                 # Python Unity bridge
│   ├── client.py           # TCP bridge + TTS + RVC voice pipeline
│   ├── tortoise_api.py     # Tortoise TTS via Gradio (alternative voice backend)
│   └── teto.pth            # RVC voice model (not committed — add manually)
│
└── middleware/             # Rust encryption library
    ├── Cargo.toml
    └── src/
        ├── lib.rs
        └── encryption.rs   # AES-256-GCM encryption/decryption
```

---

## Roadmap

- [x] Rust TCP server with Ollama streaming integration
- [x] Python Unity bridge (TCP relay)
- [x] TTS + RVC voice pipeline (`pyttsx3` → `teto.pth`)
- [x] ELO-based mood engine with sentiment analysis
- [x] Response safety filter
- [x] AES-256-GCM encryption middleware
- [x] Model warmup & heartbeat keep-alive
- [x] Per-request bottleneck profiling & disk logging
- [ ] Integrate encryption middleware into live TCP sockets
- [ ] Persistent mood state across sessions (disk storage)
- [ ] Unity C# client SDK / example project
- [ ] Tortoise TTS backend as drop-in replacement for RVC
- [ ] Multi-character voice profile support
- [ ] Web dashboard for mood & session analytics

---

## Contributing

```bash
git checkout -b feature/your-feature
git commit -m "Add your message here"
git push origin feature/your-feature
```

Pull requests are welcome. Please open an issue first for major changes.

---

## License

This project is licensed under the **MIT License**.  
You are free to use, modify, and distribute with attribution.

---

## Contact

📧 **Email:** neuromate07@gmail.com

---

> *NeuroMate started as a web wellness app — and evolved into something more intimate: a real-time, emotionally aware AI companion living inside a virtual world, running entirely on your own machine.*

**"Build what you wish existed."**
