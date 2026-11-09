"""
GeronimoHQ Update Key Generation Tool
Generates an Ed25519 signing keypair for CS2 Command Center updates.
Stores private key OUTSIDE the repository (default: %USERPROFILE%\\Documents\\GeronimoHQ-keys\\).
The private key must never be committed or printed into build logs.
"""

import os
import sys
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

def generate_keys():
    user_docs = os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), "Documents")
    key_dir = os.path.join(user_docs, "GeronimoHQ-keys")
    os.makedirs(key_dir, exist_ok=True)
    
    priv_path = os.path.join(key_dir, "geronimo_update_private.key")
    pub_path = os.path.join(key_dir, "geronimo_update_public.key")

    if os.path.exists(priv_path):
        print(f"[KEYS] Existing private key found at: {priv_path}")
        with open(priv_path, "rb") as f:
            priv_bytes = f.read()
        priv_key = ed25519.Ed25519PrivateKey.from_private_bytes(priv_bytes)
    else:
        priv_key = ed25519.Ed25519PrivateKey.generate()
        priv_bytes = priv_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        with open(priv_path, "wb") as f:
            f.write(priv_bytes)
        print(f"[KEYS] Generated new Ed25519 private key at: {priv_path}")
        print("=" * 70)
        print("WARNING: Back this up; if lost, installed apps can't accept updates; if leaked, anyone can push malware.")
        print("=" * 70)

    pub_key = priv_key.public_key()
    pub_bytes = pub_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    with open(pub_path, "wb") as f:
        f.write(pub_bytes)
        
    pub_hex = pub_bytes.hex()
    print(f"[KEYS] Public key saved to: {pub_path}")
    print(f"[KEYS] Embedded Public Key HEX: {pub_hex}")
    return priv_path, pub_hex

if __name__ == "__main__":
    generate_keys()
