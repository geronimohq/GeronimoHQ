"""AUDIT: import this BEFORE `import app` in every test that creates the app.

It redirects the app's settings file to a temp folder and stubs Windows startup
(registry Run key + Task Scheduler), so tests never change the owner's real
%APPDATA%\\CS2CommandCenter\\command_center_config.json or the registry.
(Found in Phase 3: exit_application() saves the last page, and older tests used
the real config.)
"""
import atexit
import os
import shutil
import tempfile

import app_config

TEMP_DIR = tempfile.mkdtemp(prefix="cs2cc_test_")
REAL_CONFIG_FILE = app_config.CONFIG_FILE
app_config.CONFIG_FILE = os.path.join(TEMP_DIR, "command_center_config.json")
app_config.set_windows_startup = lambda enabled, minimized=False: True
app_config.is_windows_startup_enabled = lambda: False
app_config.is_windows_startup_minimized = lambda: False
atexit.register(shutil.rmtree, TEMP_DIR, True)
