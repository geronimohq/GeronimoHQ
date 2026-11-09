"""
AUDIT Phase 2 - tests for the owner's 9 known bugs.

Safe to run on the owner's PC:
- the app's config file is redirected to a temp folder (real settings untouched),
- Windows startup (registry Run key + schtasks) is stubbed: nothing is written,
- no message boxes are shown (stubbed),
- autoexec tests use a temp cfg folder, never the real CS2 folder.
"""
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
from unittest import mock

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")  # ● and ≤ in printed evidence
    except Exception:
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import app_config  # noqa: E402

_TMP = tempfile.mkdtemp(prefix="cs2cc_p2_")
_REAL_CONFIG_FILE = app_config.CONFIG_FILE
app_config.CONFIG_FILE = os.path.join(_TMP, "command_center_config.json")

# Fake Windows startup state (instead of the registry / Task Scheduler)
_FAKE_STARTUP = {"enabled": False, "minimized": False, "calls": []}


def _fake_set_startup(enabled, minimized=False):
    _FAKE_STARTUP["calls"].append((enabled, minimized))
    _FAKE_STARTUP["enabled"], _FAKE_STARTUP["minimized"] = bool(enabled), bool(minimized)
    return True


app_config.set_windows_startup = _fake_set_startup
app_config.is_windows_startup_enabled = lambda: _FAKE_STARTUP["enabled"]
app_config.is_windows_startup_minimized = lambda: _FAKE_STARTUP["minimized"]

import app  # noqa: E402  (imported after the redirects above)
import core_logic  # noqa: E402


def _quiet_boxes():
    return mock.patch.multiple(app.messagebox, showinfo=mock.DEFAULT, showwarning=mock.DEFAULT,
                               showerror=mock.DEFAULT, askyesno=mock.DEFAULT)


class AppTestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert app_config.CONFIG_FILE.startswith(_TMP), "config must be redirected"
        cls.root = app.CS2TruePanoramaApp()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        try:
            with mock.patch.object(app.os, "_exit", lambda code=0: None):
                cls.root.exit_application()
        except Exception:
            pass


# --------------------------------------------------------------------------- #6
class Bug6SettingsPersist(AppTestBase):
    NON_DEFAULT = {
        "start_with_windows": True,
        "start_minimized": True,
        "minimize_to_tray_on_close": False,
        "open_on_page": "Last used page",
        "sniper_sound_enabled": False,
        "server_refresh_speed": "Eco (15s)",
        "discord_rpc_enabled": False,       # P3-01: Settings tick = the real Discord switch
        "check_updates_on_startup": False,   # the owner's reported bug
    }

    def _open(self):
        self.root.open_settings_dialog()
        return self.root._settings_dialog_vars

    def test_dialog_covers_every_setting(self):
        with _quiet_boxes():
            v = self._open()
            self.assertEqual(set(v), set(app_config.SETTINGS_DEFAULTS))
            self.root._settings_dialog_vars["start_with_windows"].set(False)

    def test_round_trip_every_setting(self):
        self.root.config["presence_secret"] = "keep-me"
        with _quiet_boxes() as boxes:
            v = self._open()
            for k, val in self.NON_DEFAULT.items():
                v[k].set(val)
            self.assertTrue(self.root._settings_dialog_save())
            boxes["showinfo"].assert_not_called()  # shown 50 ms later via after()
        # 1) on disk
        with open(app_config.CONFIG_FILE, encoding="utf-8") as f:
            disk = json.load(f)
        for k, val in self.NON_DEFAULT.items():
            self.assertEqual(disk[k], val, f"{k} not written to disk")
        self.assertEqual(disk["presence_secret"], "keep-me")
        # 2) "close and reopen the app": a fresh load_config()
        fresh = app_config.load_config()
        for k, val in self.NON_DEFAULT.items():
            self.assertEqual(fresh[k], val, f"{k} lost after reload")
        # 3) reopen the dialog: ticks are shown as saved
        self.root.config = fresh
        with _quiet_boxes():
            v2 = self._open()
            for k, val in self.NON_DEFAULT.items():
                self.assertEqual(v2[k].get(), val, f"{k} not shown after reopen")
            self.root._settings_dialog_save()
        print("\n[#6] round trip OK for:", ", ".join(sorted(self.NON_DEFAULT)))

    def test_startup_entry_only_touched_when_changed(self):
        with _quiet_boxes():
            self._open()
            self.root._settings_dialog_save()
            n = len(_FAKE_STARTUP["calls"])
            self._open()
            self.root._settings_dialog_save()   # nothing changed
            self.assertEqual(len(_FAKE_STARTUP["calls"]), n)

    def test_failed_write_is_reported_not_called_saved(self):
        with _quiet_boxes() as boxes, mock.patch.object(app_config, "save_config", return_value=False):
            self._open()
            self.assertFalse(self.root._settings_dialog_save())
            boxes["showerror"].assert_called_once()
        # dialog stays open so the user can retry; close it
        for w in self.root.winfo_children():
            if isinstance(w, app.tk.Toplevel):
                w.destroy()

    def test_reset_keeps_secret_and_client_id(self):
        cfg = {"presence_secret": "s", "discord_client_id": "123", "check_updates_on_startup": False}
        app_config.reset_settings(cfg)
        self.assertEqual(cfg["presence_secret"], "s")
        self.assertEqual(cfg["discord_client_id"], "123")
        self.assertTrue(cfg["check_updates_on_startup"])


# --------------------------------------------------------------------------- #1
class Bug1AutoexecStatus(AppTestBase):
    def setUp(self):
        self.cfg = tempfile.mkdtemp(prefix="cfg_", dir=_TMP)
        self._old = dict(self.root.paths)
        self.root.paths["cfg_dir"] = self.cfg
        self.root.paths["autoexec_cfg"] = None   # like a PC where autoexec.cfg did not exist at start
        self.root.config.pop("autoexec_last_app_save", None)
        self.auto = os.path.join(self.cfg, "autoexec.cfg")

    def tearDown(self):
        self.root.paths.clear(); self.root.paths.update(self._old)

    def dash_text(self):
        self.root._select_nav("DASHBOARD")
        self.root.update_idletasks()
        return self.root.lbl_dash_autoexec_status.cget("text")

    def test_user_file_then_app_ze_write_updates_without_restart(self):
        with open(self.auto, "w", encoding="utf-8") as f:
            f.write('bind "mouse4" "+jump"\n')
        self.assertIn("no section written by this app", self.dash_text())
        res = core_logic.apply_ze_visual_and_hud_customizer(self.cfg, {"duck_key": "F7", "voice_mute_key": "F8"})
        self.assertTrue(res["success"])
        self.root._refresh_autoexec_preview()            # what every writer calls afterwards
        self.assertIn("includes settings written by this app",
                      self.root.lbl_dash_autoexec_status.cget("text"))

    def test_engine_tweaks_block_is_recognised(self):
        ok, _ = core_logic.install_autoexec(self.cfg)
        self.assertTrue(ok)
        self.assertIn("includes settings written by this app", self.dash_text())

    def test_in_app_editor_save_then_outside_edit(self):
        with open(self.auto, "w", encoding="utf-8") as f:
            f.write("// mine\n")
        self.root._select_nav("AUTOEXEC")
        self.root.update_idletasks()
        self.root.is_autoexec_editing = True
        self.root.txt_box.config(state="normal")
        self.root.txt_box.delete("1.0", "end")
        self.root.txt_box.insert("1.0", 'fps_max "300"\n')
        with _quiet_boxes():
            self.root._save_autoexec_manual()
        self.assertIn("last saved in this app", self.dash_text())
        # Someone edits the file outside the app -> on window focus the label changes
        with open(self.auto, "a", encoding="utf-8") as f:
            f.write("// edited in Notepad\n")
        ev = mock.Mock(widget=self.root)
        self.root._on_app_focus_in(ev)
        self.assertIn("no section written by this app", self.root.lbl_dash_autoexec_status.cget("text"))

    def test_missing_file(self):
        self.assertIn("not found", self.dash_text())


# --------------------------------------------------------------------------- #3
import server_browser  # noqa: E402


class Bug3StatusBar(AppTestBase):
    def test_sniper_states(self):
        f = server_browser.sniper_status_bar
        self.assertEqual(f({"is_active": False, "last_fired_time": 0})[1], "idle")
        t, s = f({"is_active": True, "target_name": "GFL ZE", "target_max_players": 63})
        self.assertEqual(s, "armed"); self.assertIn("GFL ZE", t); self.assertIn("≤ 63", t)
        self.assertEqual(f({"is_active": False, "last_fired_time": 100.0}, now=101.0)[1], "triggered")
        t, s = f({"is_active": False, "last_fired_time": 100.0}, now=105.2)
        self.assertEqual(s, "cooldown"); self.assertIn("5s", t)
        self.assertEqual(f({"is_active": False, "last_fired_time": 100.0}, now=111.0)[1], "idle")

    def test_label_follows_real_sniper_even_when_withdrawn(self):
        sn = self.root.sniper
        self.root.withdraw()  # like "minimized to tray"
        with mock.patch.object(sn, "get_status", return_value={"is_active": True, "target_name": "Mapeadores ZE", "target_max_players": 0}):
            self.root._status_bar_tick()
            self.assertIn("ARMED — Mapeadores ZE", self.root.status_sniper_lbl.cget("text"))
        with mock.patch.object(sn, "get_status", return_value={"is_active": False, "last_fired_time": 0}):
            self.root._status_bar_tick()
            self.assertEqual(self.root.status_sniper_lbl.cget("text"), "● SLOT SNIPER: IDLE")

    def test_dns_label_is_real(self):
        f = core_logic.dns_status_bar
        name0 = core_logic.DNS_PROVIDERS[0]["name"]
        self.assertEqual(f(f"{name0} [1.1.1.1, 1.0.0.1]"), (f"● DNS: {name0}", "provider"))
        self.assertEqual(f("Automatic DHCP (192.168.1.1)")[1], "automatic")
        self.assertEqual(f("Custom Static [10.0.0.53, 10.0.0.54]"), ("● DNS: custom (10.0.0.53)", "custom"))
        self.root._apply_dns_status_bar("Automatic (ISP / DHCP)")
        self.assertNotIn("ACTIVE", self.root.status_dns_lbl.cget("text"))

    def test_no_hard_coded_status_text_left(self):
        with open(os.path.join(HERE, "app.py"), encoding="utf-8") as fh:
            src = fh.read()
        self.assertFalse('"● GAMING DNS: ACTIVE"' in src)
        self.assertFalse('text="● SLOT SNIPER: IDLE", font' in src and "_status_bar_tick" not in src)


# --------------------------------------------------------------------------- #4
import discord_rpc  # noqa: E402


class _FakeRpc:
    """Stands in for the Discord pipe: nothing is sent anywhere."""
    def __init__(self, snap=None):
        self.snap, self.connected, self.client_id = snap, bool(snap), "x"
    def broadcast_snapshot(self):
        return dict(self.snap) if self.snap else None
    def set_client_id(self, c): pass
    def clear_activity(self): self.snap = None; return True
    def close(self): self.snap = None; self.connected = False
    def connect(self): return False
    def set_activity(self, **k): return False


class Bug4DiscordPreview(AppTestBase):
    def setUp(self):
        self._real = self.root.discord_rpc

    def tearDown(self):
        self.root.discord_rpc = self._real

    def _texts(self):
        r = self.root
        return {"status": r.preview_status_lbl.cget("text"), "dormant": r.preview_dormant_title.cget("text"),
                "details": r.discord_preview_details.get(), "btn1": r.discord_preview_btn1.get(),
                "active_shown": bool(r.preview_active.winfo_ismapped())}

    def test_first_open_is_neutral_then_checks_automatically(self):
        self.root.discord_rpc = _FakeRpc(None)

        class _SyncThread:  # run the worker inline: tests have no Tk mainloop for after() from threads
            def __init__(self, target=None, daemon=None, **k): self.t = target
            def start(self): self.t()

        with mock.patch.object(core_logic, "is_cs2_running", return_value=False), _quiet_boxes() as boxes, \
                mock.patch.object(app.threading, "Thread", _SyncThread):
            self.root._select_nav("DISCORD")
            self.root.update()
            t = self._texts()
            self.assertIn("Checking", t["status"])          # neutral, not "Online"
            self.assertNotIn("Main Menu", t["details"])
            self.assertNotIn("74.91.124.21", t["btn1"])
            # the automatic check runs (after 150 ms, in a thread) -> Standby, no pop-up
            import time as _t
            deadline = _t.time() + 5
            while "Checking" in self.root.preview_status_lbl.cget("text") and _t.time() < deadline:
                self.root.update(); _t.sleep(0.05)
            boxes["showwarning"].assert_not_called()
        t = self._texts()
        self.assertIn("Standby", t["status"])
        self.assertFalse(t["active_shown"])
        print("\n[#4] after auto-check with CS2 closed:", t)

    def test_preview_ignores_placeholder_text_when_nothing_sent(self):
        self.root.discord_rpc = _FakeRpc(None)
        self.root._discord_preview_checked = True
        self.root._update_discord_preview_labels("In Main Menu • Standby", "CS2 Command Center", "🎮 Server: 74.91.124.21:27015")
        t = self._texts()
        self.assertIn("Standby", t["status"]); self.assertEqual(t["details"], ""); self.assertFalse(t["active_shown"])

    def test_preview_shows_exactly_what_was_sent(self):
        sent = {"details": "GFL Clan Zombie Escape 24/7", "state": "Map: ze_x (60/64 Players)",
                "timestamps": {"start": 1}, "buttons": [{"label": "Join", "url": "https://geronimohq.com/connect/"}]}
        self.root.discord_rpc = _FakeRpc(sent)
        self.root._discord_preview_checked = True
        self.root._select_nav("DISCORD"); self.root.update_idletasks()
        self.root._update_discord_preview_labels("ignored", "ignored")
        t = self._texts()
        self.assertEqual(t["details"], sent["details"]); self.assertEqual(t["btn1"], "Join")
        self.assertIn("In-Game", t["status"])
        self.assertEqual(self.root.preview_status_lbl.cget("fg"), "#57d98a")

    def test_rpc_snapshot_cleared_on_close(self):
        rpc = discord_rpc.DiscordRPC("1")
        rpc.connected, rpc.current_activity = True, {"details": "x"}
        self.assertIsNotNone(rpc.broadcast_snapshot())
        rpc.close()
        self.assertIsNone(rpc.broadcast_snapshot())


# --------------------------------------------------------------------------- #2
import ast  # noqa: E402
import subprocess  # noqa: E402

ROOT = os.path.dirname(HERE)
FIXTURE_ROWS = [
    {"id": "gfl", "host": "74.91.124.21", "port": 27015, "online": True, "curr_players": 60, "bots": 2, "max_players": 64, "sampled_at": 1000},
    {"id": "rss", "host": "14.5.33.30", "port": 27015, "online": True, "curr_players": 10, "bots": 0, "max_players": 64, "sampled_at": 1000},
    {"id": "rss_alias", "host": "14.5.33.30", "port": 27015, "online": True, "curr_players": 10, "bots": 0, "max_players": 64, "sampled_at": 1000},
    {"id": "old", "host": "1.2.3.4", "port": 27015, "online": True, "curr_players": 30, "bots": 0, "max_players": 64, "sampled_at": 800},
    {"id": "down", "host": "5.6.7.8", "port": 27015, "online": False, "curr_players": 0, "max_players": 0, "sampled_at": 1000},
    {"id": "nobots", "host": "9.9.9.9", "port": 27016, "online": True, "curr_players": 5, "max_players": 32, "sampled_at": 1000},
]


def _func_source(path, name):
    with open(path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.dump(node)
    raise AssertionError(f"{name} not found in {path}")


class Bug2Totals(AppTestBase):
    def test_rule(self):
        t = server_browser.compute_player_totals(FIXTURE_ROWS, now=1000)
        self.assertEqual(t["humans"], 58 + 10 + 5)          # bots removed, alias once, stale/offline out
        self.assertEqual(t["online_servers"], 3)
        self.assertEqual(t["total_servers"], 5)              # alias dropped
        self.assertEqual(t["duplicates_dropped"], 1)
        self.assertEqual(t["stale_servers"], 1)
        self.assertEqual(t["bots_unknown_servers"], 1)

    def test_backend_and_ci_script_use_identical_function(self):
        ref = _func_source(os.path.join(HERE, "server_browser.py"), "compute_player_totals")
        for p in (os.path.join(ROOT, "backend", "api.py"), os.path.join(ROOT, "scripts", "fetch_live_servers.py")):
            self.assertEqual(_func_source(p, "compute_player_totals"), ref, f"{p} differs")

    def test_website_typescript_gives_same_numbers(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node not installed")
        ts = os.path.join(ROOT, "src", "utils", "playerTotals.ts").replace("\\", "/")
        js = ("import {computePlayerTotals} from 'file:///" + ts + "';"
              "const rows=JSON.parse(process.argv[1]);"
              "console.log(JSON.stringify(computePlayerTotals(rows,1000)));")
        out = subprocess.run([node, "--input-type=module", "-e", js, json.dumps(FIXTURE_ROWS)],
                             capture_output=True, text=True, timeout=60)
        self.assertEqual(out.returncode, 0, out.stderr)
        web = json.loads(out.stdout.strip().splitlines()[-1])
        py = server_browser.compute_player_totals(FIXTURE_ROWS, now=1000)
        for k in ("humans", "bots", "online_servers", "total_servers", "stale_servers", "bots_unknown_servers", "duplicates_dropped"):
            self.assertEqual(web[k], py[k], k)

    def test_shared_totals_sources(self):
        server_browser._TOTALS_CACHE.update(at=0, totals=None, source=None)
        new_backend = {"timestamp": 1000, "servers": {}, "totals": {"humans": 7, "bots": 1, "online_servers": 2, "total_servers": 41,
                       "stale_servers": 0, "bots_unknown_servers": 0, "duplicates_dropped": 0, "max_age_s": 90}}
        t = server_browser.get_shared_totals(now=1000, fetch_backend=lambda: new_backend, query_direct=lambda: [])
        self.assertEqual((t["humans"], t["source"]), (7, "backend"))
        # cached for 60 s: a second call does not hit the network
        t2 = server_browser.get_shared_totals(now=1030, fetch_backend=lambda: 1 / 0, query_direct=lambda: 1 / 0)
        self.assertEqual(t2["humans"], 7)
        # old backend (no totals, no bots): same rule, flagged
        server_browser._TOTALS_CACHE.update(at=0, totals=None)
        old = {"timestamp": 1000, "servers": {"gfl": {"host": "74.91.124.21", "port": 27015, "online": True, "curr_players": 59, "max_players": 64}}}
        t3 = server_browser.get_shared_totals(now=1000, fetch_backend=lambda: old, query_direct=lambda: [])
        self.assertEqual((t3["humans"], t3["bots_unknown_servers"]), (59, 1))
        # backend down -> direct A2S fallback
        server_browser._TOTALS_CACHE.update(at=0, totals=None)
        t4 = server_browser.get_shared_totals(now=1000, fetch_backend=lambda: None, query_direct=lambda: FIXTURE_ROWS)
        self.assertEqual((t4["humans"], t4["source"]), (73, "direct"))
        server_browser._TOTALS_CACHE.update(at=0, totals=None)

    def test_dashboard_and_servers_page_show_the_same_numbers(self):
        self.root._select_nav("SERVERS"); self.root._select_nav("DASHBOARD"); self.root.update_idletasks()
        t = server_browser.compute_player_totals(FIXTURE_ROWS, now=1000); t["source"] = "backend"
        self.root._apply_ze_totals(t)
        self.assertEqual(self.root.dash_ze_players_lbl.cget("text"), "73 players in-game (bots unknown)")
        self.assertEqual(self.root.lbl_srv_players.cget("text"), "👥 73 PLAYERS IN-GAME (BOTS UNKNOWN)")
        self.assertEqual(self.root.dash_ze_nodes_lbl.cget("text"), "3 / 5 servers online")
        self.assertEqual(self.root.lbl_srv_nodes.cget("text"), "📡 3 / 5 SERVERS ONLINE")

    def test_no_hard_coded_totals_left(self):
        with open(os.path.join(HERE, "app.py"), encoding="utf-8") as fh:
            src = fh.read()
        for bad in ("646 players", "646 PLAYERS", "34 / 41"):
            self.assertFalse(bad in src, bad)
        with open(os.path.join(ROOT, "src", "components", "ServerRadarPreview.tsx"), encoding="utf-8") as fh:
            self.assertFalse("online_servers ?? 33" in fh.read())


# --------------------------------------------------------------------------- #5
class Bug5Geo(unittest.TestCase):
    SAMPLE = {"code": 0, "data": {"contain_countries": 37, "total_count": 64, "continents": [
        {"count": 15, "name": "Europe"}, {"count": 10, "name": "North America"}, {"count": 7, "name": "Asia"},
        {"count": 3, "name": "South America"}, {"count": 2, "name": "Africa"}]}}

    def test_estimate_label_and_sample_size(self):
        g = server_browser.parse_zegraph_continents(self.SAMPLE)
        txt = server_browser.get_server_demographics_text("Chicago, US", 64, dict(g, age_s=0))
        self.assertIn("estimate, 37 of 64 players", txt)
        self.assertIn("Europe 41%", txt)
        print("\n[#5] GFL geo line:", txt)

    def test_zero_players_and_no_data(self):
        self.assertEqual(server_browser.get_server_demographics_text("Chicago, US", 0), "🌐 GEO: server empty")
        self.assertIn("no measured data", server_browser.get_server_demographics_text("Europe (Spain)", 20))

    def test_no_invented_percentages_left(self):
        with open(os.path.join(HERE, "server_browser.py"), encoding="utf-8") as fh:
            src = fh.read()
        for bad in ("US 54%", "FR 44%", "CN 88%", "INTL 65%"):
            self.assertFalse(bad in src, bad)

    def test_offline_fallback_uses_last_value_with_age(self):
        server_browser._GEO_CACHE.update(at=1000.0, data=server_browser.parse_zegraph_continents(self.SAMPLE))
        with mock.patch.object(server_browser.urllib.request, "urlopen", side_effect=OSError("offline")):
            g = server_browser.fetch_gfl_continents(now=1000.0 + 900)
        self.assertEqual(g["sample"], 37)
        self.assertGreaterEqual(g["age_s"], 900)
        self.assertIn("15 min old", server_browser.get_server_demographics_text("x", 5, g))
        server_browser._GEO_CACHE.update(at=0.0, data=None)

    def test_geo_never_takes_player_names(self):
        import inspect
        sig = inspect.signature(server_browser.get_server_demographics_text)
        self.assertEqual(list(sig.parameters), ["region_name", "total_players", "geo"])


# --------------------------------------------------------------------------- #7
USER_FACING = [
    os.path.join(HERE, f) for f in ("app.py", "core_logic.py", "discord_rpc.py", "cs2_gsi.py", "server_browser.py")
] + [os.path.join(ROOT, *p) for p in (
    ("src", "App.tsx"), ("src", "components", "CS2CommandCenterPreview.tsx"),
    ("src", "components", "CS2AutoexecGeneratorSection.tsx"), ("src", "components", "ServerRadarPreview.tsx"),
    ("public", "connect", "index.html"), ("index.html",), ("README.md",))]
# Clearly labelled parody components ("PARODY MEME // NO REAL PRIZE") are out of scope.
BANNED = [r"vac[- ]?safe", r"sub-tick verified", r"zero runtime overhead", r"100% clean",
          r"safety guarantee", r"100% verified", r"engine verified", r"100% consistent",
          r"\bguarantee[sd]?\b(?!.*(grab release|execution|zero ui|zero flicker))"]


class Bug7Claims(unittest.TestCase):
    def test_no_marketing_claims_left(self):
        hits = []
        for p in USER_FACING:
            with open(p, encoding="utf-8") as fh:
                for n, line in enumerate(fh, 1):
                    low = line.lower()
                    if "audit p2-#7" in low:      # the audit comments that name the old text
                        continue
                    for pat in BANNED:
                        if re.search(pat, low):
                            hits.append(f"{os.path.relpath(p, ROOT)}:{n}: {line.strip()[:90]}")
        self.assertEqual(hits, [], "\n".join(hits))

    def test_plain_fact_and_disclaimer_present(self):
        with open(os.path.join(HERE, "app.py"), encoding="utf-8") as fh:
            src = fh.read()
        self.assertIn("Does not read or modify CS2 memory.", src)
        self.assertIn("not affiliated with Valve", src)


# --------------------------------------------------------------------------- #9
class Bug9Autoexec(unittest.TestCase):
    def setUp(self):
        self.cfg = tempfile.mkdtemp(prefix="cfg9_", dir=_TMP)
        self.auto = os.path.join(self.cfg, "autoexec.cfg")

    def read(self):
        with open(self.auto, encoding="utf-8") as fh:
            return fh.read()

    def test_reapply_engine_tweaks_keeps_ze_block_and_user_lines(self):
        with open(self.auto, "w", encoding="utf-8") as fh:
            fh.write('bind "mouse5" "+voicerecord"\n')
        core_logic.install_autoexec(self.cfg)
        core_logic.apply_ze_visual_and_hud_customizer(self.cfg, {"duck_key": "F7", "voice_mute_key": "F8"})
        with open(self.auto, "a", encoding="utf-8") as fh:
            fh.write("// my line at the very end\n")
        core_logic.install_autoexec(self.cfg)          # before the fix this deleted the ZE block
        txt = self.read()
        self.assertIn('bind "mouse5" "+voicerecord"', txt)
        self.assertIn("ZE VISUAL, HUD & AUDIO DUCKING STUDIO START", txt)
        self.assertIn("// my line at the very end", txt)
        self.assertEqual(txt.count("[CS2 FPS OPTIMIZER - PERFORMANCE TWEAKS]"), 1)
        self.assertEqual(txt.count("PERFORMANCE TWEAKS END]"), 1)

    def test_old_block_without_end_marker_is_replaced_not_truncated(self):
        old = ("// mine\n// ============================================================\n"
               "// [CS2 FPS OPTIMIZER - PERFORMANCE TWEAKS]\n// ============================================================\n"
               "fps_max 0\n\necho \"[CS2 FPS Optimizer] Performance tweaks & custom binds loaded successfully!\"\n"
               "// ZE after\nbind F7 x\n")
        with open(self.auto, "w", encoding="utf-8") as fh:
            fh.write(old)
        core_logic.install_autoexec(self.cfg)
        txt = self.read()
        self.assertIn("// ZE after\nbind F7 x", txt)
        self.assertIn("// mine", txt)
        self.assertEqual(txt.count("[CS2 FPS OPTIMIZER - PERFORMANCE TWEAKS]"), 1)

    def test_restore_without_backup_removes_only_the_block(self):
        with open(self.auto, "w", encoding="utf-8") as fh:
            fh.write("// a\n" + core_logic.PERF_BLOCK + "// b\n")
        core_logic.restore_autoexec_backup(self.cfg)
        txt = self.read()
        self.assertIn("// a", txt); self.assertIn("// b", txt)
        self.assertNotIn("PERFORMANCE TWEAKS", txt)

    def test_blocks_have_undo_lines_and_no_writeconfig_or_camera_turn_binds(self):
        core_logic.apply_ze_visual_and_hud_customizer(self.cfg, {"duck_key": "F7", "voice_mute_key": "F8"})
        ze = self.read()
        for txt in (ze, core_logic.PERF_BLOCK):
            self.assertIn("UNDO", txt)
            self.assertNotIn("host_writeconfig", txt.lower().replace("// audit", ""))
            self.assertIsNone(re.search(r'"\+(left|right)"|[;" ]\+(left|right)\b', txt))
        self.assertIn("unbind F7", ze)
        print("\n[#9] ZE block header:\n" + "\n".join(ze.splitlines()[:7]))

    def test_website_generator_source(self):
        with open(os.path.join(ROOT, "src", "components", "CS2AutoexecGeneratorSection.tsx"), encoding="utf-8") as fh:
            src = fh.read()
        self.assertNotIn("host_writeconfig", src)
        self.assertIsNone(re.search(r"\+left|\+right|-left|-right", src))
        self.assertIn("HOW TO UNDO", src)
        self.assertLess(src.index("HOW TO UNDO"), src.index("const out = [...header, ...undoLines, ...body]"))


# --------------------------------------------------------------------------- #8
class Bug8NavbarSource(unittest.TestCase):
    """Behaviour was checked in a browser (see audit/FINDINGS_PHASE2.md); this guards the code."""
    def test_click_sets_active_first_and_bottom_forces_contact(self):
        with open(os.path.join(ROOT, "src", "components", "CyberNavbar.tsx"), encoding="utf-8") as fh:
            src = fh.read()
        click = src[src.index("const handleNavClick"):]
        self.assertLess(click.index("setActiveSection(targetId)"), click.index("scrollToSectionById(targetId)"))
        self.assertIn("if (isManualScrollingRef.current) return;", src)
        self.assertRegex(src, r"scrollY \+ windowHeight >= docHeight - \d+\)\s*\{\s*setActiveSection\('contact'\)")


if __name__ == "__main__":
    try:
        _res = unittest.main(exit=False, verbosity=2)
        ok = _res.result.wasSuccessful()
    finally:
        shutil.rmtree(_TMP, ignore_errors=True)
    sys.stdout.flush(); sys.stderr.flush()
    os._exit(0 if ok else 1)
