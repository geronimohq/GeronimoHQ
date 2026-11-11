"""Owner's laptop test 2026-11-11: a slow PC showed the built-in SAMPLE specs (Ryzen 5700X3D / RX 6600) instead of its own Intel N100,
because the page gave up waiting for the engine after 1.5 s. Inside the app the page must wait and never show sample data."""
import os
import re
import unittest

import _test_isolation  # noqa: F401
import core_logic
import core_service

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class NeverSampleDataInsideTheApp(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "desktop-ui", "src", "api.ts"), encoding="utf-8") as fh:
            self.api = fh.read()

    def test_the_apps_own_address_waits_for_the_engine_and_never_falls_back_to_sample_data(self):
        self.assertIn("window.location.hostname === '127.0.0.1'", self.api)            # pywebview serves the page from 127.0.0.1
        self.assertRegex(self.api, r"setTimeout\(res, IN_APP \? \d{5,} : 1500\)")        # long wait inside the app, 1.5 s only in a plain browser
        self.assertRegex(self.api, r"if \(IN_APP\) throw new Error")                      # a missing engine is an error, not sample data

    def test_every_sample_cpu_in_the_page_is_behind_the_mock(self):
        self.assertEqual(len(re.findall("5700X3D", self.api)), 1)                         # only the one mock answer for 'hw_info'


class RealSpecsComeFromWindows(unittest.TestCase):
    def test_hw_info_reports_what_windows_says(self):
        import hardware_info
        from unittest import mock
        with mock.patch.object(hardware_info, "get_cpu_info", return_value={"name": "Intel(R) N100", "is_x3d": False, "is_laptop": False, "power_reason": "x", "recommended_power_plan": "High Performance"}), \
                mock.patch.object(hardware_info, "get_gpu_info", return_value={"name": "Intel(R) UHD Graphics"}):
            r = core_service.Core().hw_info()
        self.assertEqual((r["cpu"], r["gpu"]), ("Intel(R) N100", "Intel(R) UHD Graphics"))


class LaptopDetection(unittest.TestCase):
    def test_a_battery_makes_a_laptop_even_when_the_cpu_name_has_no_mobile_marker(self):
        import hardware_info
        from unittest import mock
        with mock.patch.object(hardware_info, "has_battery", return_value=True), mock.patch.object(hardware_info.winreg, "OpenKey", side_effect=OSError), \
                mock.patch.object(hardware_info.platform, "processor", return_value="Intel(R) N100"):
            cpu = hardware_info.get_cpu_info()
        self.assertTrue(cpu["is_laptop"])
        self.assertEqual(cpu["recommended_power_plan"], "Balanced")
        with mock.patch.object(hardware_info, "has_battery", return_value=False), mock.patch.object(hardware_info.winreg, "OpenKey", side_effect=OSError), \
                mock.patch.object(hardware_info.platform, "processor", return_value="AMD Ryzen 5 5600 6-Core Processor"):
            self.assertFalse(hardware_info.get_cpu_info()["is_laptop"])


if __name__ == "__main__":
    unittest.main()
