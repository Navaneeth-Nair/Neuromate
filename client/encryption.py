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


def get_shared_secret() -> str:
    secret = os.getenv("MONIKA_SHARED_SECRET")
    if secret is None:
        raise ValueError("MONIKA_SHARED_SECRET environment variable is required")
    if len(secret) < 16:
        raise ValueError(
            "MONIKA_SHARED_SECRET must be at least 16 characters for security"
        )
    return secret


def derive_key(secret: str) -> bytes:
    return hashlib.sha256(secret.encode()).digest()


class Encryption:
    def __init__(self):
        secret = get_shared_secret()
        self.key = derive_key(secret)
        self.nonce_size = NONCE_SIZE

    def encrypt(self, plaintext: bytes) -> bytes:
        nonce = os.urandom(self.nonce_size)
        aesgcm = AESGCM(self.key)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        return nonce + ciphertext

    def decrypt(self, encrypted: bytes) -> bytes:
        if len(encrypted) < self.nonce_size:
            raise ValueError("Encrypted data too short")
        nonce = encrypted[: self.nonce_size]
        ciphertext = encrypted[self.nonce_size :]
        aesgcm = AESGCM(self.key)
        return aesgcm.decrypt(nonce, ciphertext, None)

    def encrypt_str(self, plaintext: str) -> bytes:
        return self.encrypt(plaintext.encode("utf-8"))

    def decrypt_str(self, encrypted: bytes) -> str:
        return self.decrypt(encrypted).decode("utf-8")


def encrypt_message(message: str) -> bytes:
    return Encryption().encrypt_str(message)


def decrypt_message(encrypted: bytes) -> str:
    return Encryption().decrypt_str(encrypted)
