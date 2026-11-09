"""
GeronimoHQ Update Manifest Generator Tool
Signs application binary details with Ed25519 private key outside the repository.
Outputs canonical signed manifest to public/update/latest.json.
Never runs in CI.
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import ed25519

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "desktop-app"))
import version

def get_canonical_bytes(ver: str, build_date: str, url: str, sha256_hex: str, size: int, notes: str) -> bytes:
    """Canonical byte representation strictly defined for signing and verification."""
    return f"{ver}\n{build_date}\n{url}\n{sha256_hex}\n{size}\n{notes}".encode("utf-8")

def make_manifest(exe_path=None, notes=None):
    if not exe_path:
        # Default to scratch/dist/CS2_Command_Center.exe or dist/CS2_Command_Center.exe
        candidates = [
            os.path.join(REPO_ROOT, "scratch", "dist", "CS2_Command_Center.exe"),
            os.path.join(REPO_ROOT, "dist", "CS2_Command_Center.exe")
        ]
        exe_path = next((c for c in candidates if os.path.exists(c)), None)

    if not exe_path or not os.path.exists(exe_path):
        raise FileNotFoundError(f"Binary not found: {exe_path}")

    # Read binary bytes
    with open(exe_path, "rb") as f:
        exe_bytes = f.read()

    # Basic PE validity check
    if not exe_bytes.startswith(b"MZ"):
        raise ValueError("Binary is not a valid Windows PE executable (missing MZ magic header).")

    app_ver = version.APP_VERSION
    build_date = version.BUILD_DATE or datetime.now().strftime("%Y-%m-%d")
    url = "https://geronimohq.com/CS2_Command_Center.exe"
    sha256_hex = hashlib.sha256(exe_bytes).hexdigest().upper()
    size = len(exe_bytes)
    if not notes:
        notes = f"CS2 Command Center v{app_ver} update with improved performance, updater, and fixes."
    if len(notes) > 300:
        notes = notes[:297] + "..."

    # Locate private key
    key_path = os.environ.get("GERONIMO_UPDATE_PRIVATE_KEY")
    if not key_path:
        user_docs = os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), "Documents")
        key_path = os.path.join(user_docs, "GeronimoHQ-keys", "geronimo_update_private.key")

    if not os.path.exists(key_path):
        raise FileNotFoundError(f"Ed25519 private key not found at: {key_path}. Run tools/generate_update_keys.py first.")

    with open(key_path, "rb") as f:
        priv_bytes = f.read()

    priv_key = ed25519.Ed25519PrivateKey.from_private_bytes(priv_bytes)
    canonical = get_canonical_bytes(app_ver, build_date, url, sha256_hex, size, notes)
    sig_bytes = priv_key.sign(canonical)
    sig_hex = sig_bytes.hex()

    manifest_data = {
        "version": app_ver,
        "build_date": build_date,
        "url": url,
        "sha256": sha256_hex,
        "size": size,
        "notes": notes,
        "signature": sig_hex
    }

    out_dir = os.path.join(REPO_ROOT, "public", "update")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "latest.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    print(f"[MANIFEST] Generated and signed manifest at: {out_file}")
    print(f"  Version: {app_ver} ({build_date})")
    print(f"  Size: {size} bytes ({size / (1024*1024):.2f} MB)")
    print(f"  SHA-256: {sha256_hex}")
    print(f"  Signature: {sig_hex[:16]}...{sig_hex[-16:]}")
    return out_file

if __name__ == "__main__":
    make_manifest()
