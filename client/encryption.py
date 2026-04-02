#!/usr/bin/env python3
"""
Encryption module for NeuroMate client.
Implements AES-256-GCM encryption matching the Rust middleware.
"""

import os
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import dotenv
from pathlib import Path

dotenv.load_dotenv(Path(__file__).resolve().parent.parent / ".env")

NONCE_SIZE = 12


def _init_aesgcm() -> AESGCM:
    secret = os.getenv("MONIKA_SHARED_SECRET")
    if secret is None:
        raise ValueError("MONIKA_SHARED_SECRET environment variable is required")
    if len(secret) < 16:
        raise ValueError(
            "MONIKA_SHARED_SECRET must be at least 16 characters for security"
        )
    key = hashlib.sha256(secret.encode()).digest()
    return AESGCM(key)


_AESGCM_INSTANCE = _init_aesgcm()


def encrypt_message(message: str) -> bytes:
    plaintext = message.encode("utf-8")
    nonce = os.urandom(NONCE_SIZE)
    ciphertext = _AESGCM_INSTANCE.encrypt(nonce, plaintext, None)
    return nonce + ciphertext


def decrypt_message(encrypted: bytes) -> str:
    if len(encrypted) < NONCE_SIZE:
        raise ValueError("Encrypted data too short")
    nonce = encrypted[: NONCE_SIZE]
    ciphertext = encrypted[NONCE_SIZE :]
    plaintext = _AESGCM_INSTANCE.decrypt(nonce, ciphertext, None)
    return plaintext.decode("utf-8")
