"""
Discord Rich Presence (IPC) Client for CS2 Command Center
Connects directly to the Discord Desktop App via local Windows Named Pipe (\\\\.\\pipe\\discord-ipc-0)
100% VAC-Safe: Pure external local IPC pipe with zero interaction with cs2.exe memory or binaries.
"""

import os
import sys
import json
import time
import struct
import threading
import ctypes
from ctypes import wintypes
import msvcrt
from typing import Optional, Dict, Any

OP_HANDSHAKE = 0
OP_FRAME = 1
OP_CLOSE = 2
OP_PING = 3
OP_PONG = 4

def _read_pipe_bytes(pipe, num_bytes: int, timeout_sec: float = 0.8) -> bytes:
    """Reads num_bytes safely with a non-blocking timeout using Windows PeekNamedPipe."""
    if not pipe or getattr(pipe, "closed", True):
        return b""
    try:
        handle = msvcrt.get_osfhandle(pipe.fileno())
        kernel32 = ctypes.windll.kernel32
        start = time.time()
        buf = bytearray()
        while len(buf) < num_bytes and (time.time() - start < timeout_sec):
            needed = num_bytes - len(buf)
            avail = wintypes.DWORD(0)
            res = kernel32.PeekNamedPipe(handle, None, 0, None, ctypes.byref(avail), None)
            if not res:
                return bytes(buf)
            if avail.value > 0:
                chunk = pipe.read(min(needed, avail.value))
                if not chunk:
                    break
                buf.extend(chunk)
            else:
                time.sleep(0.015)
        return bytes(buf)
    except Exception:
        return b""

class DiscordRPC:
    def __init__(self, client_id: str = ""):
        self.client_id = client_id
        self.pipe = None
        self.connected = False
        self.current_activity: Optional[Dict[str, Any]] = None
        self.start_time = int(time.time())
        self._lock = threading.RLock()

    def set_client_id(self, client_id: str):
        with self._lock:
            if self.client_id != client_id:
                self.close()
                self.client_id = client_id

    def connect(self) -> bool:
        """Attempts to open connection to the local Discord desktop client."""
        if not self.client_id or not self.client_id.strip():
            return False

        with self._lock:
            if self.connected and self.pipe:
                return True

            for i in range(10):
                pipe_path = rf"\\.\pipe\discord-ipc-{i}"
                try:
                    # Open named pipe for read/write in binary unbuffered mode
                    self.pipe = open(pipe_path, "rb+", buffering=0)
                    # Handshake (opcode 0)
                    handshake = json.dumps({"v": 1, "client_id": self.client_id.strip()}).encode("utf-8")
                    self.pipe.write(struct.pack("<ii", OP_HANDSHAKE, len(handshake)) + handshake)
                    
                    # Read response header (8 bytes) with non-blocking timeout
                    hdr = _read_pipe_bytes(self.pipe, 8, timeout_sec=0.8)
                    if len(hdr) == 8:
                        op, length = struct.unpack("<ii", hdr)
                        resp_data = _read_pipe_bytes(self.pipe, length, timeout_sec=0.8).decode("utf-8", errors="replace")
                        if resp_data:
                            resp_json = json.loads(resp_data)
                            if resp_json.get("evt") == "READY":
                                self.connected = True
                                return True
                    self.pipe.close()
                    self.pipe = None
                except Exception:
                    if self.pipe:
                        try:
                            self.pipe.close()
                        except Exception:
                            pass
                        self.pipe = None

            self.connected = False
            return False

    def set_activity(
        self,
        state: str,
        details: str = "CS2 Command Center",
        start_timestamp: Optional[int] = None,
        large_image: Optional[str] = None,
        large_text: str = "Counter-Strike 2",
        buttons: Optional[list] = None
    ) -> bool:
        """Updates Discord Rich Presence activity."""
        if not self.client_id or not self.client_id.strip():
            return False

        with self._lock:
            if not self.connected:
                if not self.connect():
                    return False

            try:
                activity_payload = {
                    "state": state[:128],
                    "details": details[:128],
                    "timestamps": {
                        "start": int(start_timestamp or self.start_time)
                    }
                }
                if large_image:
                    activity_payload["assets"] = {
                        "large_image": large_image,
                        "large_text": large_text[:128]
                    }
                if buttons and isinstance(buttons, list) and len(buttons) > 0:
                    valid_b = []
                    for b in buttons[:2]:
                        if isinstance(b, dict) and "label" in b and "url" in b:
                            valid_b.append({"label": str(b["label"])[:32], "url": str(b["url"])[:512]})
                    if valid_b:
                        activity_payload["buttons"] = valid_b
                
                payload = {
                    "cmd": "SET_ACTIVITY",
                    "args": {
                        "pid": os.getpid(),
                        "activity": activity_payload
                    },
                    "nonce": str(int(time.time() * 1000))
                }

                data = json.dumps(payload).encode("utf-8")
                self.pipe.write(struct.pack("<ii", OP_FRAME, len(data)) + data)
                
                # Consume response with timeout to keep pipe synchronized
                hdr = _read_pipe_bytes(self.pipe, 8, timeout_sec=0.5)
                if len(hdr) == 8:
                    op, length = struct.unpack("<ii", hdr)
                    if length > 0:
                        _read_pipe_bytes(self.pipe, length, timeout_sec=0.5)

                self.current_activity = activity_payload
                return True
            except Exception:
                self.connected = False
                if self.pipe:
                    try:
                        self.pipe.close()
                    except Exception:
                        pass
                    self.pipe = None
                return False

    def clear_activity(self) -> bool:
        """Clears user status on Discord."""
        with self._lock:
            if not self.connected or not self.pipe:
                return True
            try:
                payload = {
                    "cmd": "SET_ACTIVITY",
                    "args": {
                        "pid": os.getpid(),
                        "activity": None
                    },
                    "nonce": str(int(time.time() * 1000))
                }
                data = json.dumps(payload).encode("utf-8")
                self.pipe.write(struct.pack("<ii", OP_FRAME, len(data)) + data)
                hdr = _read_pipe_bytes(self.pipe, 8, timeout_sec=0.5)
                if len(hdr) == 8:
                    op, length = struct.unpack("<ii", hdr)
                    if length > 0:
                        _read_pipe_bytes(self.pipe, length, timeout_sec=0.5)
                self.current_activity = None
                return True
            except Exception:
                self.connected = False
                return False

    def close(self):
        """Closes Discord IPC pipe."""
        with self._lock:
            if self.pipe:
                try:
                    self.pipe.close()
                except Exception:
                    pass
                self.pipe = None
            self.connected = False

# Global singleton helper
_global_rpc: Optional[DiscordRPC] = None

def get_discord_rpc() -> DiscordRPC:
    global _global_rpc
    if _global_rpc is None:
        _global_rpc = DiscordRPC()
    return _global_rpc
