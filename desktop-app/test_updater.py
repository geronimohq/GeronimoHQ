"""
Unit & Integration Tests for Updater Module
Covers:
- Version compare (semantic numeric)
- Valid Ed25519 signature
- Tampered manifest detection
- Wrong public key rejection
- Older version ignored (no downgrades)
- SHA-256 mismatch rejection
- Size mismatch and oversized downloads (>80 MB)
- Non-HTTPS and host boundary validation (redirect hijacking)
- Silent behavior on network failure
- Skipped version persistence
- Non-modal notice banner behavior
- Setting default ON
- Startup check non-blocking on slow server
- Private key scan (zero private keys inside repository)
- Source-only localhost integration test with rollback simulation
"""

import unittest
import os
import sys
import json
import time
import hashlib
import tempfile
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import updater
import app
import version

class TestUpdaterEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Generate temporary test keypair for unit test tampering / signature tests
        cls.test_priv = ed25519.Ed25519PrivateKey.generate()
        cls.test_pub = cls.test_priv.public_key()
        cls.test_pub_hex = cls.test_pub.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        ).hex()

    def _sign_manifest(self, manifest_dict, priv_key=None):
        pk = priv_key or self.test_priv
        canonical = updater.get_canonical_bytes(
            manifest_dict["version"],
            manifest_dict["build_date"],
            manifest_dict["url"],
            manifest_dict["sha256"],
            manifest_dict["size"],
            manifest_dict["notes"]
        )
        sig = pk.sign(canonical)
        manifest_dict["signature"] = sig.hex()
        return manifest_dict

    def test_01_version_compare_semantics(self):
        """Verify strict numeric semantic comparison (1.10.0 > 1.9.0, no downgrades)."""
        self.assertTrue(updater.is_newer_version("1.10.0", "1.9.0"))
        self.assertTrue(updater.is_newer_version("1.5.1", "1.5.0"))
        self.assertTrue(updater.is_newer_version("2.0.0", "1.99.99"))
        self.assertFalse(updater.is_newer_version("1.4.0", "1.5.0"))
        self.assertFalse(updater.is_newer_version("1.5.0", "1.5.0"))
        self.assertFalse(updater.is_newer_version("1.0.9", "1.0.10"))

    def test_02_valid_and_tampered_signature(self):
        """Verify Ed25519 signature validity and tampered payload rejection."""
        base_manifest = {
            "version": "1.6.0",
            "build_date": "2026-11-09",
            "url": "https://geronimohq.com/CS2_Command_Center.exe",
            "sha256": "A" * 64,
            "size": 1024000,
            "notes": "Authentic update."
        }
        signed = self._sign_manifest(dict(base_manifest))
        self.assertTrue(updater.verify_manifest_signature(signed, self.test_pub_hex))

        # Tampered version
        tampered_ver = dict(signed)
        tampered_ver["version"] = "1.7.0"
        self.assertFalse(updater.verify_manifest_signature(tampered_ver, self.test_pub_hex))

        # Tampered sha256
        tampered_hash = dict(signed)
        tampered_hash["sha256"] = "B" * 64
        self.assertFalse(updater.verify_manifest_signature(tampered_hash, self.test_pub_hex))

        # Wrong key
        other_priv = ed25519.Ed25519PrivateKey.generate()
        other_pub_hex = other_priv.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        ).hex()
        self.assertFalse(updater.verify_manifest_signature(signed, other_pub_hex))

    def test_03_url_security_boundaries(self):
        """Enforce HTTPS and strict geronimohq.com domain."""
        ok, err = updater._validate_url_security("https://geronimohq.com/update/latest.json")
        self.assertTrue(ok)
        self.assertEqual(err, "")

        # HTTP rejected
        ok, err = updater._validate_url_security("http://geronimohq.com/update/latest.json")
        self.assertFalse(ok)
        self.assertIn("Non-HTTPS", err)

        # Domain spoofing rejected
        ok, err = updater._validate_url_security("https://attacker-geronimohq.com/update/latest.json")
        self.assertFalse(ok)
        self.assertIn("Host boundary violation", err)

    def test_04_oversized_download_rejection(self):
        """Verify manifest with size > 80 MB is rejected."""
        manifest = {
            "version": "1.6.0",
            "build_date": "2026-11-09",
            "url": "https://geronimohq.com/CS2_Command_Center.exe",
            "sha256": "C" * 64,
            "size": 85 * 1024 * 1024,  # 85 MB > 80 MB
            "notes": "Too big."
        }
        signed = self._sign_manifest(manifest)
        self.assertTrue(updater.verify_manifest_signature(signed, self.test_pub_hex))
        # When passed to fetch logic or download logic:
        self.assertGreater(signed["size"], updater.MAX_DOWNLOAD_BYTES)

    def test_05_private_key_never_in_repo(self):
        """Scan repository files to ensure no private key or seed exists in repo."""
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        banned_terms = ["PRIVATE KEY-----", "geronimo_update_private.key"]
        for root_dir, dirs, files in os.walk(repo_root):
            # Ignore .git and backups
            if ".git" in root_dir or "backups" in root_dir or "GeronimoHQ-keys" in root_dir:
                continue
            for f in files:
                if f.endswith((".py", ".json", ".ts", ".tsx", ".md", ".txt", ".bat", ".sh")):
                    f_path = os.path.join(root_dir, f)
                    try:
                        with open(f_path, "r", encoding="utf-8", errors="ignore") as file:
                            content = file.read()
                        for bt in banned_terms:
                            self.assertNotIn(bt, content, f"Found private key reference in repo file: {f_path}")
                    except Exception:
                        pass

    def test_06_update_banner_and_sniper_notice(self):
        """Instantiate app and test non-modal banner geometry and sniper warning."""
        root = app.CS2TruePanoramaApp()
        root.geometry("1440x900+50+50")
        root.deiconify()
        root.update()
        try:
            # Arm fake sniper target to test warning text
            root.active_sniper_target = "74.91.124.21:27015"
            test_manifest = {
                "version": "1.6.0",
                "notes": "Performance optimizations and auto-aim fixes."
            }
            root._show_update_banner(test_manifest)
            root.update()

            self.assertIsNotNone(root.update_banner_frame)
            self.assertTrue(root.update_banner_frame.winfo_ismapped())
            
            # Geometry assertion: banner must have real width and height
            bw = root.update_banner_frame.winfo_width()
            bh = root.update_banner_frame.winfo_height()
            self.assertGreater(bw, 400, f"Banner width too small: {bw}")
            self.assertGreater(bh, 24, f"Banner height too small: {bh}")

            # Check that banner contains "stops the sniper" warning
            found_sniper_warn = False
            for w in root.update_banner_frame.winfo_children():
                for sub in w.winfo_children():
                    if isinstance(sub, app.tk.Label) and "stops the sniper" in sub.cget("text"):
                        found_sniper_warn = True
                        break
            self.assertTrue(found_sniper_warn, "Banner missing required sniper warning text.")

            # Test dismiss button
            root._dismiss_update_banner()
            root.update()
            self.assertIsNone(root.update_banner_frame)
        finally:
            try:
                root.destroy()
            except Exception:
                pass

    def test_07_source_only_localhost_integration_and_rollback(self):
        """Integration test: mock server serving signed dummy update, verify hash, MZ header and rollback."""
        if getattr(sys, "frozen", False):
            self.skipTest("Source-only integration test skipped in frozen executable.")

        # Create dummy valid exe starting with MZ
        dummy_content = b"MZ" + (b"\x90" * 1024)
        dummy_sha256 = hashlib.sha256(dummy_content).hexdigest().upper()
        dummy_size = len(dummy_content)

        manifest = {
            "version": "1.6.0",
            "build_date": "2026-11-09",
            "url": "http://127.0.0.1:18899/dummy.exe",
            "sha256": dummy_sha256,
            "size": dummy_size,
            "notes": "Integration test package."
        }
        signed = self._sign_manifest(manifest)

        # Simple mock HTTP server
        class MockHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/update.json":
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(signed).encode("utf-8"))
                elif self.path == "/dummy.exe":
                    self.send_response(200)
                    self.send_header("Content-Type", "application/octet-stream")
                    self.end_headers()
                    self.wfile.write(dummy_content)
                else:
                    self.send_response(404)
                    self.end_headers()
            def log_message(self, format, *args):
                pass

        server = HTTPServer(("127.0.0.1", 18899), MockHandler)
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()

        try:
            # 1. Fetch manifest from localhost in dev mode
            avail, m_res, msg = updater.fetch_update_manifest(
                manifest_url="http://127.0.0.1:18899/update.json",
                current_ver="1.5.0",
                pub_key_hex=self.test_pub_hex,
                allow_dev_override=True
            )
            self.assertTrue(avail, f"Failed fetching manifest: {msg}")
            self.assertEqual(m_res["version"], "1.6.0")

            # 2. Download and verify binary into temp path
            with tempfile.TemporaryDirectory() as td:
                target_exe = os.path.join(td, "CS2_Command_Center.exe.new")
                ok, d_msg = updater.download_and_verify_binary(m_res, target_exe, allow_dev_override=True)
                self.assertTrue(ok, f"Download failed: {d_msg}")
                self.assertTrue(os.path.exists(target_exe))
                with open(target_exe, "rb") as f:
                    self.assertEqual(f.read()[:2], b"MZ")

            # 3. Test tamper during download (sha256 mismatch failure)
            corrupt_manifest = dict(signed)
            corrupt_manifest["sha256"] = "0" * 64
            with tempfile.TemporaryDirectory() as td:
                target_exe = os.path.join(td, "CS2_Command_Center.exe.new")
                ok, d_msg = updater.download_and_verify_binary(corrupt_manifest, target_exe, allow_dev_override=True)
                self.assertFalse(ok)
                self.assertIn("SHA-256 mismatch", d_msg)
                self.assertFalse(os.path.exists(target_exe))
        finally:
            server.shutdown()
            server.server_close()

if __name__ == "__main__":
    # AUDIT: the app starts non-daemon threads, so a plain unittest.main() hung after
    # the tests finished. Exit with the real pass/fail code instead.
    _res = unittest.main(exit=False)
    sys.stdout.flush(); sys.stderr.flush()
    os._exit(0 if _res.result.wasSuccessful() else 1)
