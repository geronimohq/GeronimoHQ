"""
CS2 Command Center - Optional Secure Update Engine
Ed25519-signed manifest verification, HTTPS host boundary checks,
safe atomic binary swap, and rollback helper.
"""

import os
import sys
import json
import time
import hashlib
import urllib.request
import urllib.parse
import urllib.error
import subprocess
from typing import Tuple, Optional, Dict, Any
from cryptography.hazmat.primitives.asymmetric import ed25519

# Global kill switch (set to False to disable updater completely)
UPDATE_CHECK_ENABLED = True

# Production Update Manifest URL
UPDATE_MANIFEST_URL = "https://geronimohq.com/update/latest.json"

# Production Embedded Ed25519 Public Key (Hex)
EMBEDDED_PUBLIC_KEY_HEX = "ec63c9ca05f1b11a4213e55de8e8396e0072775ef5cc16911a20d40d8586e17f"

# Allowed Production Host
ALLOWED_HOST = "geronimohq.com"

# Maximum download size: 80 MB
MAX_DOWNLOAD_BYTES = 80 * 1024 * 1024

def parse_semver(v_str: str) -> Tuple[int, ...]:
    """Parse semver string into numeric tuple for strict comparison (e.g. '1.10.0' > '1.9.0')."""
    v_clean = v_str.strip().lstrip("vV")
    parts = []
    for p in v_clean.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)

def is_newer_version(candidate_ver: str, current_ver: str) -> bool:
    """Returns True strictly if candidate_ver is newer than current_ver."""
    return parse_semver(candidate_ver) > parse_semver(current_ver)

def get_canonical_bytes(ver: str, build_date: str, url: str, sha256_hex: str, size: int, notes: str) -> bytes:
    """Canonical byte representation strictly defined for signing and verification."""
    return f"{ver}\n{build_date}\n{url}\n{sha256_hex}\n{size}\n{notes}".encode("utf-8")

def verify_manifest_signature(manifest: Dict[str, Any], pub_key_hex: str = EMBEDDED_PUBLIC_KEY_HEX) -> bool:
    """Verifies that the manifest's Ed25519 signature matches the canonical byte payload."""
    try:
        sig_hex = manifest.get("signature", "")
        if not sig_hex:
            return False
        sig_bytes = bytes.fromhex(sig_hex)
        pub_bytes = bytes.fromhex(pub_key_hex)
        pub_key = ed25519.Ed25519PublicKey.from_public_bytes(pub_bytes)
        
        canonical = get_canonical_bytes(
            manifest["version"],
            manifest["build_date"],
            manifest["url"],
            manifest["sha256"],
            int(manifest["size"]),
            manifest["notes"]
        )
        pub_key.verify(sig_bytes, canonical)
        return True
    except Exception:
        return False

def _validate_url_security(url: str, allow_dev_override: bool = False) -> Tuple[bool, str]:
    """Validates HTTPS-only protocol and exact domain boundary."""
    try:
        parsed = urllib.parse.urlparse(url)
        # Frozen executable NEVER allows HTTP or non-geronimohq.com hosts
        is_frozen = getattr(sys, "frozen", False)
        
        if not is_frozen and allow_dev_override:
            if parsed.hostname in ("localhost", "127.0.0.1") and parsed.scheme in ("http", "https"):
                return True, ""

        if parsed.scheme != "https":
            return False, f"Non-HTTPS URL rejected for security: {url}"

        if parsed.hostname != ALLOWED_HOST:
            return False, f"Host boundary violation ({parsed.hostname} != {ALLOWED_HOST}): {url}"

        return True, ""
    except Exception as e:
        return False, f"Invalid URL: {e}"

class SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Custom redirect handler that enforces max 2 redirects and strict host boundary."""
    def __init__(self, allow_dev_override: bool = False):
        super().__init__()
        self.redirect_count = 0
        self.allow_dev_override = allow_dev_override

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.redirect_count += 1
        if self.redirect_count > 2:
            raise urllib.error.HTTPError(newurl, code, "Exceeded maximum allowed redirects (2)", headers, fp)
        valid, err = _validate_url_security(newurl, self.allow_dev_override)
        if not valid:
            raise urllib.error.HTTPError(newurl, 403, f"Security violation on redirect: {err}", headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def fetch_update_manifest(
    manifest_url: str = UPDATE_MANIFEST_URL,
    current_ver: str = "1.5.0",
    pub_key_hex: str = EMBEDDED_PUBLIC_KEY_HEX,
    timeout: Tuple[int, int] = (5, 10),
    allow_dev_override: bool = False
) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Checks for available update from signed manifest.
    Returns: (is_available, manifest_dict_or_None, status_or_error_msg)
    """
    if not UPDATE_CHECK_ENABLED:
        return False, None, "Update checks disabled."

    valid, err = _validate_url_security(manifest_url, allow_dev_override)
    if not valid:
        return False, None, err

    try:
        connect_to, read_to = timeout
        opener = urllib.request.build_opener(SafeRedirectHandler(allow_dev_override))
        req = urllib.request.Request(
            manifest_url,
            headers={
                "User-Agent": f"CS2-Command-Center/{current_ver}",
                "Accept": "application/json"
            }
        )
        with opener.open(req, timeout=connect_to + read_to) as resp:
            data = resp.read(MAX_DOWNLOAD_BYTES)
            
        manifest = json.loads(data.decode("utf-8"))
        
        # Verify required fields
        required_keys = ["version", "build_date", "url", "sha256", "size", "notes", "signature"]
        for k in required_keys:
            if k not in manifest:
                return False, None, f"Missing required manifest field: {k}"

        # Host boundary check on binary URL
        valid_bin_url, bin_err = _validate_url_security(manifest["url"], allow_dev_override)
        if not valid_bin_url:
            return False, None, bin_err

        # Verify signature
        if not verify_manifest_signature(manifest, pub_key_hex):
            return False, None, "Invalid cryptographic signature on update manifest."

        # Verify size limit
        if manifest["size"] > MAX_DOWNLOAD_BYTES or manifest["size"] <= 0:
            return False, None, f"Oversized update payload ({manifest['size']} bytes > 80 MB limit)."

        # Check version semantics
        if is_newer_version(manifest["version"], current_ver):
            return True, manifest, f"Update available: v{manifest['version']}"
        else:
            return False, manifest, "You have the latest version."

    except Exception as e:
        return False, None, f"Update check network error: {e}"

def download_and_verify_binary(
    manifest: Dict[str, Any],
    target_path: str,
    allow_dev_override: bool = False,
    progress_callback = None
) -> Tuple[bool, str]:
    """Downloads binary, enforces byte count, SHA-256, and MZ header."""
    valid, err = _validate_url_security(manifest["url"], allow_dev_override)
    if not valid:
        return False, err

    # Check directory writability
    target_dir = os.path.dirname(os.path.abspath(target_path))
    if not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)
    if not os.access(target_dir, os.W_OK):
        return False, f"Folder {target_dir} is not writable. Please update manually from geronimohq.com."

    temp_path = target_path + ".download"
    hasher = hashlib.sha256()
    downloaded = 0
    expected_size = int(manifest["size"])
    expected_sha256 = manifest["sha256"].upper()

    try:
        opener = urllib.request.build_opener(SafeRedirectHandler(allow_dev_override))
        req = urllib.request.Request(
            manifest["url"],
            headers={"User-Agent": "CS2-Command-Center-Updater/1.0"}
        )
        with opener.open(req, timeout=30) as resp, open(temp_path, "wb") as out_f:
            while True:
                chunk = resp.read(64 * 1024)
                if not chunk:
                    break
                downloaded += len(chunk)
                if downloaded > MAX_DOWNLOAD_BYTES or downloaded > expected_size:
                    out_f.close()
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    return False, "Downloaded file exceeded expected manifest size."
                hasher.update(chunk)
                out_f.write(chunk)
                if progress_callback:
                    progress_callback(downloaded, expected_size)

        if downloaded != expected_size:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return False, f"Download incomplete: got {downloaded} bytes, expected {expected_size}."

        calc_hash = hasher.hexdigest().upper()
        if calc_hash != expected_sha256:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return False, f"SHA-256 mismatch: got {calc_hash}, expected {expected_sha256}."

        # Verify MZ Windows PE magic header
        with open(temp_path, "rb") as f:
            magic = f.read(2)
        if magic != b"MZ":
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return False, "Downloaded file is corrupted or not a valid Windows executable (missing MZ magic)."

        # Rename to target_path (.new)
        if os.path.exists(target_path):
            os.remove(target_path)
        os.replace(temp_path, target_path)
        return True, "Download verified successfully."

    except Exception as e:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
        return False, f"Download failed: {e}"

def spawn_updater_helper_and_exit(current_exe_path: str, new_exe_path: str):
    """
    Spawns an out-of-process batch helper that:
    1. Waits for current process PID to exit.
    2. Renames current exe -> .old
    3. Moves new exe -> current exe
    4. Relaunches current exe
    5. Checks after 20s if running; if not, restores .old and relaunches .old.
    """
    pid = os.getpid()
    exe_dir = os.path.dirname(os.path.abspath(current_exe_path))
    exe_name = os.path.basename(current_exe_path)
    old_exe_path = current_exe_path + ".old"
    helper_bat = os.path.join(exe_dir, "_geronimo_updater.bat")

    script = f"""@echo off
setlocal
cd /d "{exe_dir}"
timeout /t 1 /nobreak >nul

:wait_pid
tasklist /fi "PID eq {pid}" 2>nul | find "{pid}" >nul
if not errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto wait_pid
)

if exist "{old_exe_path}" del /f /q "{old_exe_path}" >nul 2>&1
ren "{current_exe_path}" "{os.path.basename(old_exe_path)}"
ren "{new_exe_path}" "{exe_name}"

start "" "{current_exe_path}"

timeout /t 20 /nobreak >nul
tasklist /fi "IMAGENAME eq {exe_name}" 2>nul | find /i "{exe_name}" >nul
if errorlevel 1 (
    echo [ROLLBACK] New binary failed to run within 20s. Restoring backup...
    if exist "{current_exe_path}" del /f /q "{current_exe_path}" >nul 2>&1
    ren "{old_exe_path}" "{exe_name}"
    start "" "{current_exe_path}"
)

del /f /q "%~f0" >nul 2>&1
exit
"""
    with open(helper_bat, "w", encoding="utf-8") as f:
        f.write(script)

    subprocess.Popen(["cmd.exe", "/c", helper_bat], shell=True, close_fds=True)
    sys.exit(0)

def cleanup_old_update_backup(exe_path: str):
    """Removes leftover .old executable from previous update on clean launch."""
    old_exe = exe_path + ".old"
    if os.path.exists(old_exe):
        try:
            os.remove(old_exe)
        except Exception:
            pass
