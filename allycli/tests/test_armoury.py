# -*- coding: utf-8 -*-
"""Tests for the 'armoury' plugin (Armoury Crate for Bazzite Linux).

All hardware access is mocked, so these tests run on any machine.
"""
import unittest
from unittest import mock

from tests import PluginTest
from plugins.armoury import armoury_crate, _report_results
from packages.armoury import PROFILES, profiles_for
from packages.armoury.system import Device, detect_device, device_label
from packages.armoury.lighting import COLORS, parse_color
import packages.armoury.power as power


ARMOURY = "packages.armoury"


FAKE_STATUS = {
    "device_kind": "xbox-ally-x",
    "device_model": "ROG Xbox Ally X RC73XA",
    "is_bazzite": True,
    "cpu": "AMD Ryzen AI Z2 Extreme",
    "temp_c": 44.5,
    "temp_chip": "k10temp",
    "mem_total_mb": 24576,
    "mem_used_mb": 9000,
    "power_profile": "balanced",
    "on_ac": True,
    "tdp_w": 35,
    "fan": {"chip": "asus-armoury", "pwm": "128", "percent": 50, "rpm": 3200,
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
        self.assertIn("ROG Xbox Ally X", out)
        self.assertIn("Bazzite", out)
        self.assertIn("AMD Ryzen AI Z2 Extreme", out)
        self.assertIn("35W", out)
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


class ArmouryDeviceTest(unittest.TestCase):
    """Device detection & per-device presets (DMI reads mocked)."""

    def _detect_with_dmi(self, vendor, product):
        def fake_read(path):
            if path == "/sys/class/dmi/id/sys_vendor":
                return vendor
            if path == "/sys/class/dmi/id/product_name":
                return product
            return None
        with mock.patch("packages.armoury.system._read",
                        side_effect=fake_read):
            return detect_device()

    def test_detect_xbox_ally_x(self):
        kind, product = self._detect_with_dmi(
            "ASUSTeK COMPUTER INC.", "ROG Xbox Ally X RC73XA")
        self.assertEqual(kind, Device.XBOX_ALLY_X)
        self.assertEqual(device_label(kind), "ROG Xbox Ally X (2025)")

    def test_detect_ally_family(self):
        self.assertEqual(self._detect_with_dmi("ASUSTeK", "ROG Ally RC71L")[0],
                         Device.ALLY)
        self.assertEqual(self._detect_with_dmi("ASUSTeK", "ROG Ally X RC72LA")[0],
                         Device.ALLY_X)
        self.assertEqual(self._detect_with_dmi("ASUSTeK", "ROG Xbox Ally RC73YA")[0],
                         Device.XBOX_ALLY)

    def test_detect_asus_laptop_and_generic(self):
        kind, _ = self._detect_with_dmi("ASUSTeK", "ROG Strix G16")
        self.assertEqual(kind, Device.ASUS_LAPTOP)
        kind, _ = self._detect_with_dmi("Dell Inc.", "XPS 13")
        self.assertEqual(kind, Device.GENERIC)

    def test_per_device_turbo_presets(self):
        # default (ROG Ally 2023): 25W battery / 30W AC
        self.assertEqual(profiles_for(Device.ALLY)["turbo"][1:], (25, 30))
        # ROG Ally X 2024: same turbo
        self.assertEqual(profiles_for(Device.ALLY_X)["turbo"][1:], (25, 30))
        # Xbox Ally X 2025: Turbo 25W battery / 35W AC (official)
        self.assertEqual(profiles_for(Device.XBOX_ALLY_X)["turbo"][1:], (25, 35))
        # Xbox Ally (Z2 A Go): 17W / 20W
        self.assertEqual(profiles_for(Device.XBOX_ALLY)["turbo"][1:], (17, 20))
        # unknown hardware falls back to default presets
        self.assertEqual(profiles_for(Device.GENERIC)["turbo"][1:], (25, 30))

    def test_apply_profile_xbox_ally_x_ac(self):
        with mock.patch(ARMOURY + ".power.set_power_profile",
                        return_value=(True, "ok")), \
                mock.patch(ARMOURY + ".power.is_on_ac_power",
                           return_value=True), \
                mock.patch(ARMOURY + ".power.set_tdp",
                           return_value=(True, "ok")) as tdp:
            results = power.apply_profile("turbo",
                                          device_kind=Device.XBOX_ALLY_X)
            tdp.assert_called_once_with(35)
        self.assertTrue(all(ok for ok, _ in results))

    def test_apply_profile_xbox_ally_x_battery(self):
        with mock.patch(ARMOURY + ".power.set_power_profile",
                        return_value=(True, "ok")), \
                mock.patch(ARMOURY + ".power.is_on_ac_power",
                           return_value=False), \
                mock.patch(ARMOURY + ".power.set_tdp",
                           return_value=(True, "ok")) as tdp:
            power.apply_profile("turbo", device_kind=Device.XBOX_ALLY_X)
            tdp.assert_called_once_with(25)

    def test_apply_profile_laptop_skips_tdp(self):
        with mock.patch(ARMOURY + ".power.set_power_profile",
                        return_value=(True, "ok")), \
                mock.patch(ARMOURY + ".power.set_tdp") as tdp:
            results = power.apply_profile("turbo",
                                          device_kind=Device.ASUS_LAPTOP)
            tdp.assert_not_called()
        msgs = [m for _, m in results]
        self.assertIn("armoury tdp", " ".join(msgs))

    def test_apply_profile_unknown_name(self):
        results = power.apply_profile("warpdrive",
                                      device_kind=Device.XBOX_ALLY_X)
        self.assertFalse(results[0][0])
        self.assertIn("Unknown profile", results[0][1])


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
