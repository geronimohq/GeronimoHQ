"""Bot filter (Net4All / FYS report bots=0 but count bots in 'players') and the Country/Region GEO view."""
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geo_estimate  # noqa: E402
import server_browser  # noqa: E402

_REAL_QUERY_INFO = server_browser.query_server_info   # the app tests below stub the network module


def _info_packet(players, max_players, bots):
    body = b"\x11" + b"Zombie Test\x00" + b"ze_test\x00" + b"csgo\x00" + b"CS2\x00" + b"\x00\x00" + bytes([players, max_players, bots])
    return b"\xff\xff\xff\xff\x49" + body + b"\x00" * 6


class FakeSock:
    def __init__(self, packet):
        self.packet = packet

    def settimeout(self, t): pass
    def sendto(self, data, addr): pass
    def recvfrom(self, n): return self.packet, ("1.2.3.4", 27015)
    def close(self): pass


class BotFilter(unittest.TestCase):
    def _info(self, players, bots, roster):
        with mock.patch.object(server_browser.socket, "socket", lambda *a, **k: FakeSock(_info_packet(players, 65, bots))), \
             mock.patch.object(server_browser.socket, "gethostbyname", lambda h: "1.2.3.4"), \
             mock.patch.object(server_browser, "query_server_players", return_value=roster) as qp:
            return _REAL_QUERY_INFO("1.2.3.4", 27015), qp

    def test_server_that_hides_bots_is_corrected_from_the_roster(self):
        info, _ = self._info(16, 0, {"success": True, "count": 1, "players": [{}]})
        self.assertEqual(info["bots"], 15)
        self.assertEqual(info["curr_players"] - info["bots"], 1)      # 1 human, as the app computes it

    def test_server_that_reports_bots_is_left_alone_and_not_queried(self):
        info, qp = self._info(10, 2, {"success": True, "count": 8, "players": []})
        self.assertEqual(info["bots"], 2)
        qp.assert_not_called()

    def test_roster_failure_keeps_reported_numbers(self):
        info, _ = self._info(16, 0, {"success": False, "players": []})
        self.assertEqual(info["bots"], 0)

    def test_all_human_server_unchanged(self):
        info, _ = self._info(63, 0, {"success": True, "count": 63, "players": []})
        self.assertEqual(info["bots"], 0)


class GeoRegion(unittest.TestCase):
    def test_regions_sum_countries(self):
        items = geo_estimate.estimate_countries("US Chicago", 40, [])
        regions = geo_estimate.estimate_regions(items)
        self.assertEqual(sum(r["percentage"] for r in regions), sum(i["percentage"] for i in items))
        self.assertTrue({r["code"] for r in regions} <= {"NA", "EU", "ASIA", "LATAM", "OTHER"})
        self.assertEqual(regions, sorted(regions, key=lambda r: -r["percentage"]))

    def test_modes_give_different_text_and_a_tooltip(self):
        c, tip_c = server_browser.get_server_demographics("US Chicago", 40, None, [], mode="country")
        r, tip_r = server_browser.get_server_demographics("US Chicago", 40, None, [], mode="region")
        self.assertNotEqual(c, r)
        self.assertIn("By Country", tip_c)
        self.assertIn("By Region", tip_r)
        self.assertIn("North America", tip_r)

    def test_text_wrapper_unchanged_default(self):
        self.assertEqual(server_browser.get_server_demographics_text("Europe (Spain)", 0), "\U0001F310 GEO: server empty")


class AppPieces(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import _test_isolation  # noqa: F401
        import app
        cls.app = app
        cls.root = app.CS2TruePanoramaApp()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        with mock.patch.object(cls.app.os, "_exit", lambda code=0: None):
            cls.root.exit_application()

    def test_bot_dominated_rule(self):
        d = self.app.CS2TruePanoramaApp._bot_dominated
        self.assertTrue(d(15, 14))       # Net4All
        self.assertTrue(d(6, 3))
        self.assertFalse(d(63, 0))       # GFL
        self.assertFalse(d(10, 2))
        self.assertFalse(d(2, 2))        # too small to call

    def test_geo_mode_is_per_server_and_badge_shows(self):
        import time
        root = self.root
        root._select_nav("SERVERS")
        end = time.time() + 1.5
        while time.time() < end:
            root.update(); time.sleep(0.02)
        ids = list(root.server_row_widgets)
        self.assertGreaterEqual(len(ids), 2)
        a, b = ids[0], ids[1]
        root._set_geo_mode("region", a)
        self.assertEqual(root.server_row_widgets[a]["geo_mode"], "region")
        self.assertEqual(root.server_row_widgets[b]["geo_mode"], "country")
        self.assertEqual(root.gfl_geo_mode, "country")
        root._set_geo_mode("region", None)
        self.assertEqual(root.server_row_widgets[b]["geo_mode"], "country")
        root._update_bot_badge(b, 15, 14)
        root.update()
        self.assertTrue(root.server_row_widgets[b]["bot_pill"].winfo_ismapped())
        root._update_bot_badge(b, 63, 0)
        root.update()
        self.assertFalse(root.server_row_widgets[b]["bot_pill"].winfo_ismapped())


if __name__ == "__main__":
    _res = unittest.main(exit=False, verbosity=2)
    sys.stdout.flush(); sys.stderr.flush()
    os._exit(0 if _res.result.wasSuccessful() else 1)
