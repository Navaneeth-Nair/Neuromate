#!/usr/bin/env python3
"""
Test client for encrypted communication with the server.
This demonstrates how encryption works between client and server.
"""

import socket
import struct
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
import hashlib

SHARED_SECRET = os.getenv("MONIKA_SHARED_SECRET", "monika-e2e-shared-secret-v1-default")
NONCE_SIZE = 12


def derive_key(secret: str) -> bytes:
    """Derive 256-bit key from secret using SHA-256."""
    return hashlib.sha256(secret.encode()).digest()


class EncryptedClient:
    def __init__(self, host="127.0.0.1", port=12345):
        self.host = host
        self.port = port
        self.key = derive_key(SHARED_SECRET)
        self.aesgcm = AESGCM(self.key)

    def encrypt(self, plaintext: bytes) -> bytes:
        """Encrypt plaintext with a random nonce."""
        nonce = os.urandom(NONCE_SIZE)
        ciphertext = self.aesgcm.encrypt(nonce, plaintext, None)
        return nonce + ciphertext

    def decrypt(self, encrypted: bytes) -> bytes:
        """Decrypt ciphertext, extracting nonce from the beginning."""
        nonce = encrypted[:NONCE_SIZE]
        ciphertext = encrypted[NONCE_SIZE:]
        return self.aesgcm.decrypt(nonce, ciphertext, None)

    def send_message(self, message: str) -> str:
        """Send encrypted message and receive encrypted response."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)
        sock.connect((self.host, self.port))

        # Encrypt and send
        encrypted = self.encrypt(message.encode("utf-8"))
        sock.sendall(struct.pack("<I", len(encrypted)))
        sock.sendall(encrypted)
        print(f"[CLIENT] Sent encrypted message: {len(encrypted)} bytes")

        # Receive response chunks
        full_response = ""
        while True:
            hdr = sock.recv(4)
            if not hdr:
                break
            length = struct.unpack("<I", hdr)[0]
            if length == 0:
                break  # EOF

            chunk = sock.recv(length)
            if not chunk:
                break

            # Decrypt chunk
            decrypted = self.decrypt(chunk)
            full_response += decrypted.decode("utf-8")
            print(
                f"[CLIENT] Received chunk: {len(chunk)} bytes -> {len(decrypted)} chars"
            )

        sock.close()
        return full_response


def test_plaintext_mode():
    """Test without encryption (ENABLE_ENCRYPTION=0)."""
    print("\n" + "=" * 50)
    print("TEST: Plaintext Mode (No Encryption)")
    print("=" * 50)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)
    sock.connect(("127.0.0.1", 12345))

    message = "Hello, how are you?"
    msg_bytes = message.encode("utf-8")
    sock.sendall(struct.pack("<I", len(msg_bytes)))
    sock.sendall(msg_bytes)
    print(f"[CLIENT] Sent plaintext: {message}")

    # Receive response
    full_response = ""
    while True:
        hdr = sock.recv(4)
        if not hdr:
            break
        length = struct.unpack("<I", hdr)[0]
        if length == 0:
            break
        chunk = sock.recv(length)
        if not chunk:
            break
        full_response += chunk.decode("utf-8")
        print(f"[CLIENT] Received: {chunk.decode('utf-8')[:50]}...")

    sock.close()
    print(f"[CLIENT] Full response: {full_response[:100]}...")


def test_encrypted_mode():
    """Test with encryption (ENABLE_ENCRYPTION=1)."""
    print("\n" + "=" * 50)
    print("TEST: Encrypted Mode")
    print("=" * 50)

    client = EncryptedClient()

    message = "Hello, how are you?"
    print(f"[CLIENT] Original message: {message}")

    # Test encryption/decryption locally first
    encrypted = client.encrypt(message.encode())
    print(f"[CLIENT] Encrypted locally: {len(encrypted)} bytes")
    decrypted = client.decrypt(encrypted)
    print(f"[CLIENT] Decrypted locally: {decrypted.decode()}")

    # Now test with server
    try:
        response = client.send_message(message)
        print(f"[CLIENT] Server response: {response[:100]}...")
    except Exception as e:
        print(f"[CLIENT] Error: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--plaintext":
        test_plaintext_mode()
    else:
        test_encrypted_mode()
