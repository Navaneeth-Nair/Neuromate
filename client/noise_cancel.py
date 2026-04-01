"""
noise_cancel.py
---------------
Noise cancellation module for the Monika Unity Bridge.

Algorithm:
  - Spectral subtraction  : estimates background noise from the first
    N_NOISE_FRAMES frames and subtracts it from every subsequent frame.
  - Adaptive gain control : RMS-normalises the voice signal so that
    quiet speakers are amplified and already-loud signals are left alone.

Public API
----------
    process_audio(raw: bytes) -> bytes

    `raw` may be either:
      • a valid WAV file (RIFF header present), or
      • raw PCM-16 mono 16 kHz bytes (no header).

    Always returns a WAV file (bytes) at 16-bit mono 16 kHz.
"""

import io
import wave
import struct
import logging
import numpy as np

log = logging.getLogger("noise-cancel")

# ---------------------------------------------------------------------------
# Tuneable constants
# ---------------------------------------------------------------------------

SAMPLE_RATE      = 48_000   # Hz  – must match Whisper's expected rate or be resampled downstream
FRAME_MS         = 20       # ms  per FFT frame
FRAME_SIZE       = int(SAMPLE_RATE * FRAME_MS / 1000)   # samples per frame
HOP_SIZE         = FRAME_SIZE // 2                       # 50 % overlap

N_NOISE_FRAMES   = 10       # number of leading frames used to estimate noise floor
OVER_SUBTRACT    = 1.5      # spectral over-subtraction factor  (1.0 – 2.0)
SPECTRAL_FLOOR   = 0.02     # minimum residual magnitude (prevents musical noise)

TARGET_RMS       = 0.15     # target RMS level after adaptive gain (0-1 float)
MAX_GAIN         = 8.0      # hard ceiling on adaptive gain multiplier
MIN_GAIN         = 0.5      # hard floor  (don't amplify already-loud signals past this)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _bytes_to_float32(pcm16: bytes) -> np.ndarray:
    """Convert raw PCM-16 LE bytes → float32 array in [-1, 1]."""
    samples = np.frombuffer(pcm16, dtype=np.int16).astype(np.float32)
    return samples / 32768.0


def _float32_to_bytes(arr: np.ndarray) -> bytes:
    """Convert float32 array in [-1, 1] → PCM-16 LE bytes (clipped)."""
    clipped = np.clip(arr, -1.0, 1.0)
    return (clipped * 32767).astype(np.int16).tobytes()


def _read_audio(raw: bytes) -> bytes:
    """
    Accept either a WAV file or bare PCM-16 bytes.
    Returns raw PCM-16 bytes (no header).
    """
    if raw[:4] == b"RIFF" and raw[8:12] == b"WAVE":
        with wave.open(io.BytesIO(raw), "rb") as wf:
            pcm = wf.readframes(wf.getnframes())
        return pcm
    return raw


def _wrap_wav(pcm16: bytes) -> bytes:
    """Wrap raw PCM-16 mono 16 kHz bytes in a proper WAV container."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm16)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Spectral subtraction
# ---------------------------------------------------------------------------

def _spectral_subtract(signal: np.ndarray) -> np.ndarray:
    """
    Reduce background noise via overlap-add spectral subtraction.

    Steps
    -----
    1.  Estimate the noise power spectrum from the first N_NOISE_FRAMES frames.
    2.  For every frame subtract OVER_SUBTRACT * noise_power from the magnitude
        spectrum, flooring at SPECTRAL_FLOOR * noise_power to avoid artefacts.
    3.  Reconstruct the waveform with overlap-add (OLA).
    """
    n      = len(signal)
    window = np.hanning(FRAME_SIZE)

    # --- Step 1: noise estimation ---------------------------------------
    noise_power = np.zeros(FRAME_SIZE)
    frames_used = 0
    for start in range(0, FRAME_SIZE * N_NOISE_FRAMES, HOP_SIZE):
        end = start + FRAME_SIZE
        if end > n:
            break
        frame  = signal[start:end] * window
        power  = np.abs(np.fft.rfft(frame, n=FRAME_SIZE)) ** 2
        noise_power += power
        frames_used += 1

    if frames_used == 0:
        log.warning("Audio too short for noise estimation – skipping spectral subtraction")
        return signal

    noise_power /= frames_used
    log.debug("Noise estimated from %d frames", frames_used)

    # --- Step 2 & 3: subtract & reconstruct ----------------------------
    output      = np.zeros(n + FRAME_SIZE)
    window_sum  = np.zeros(n + FRAME_SIZE)

    for start in range(0, n, HOP_SIZE):
        end   = start + FRAME_SIZE
        frame = np.zeros(FRAME_SIZE)
        actual = min(FRAME_SIZE, n - start)
        frame[:actual] = signal[start:start + actual]
        frame *= window

        spectrum   = np.fft.rfft(frame, n=FRAME_SIZE)
        magnitude  = np.abs(spectrum)
        phase      = np.angle(spectrum)

        # Spectral subtraction with floor
        clean_mag  = magnitude - OVER_SUBTRACT * np.sqrt(noise_power)
        floor_mag  = SPECTRAL_FLOOR * np.sqrt(noise_power)
        clean_mag  = np.maximum(clean_mag, floor_mag)

        clean_spec = clean_mag * np.exp(1j * phase)
        clean_frame = np.fft.irfft(clean_spec, n=FRAME_SIZE) * window

        output[start:start + FRAME_SIZE]     += clean_frame
        window_sum[start:start + FRAME_SIZE] += window ** 2

    # Normalise by the OLA window sum (avoid divide-by-zero)
    nonzero = window_sum > 1e-8
    output[nonzero] /= window_sum[nonzero]

    return output[:n]


# ---------------------------------------------------------------------------
# Adaptive gain control
# ---------------------------------------------------------------------------

def _adaptive_gain(signal: np.ndarray) -> np.ndarray:
    rms = float(np.sqrt(np.mean(signal ** 2))) if len(signal) else 0.0
    if rms < 1e-9:
        log.debug("Signal RMS near zero – skipping adaptive gain")
        return signal

    gain = TARGET_RMS / rms
    gain = float(np.clip(gain, MIN_GAIN, MAX_GAIN))
    log.debug("Adaptive gain: RMS=%.4f  gain=%.2fx", rms, gain)
    return signal * gain


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def process_audio(raw: bytes) -> bytes:

    if not raw:
        log.warning("process_audio received empty payload – returning as-is")
        return raw

    pcm = _read_audio(raw)
    signal = _bytes_to_float32(pcm)

    log.info("noise_cancel: input  %.3f s  RMS=%.4f",
             len(signal) / SAMPLE_RATE,
             float(np.sqrt(np.mean(signal ** 2))) if len(signal) else 0.0)

    # signal = _spectral_subtract(signal)
    signal = _adaptive_gain(signal)

    log.info("noise_cancel: output RMS=%.4f",
             float(np.sqrt(np.mean(signal ** 2))) if len(signal) else 0.0)

    return _wrap_wav(_float32_to_bytes(signal))