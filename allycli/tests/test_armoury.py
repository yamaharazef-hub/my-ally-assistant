# -*- coding: utf-8 -*-
"""Tests for the 'armoury' plugin (Armoury Crate for Bazzite Linux).

All hardware access is mocked, so these tests run on any machine.
"""
import unittest
from unittest import mock

from tests import PluginTest
from plugins.armoury import armoury_crate, _report_results
from packages.armoury import PROFILES
from packages.armoury.lighting import COLORS, parse_color


ARMOURY = "packages.armoury"


FAKE_STATUS = {
    "device_kind": "rog-ally",
    "device_model": "ROG Ally RC71L",
    "is_bazzite": True,
    "cpu": "AMD Ryzen Z1 Extreme",
    "temp_c": 44.5,
    "temp_chip": "k10temp",
    "mem_total_mb": 16384,
    "mem_used_mb": 5000,
    "power_profile": "balanced",
    "on_ac": True,
    "tdp_w": 30,
    "fan": {"chip": "asus", "pwm": "128", "percent": 50, "rpm": 3200,
            "manual": False, "pwm_file": "/sys/x/pwm1"},
    "battery": {"name": "BAT0", "percent": 78, "status": "Discharging",
                "charge_limit": 80},
    "rgb_backends": ["kernel LEDs (ROG Ally / ASUS)"],
    "uptime": "2h 15m",
}


class ArmouryTest(PluginTest):
    def setUp(self):
        self.test = self.load_plugin(armoury_crate)

    def output(self):
        """Everything Ally said so far, joined into one string."""
        return "\n".join(str(t) for t in self.history_say().view_text())

    def history_say(self):
        return self.ally_api.say_history

    def test_dashboard(self):
        with mock.patch(ARMOURY + ".get_status", return_value=FAKE_STATUS):
            self.test(self.ally_api, "status")
        out = self.output()
        self.assertIn("ARMOURY CRATE", out)
        self.assertIn("ROG Ally", out)
        self.assertIn("Bazzite", out)
        self.assertIn("AMD Ryzen Z1 Extreme", out)
        self.assertIn("30W", out)
        self.assertIn("80%", out)
        self.assertIn("balanced", out)

    def test_no_args_shows_dashboard(self):
        with mock.patch(ARMOURY + ".get_status", return_value=FAKE_STATUS):
            self.test(self.ally_api, "")
        self.assertIn("ARMOURY CRATE", self.output())

    def test_profile_turbo(self):
        results = [(True, "Power profile set to 'performance'"),
                   (True, "TDP preset applied: 30W")]
        with mock.patch(ARMOURY + ".apply_profile",
                        return_value=results) as apply_mock:
            self.test(self.ally_api, "profile turbo")
            apply_mock.assert_called_once_with("turbo")
        self.assertIn("TDP preset applied: 30W", self.output())

    def test_profile_usage(self):
        with mock.patch(ARMOURY + ".get_power_profile",
                        return_value="balanced"):
            self.test(self.ally_api, "profile")
        self.assertIn("Usage: armoury profile", self.output())

    def test_tdp_set(self):
        with mock.patch(ARMOURY + ".set_tdp",
                        return_value=(True, "TDP set to 15W")) as set_mock:
            self.test(self.ally_api, "tdp 15")
            set_mock.assert_called_once_with("15")
        self.assertIn("TDP set to 15W", self.output())

    def test_tdp_failure_reported(self):
        with mock.patch(ARMOURY + ".set_tdp",
                        return_value=(False, "ryzenadj failed")):
            self.test(self.ally_api, "tdp 15")
        self.assertIn("ryzenadj failed", self.output())

    def test_fan_usage(self):
        self.test(self.ally_api, "fan")
        self.assertIn("Usage: armoury fan", self.output())

    def test_fan_set(self):
        with mock.patch(ARMOURY + ".set_fan",
                        return_value=(True, "Fan set to 60%")) as set_mock:
            self.test(self.ally_api, "fan 60")
            set_mock.assert_called_once_with("60")

    def test_rgb_set(self):
        with mock.patch(ARMOURY + ".set_rgb",
                        return_value=(True, "Lighting #00C800")) as set_mock:
            self.test(self.ally_api, "rgb green")
            set_mock.assert_called_once_with("green")

    def test_rgb_usage(self):
        with mock.patch(ARMOURY + ".get_rgb_backends", return_value=[]):
            self.test(self.ally_api, "rgb")
        self.assertIn("Usage: armoury rgb", self.output())

    def test_battery_usage(self):
        with mock.patch(ARMOURY + ".get_charge_limit", return_value=80):
            self.test(self.ally_api, "battery")
        self.assertIn("Current charge limit: 80%", self.output())

    def test_battery_set(self):
        with mock.patch(ARMOURY + ".set_charge_limit",
                        return_value=(True, "Battery care enabled")) as m:
            self.test(self.ally_api, "battery 80")
            m.assert_called_once_with("80")

    def test_unknown_subcommand_shows_help(self):
        self.test(self.ally_api, "warpdrive")
        out = self.output()
        self.assertIn("Unknown armoury command 'warpdrive'", out)
        self.assertIn("armoury tdp", out)

    def test_help(self):
        self.test(self.ally_api, "help")
        self.assertIn("Armoury Crate commands", self.output())

    def test_report_results_returns_overall_status(self):
        # all ok -> True ; single failure -> False
        self.assertTrue(_report_results(self.ally_api, [(True, "a")]))
        self.assertFalse(_report_results(
            self.ally_api, [(True, "a"), (False, "b")]))


class ArmouryHelpersTest(unittest.TestCase):
    """Offline unit tests for helper logic (no hardware needed)."""

    def test_profiles_shape(self):
        for name in ("silent", "performance", "turbo"):
            self.assertIn(name, PROFILES)
            ppd, tdp_dc, tdp_ac = PROFILES[name]
            self.assertIsInstance(ppd, str)
            self.assertLess(tdp_dc, tdp_ac + 1)
        # Armoury Crate semantics on the Ally: Turbo = 25W batt / 30W AC
        self.assertEqual(PROFILES["turbo"][1], 25)
        self.assertEqual(PROFILES["turbo"][2], 30)

    def test_parse_color_names(self):
        self.assertEqual(parse_color("red"), (255, 0, 0))
        self.assertEqual(parse_color("GREEN"), (0, 200, 0))
        self.assertEqual(parse_color("off"), (0, 0, 0))

    def test_parse_color_hex(self):
        self.assertEqual(parse_color("#FF8800"), (255, 136, 0))
        self.assertEqual(parse_color("00ff00"), (0, 255, 0))

    def test_parse_color_invalid(self):
        self.assertIsNone(parse_color("not-a-colour"))
        self.assertIsNone(parse_color("#12345"))
        self.assertIsNone(parse_color(None))

    def test_colors_palette_present(self):
        for colour in ("off", "white", "red", "green", "blue"):
            self.assertIn(colour, COLORS)


if __name__ == '__main__':
    unittest.main()
