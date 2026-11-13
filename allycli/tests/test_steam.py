# -*- coding: utf-8 -*-
"""Tests for Steam / Game Mode integration (plugin 'steam').

Touches no real Steam installation: every test works against temporary
directories and mocked find_steam_users().
"""
import glob
import os
import tempfile
import unittest
from unittest import mock

from tests import PluginTest
from plugins.steam import steam as steam_plugin
from packages.steamint import vdf
from packages.steamint.steam import (
    APP_NAME, appid64, build_entry, shortcut_id,
    steam_remove, steam_setup, steam_status)
import packages.steamint.launcher as launcher


STEAM = "packages.steamint.steam"


def _make_entry(name="Test Game", exe='"/usr/bin/test"'):
    entry = {
        "_index": "0",
        "appid": 12345,
        "AppName": name,
        "Exe": exe,
        "StartDir": '"/usr"',
        "icon": "",
        "ShortcutPath": "",
        "LaunchOptions": "",
        "IsHidden": 0,
        "AllowDesktopConfig": 1,
        "AllowOverlay": 1,
        "OpenVR": 0,
        "Devkit": 0,
        "DevkitGameID": "",
        "DevkitOverrideAppID": 0,
        "LastPlayTime": 0,
        "tags": ["Action"],
    }
    return entry


class VDFTest(unittest.TestCase):
    def test_roundtrip_single_entry(self):
        original = [_make_entry()]
        data = vdf.dump_shortcuts(original)
        loaded = vdf.load_shortcuts_from_bytes(data)
        self.assertEqual(len(loaded), 1)
        entry = loaded[0]
        self.assertEqual(entry["AppName"], "Test Game")
        self.assertEqual(entry["appid"], 12345)
        self.assertEqual(entry["LaunchOptions"], "")
        self.assertEqual(entry["tags"], ["Action"])

    def test_roundtrip_multiple_entries_and_negative_appid(self):
        entry1 = _make_entry("A")
        entry2 = _make_entry("B")
        entry2["appid"] = -2013205247   # signed int32, high bit set
        loaded = vdf.load_shortcuts_from_bytes(
            vdf.dump_shortcuts([entry1, entry2]))
        self.assertEqual([e["AppName"] for e in loaded], ["A", "B"])
        self.assertEqual(loaded[1]["appid"], -2013205247)

    def test_roundtrip_empty(self):
        self.assertEqual(vdf.load_shortcuts_from_bytes(
            vdf.dump_shortcuts([])), [])

    def test_load_empty_file(self):
        self.assertEqual(vdf.load_shortcuts_from_bytes(b""), [])

    def test_corrupt_file_raises(self):
        with self.assertRaises(vdf.VDFError):
            vdf.load_shortcuts_from_bytes(b"steam is great")


class ShortcutIDsTest(unittest.TestCase):
    def test_shortcut_id_algorithm(self):
        exe = '"~/.local/bin/ally-terminal"'
        sid = shortcut_id(exe, APP_NAME)
        self.assertTrue(sid & 0x80000000)         # high bit always set
        # deterministic
        self.assertEqual(sid, shortcut_id(exe, APP_NAME))
        # 64-bit artwork id layout
        self.assertEqual(appid64(sid), ((sid & 0xFFFFFFFF) << 32) | 0x02000000)

    def test_build_entry_signed_appid(self):
        entry, sid = build_entry('"/x"', '"/x"', "")
        # stored appid is the int32-signed view of sid
        self.assertEqual(entry["appid"] & 0xFFFFFFFF, sid & 0xFFFFFFFF)
        self.assertEqual(entry["AppName"], APP_NAME)
        self.assertIn("Assistant", entry["tags"])


class SteamFilesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.user_dir = os.path.join(self.tmp.name, "userdata", "12345678")
        os.makedirs(self.user_dir)

    def tearDown(self):
        self.tmp.cleanup()

    def _paths(self):
        cfg = os.path.join(self.user_dir, "config")
        return os.path.join(cfg, "shortcuts.vdf"), os.path.join(cfg, "grid")

    def test_setup_adds_shortcut_and_artwork(self):
        messages = []
        with mock.patch(STEAM + ".install_launcher",
                        return_value="/fake/wrapper"), \
                mock.patch(STEAM + ".install_desktop_entry"), \
                mock.patch(STEAM + ".find_steam_users",
                           return_value=[self.user_dir]):
            steam_setup(messages)

        vdf_path, grid = self._paths()
        self.assertTrue(os.path.exists(vdf_path))
        entries = vdf.load_shortcuts(vdf_path)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["AppName"], APP_NAME)

        # artwork files land in config/grid keyed by appid64
        sid = entries[0]["appid"] & 0xFFFFFFFF
        arts = glob.glob(os.path.join(grid, f"{appid64(sid)}*.png"))
        self.assertTrue(len(arts) >= 4, f"expected >=4 artworks, got {arts}")

        ok_flags = [ok for ok, _ in messages]
        self.assertTrue(any(ok_flags))
        # backup file should exist on second run; no duplicates
        with mock.patch(STEAM + ".install_launcher",
                        return_value="/fake/wrapper"), \
                mock.patch(STEAM + ".install_desktop_entry"), \
                mock.patch(STEAM + ".find_steam_users",
                           return_value=[self.user_dir]):
            messages2 = []
            steam_setup(messages2)
        entries2 = vdf.load_shortcuts(vdf_path)
        self.assertEqual(len(entries2), 1)   # still exactly one Ally entry

    def test_setup_without_steam(self):
        messages = []
        with mock.patch(STEAM + ".install_launcher",
                        return_value="/fake/wrapper"), \
                mock.patch(STEAM + ".install_desktop_entry"), \
                mock.patch(STEAM + ".find_steam_users", return_value=[]):
            steam_setup(messages)
        # no Steam -> a clear failure message, nothing written
        self.assertTrue(any((not ok) and "No Steam" in m
                            for ok, m in messages))
        vdf_path, _ = self._paths()
        self.assertFalse(os.path.exists(vdf_path))

    def test_status_and_remove(self):
        # nothing installed -> status reports no shortcuts.vdf yet
        with mock.patch(STEAM + ".find_steam_users",
                        return_value=[self.user_dir]):
            messages = steam_status()
        self.assertTrue(any("no shortcuts.vdf" in m for _, m in messages))

        # install then remove
        with mock.patch(STEAM + ".install_launcher",
                        return_value="/fake/wrapper"), \
                mock.patch(STEAM + ".install_desktop_entry"), \
                mock.patch(STEAM + ".find_steam_users",
                           return_value=[self.user_dir]):
            steam_setup([])
            remove_messages = []
            steam_remove(remove_messages)
        vdf_path, _ = self._paths()
        entries = vdf.load_shortcuts(vdf_path)
        self.assertEqual(entries, [])
        self.assertTrue(any("removed" in m for _, m in remove_messages))


class LauncherTest(unittest.TestCase):
    def test_find_terminal(self):
        with mock.patch("shutil.which",
                        side_effect=lambda b: "/usr/bin/konsole"
                        if b == "konsole" else None):
            self.assertEqual(launcher.find_terminal(), "konsole")
        with mock.patch("shutil.which", return_value=None):
            self.assertIsNone(launcher.find_terminal())

    def test_install_launcher_writes_executable_script(self):
        tmp = tempfile.mkdtemp(prefix="allylauncher")
        wrapper = os.path.join(tmp, "ally-terminal")
        messages = []
        try:
            with mock.patch("packages.steamint.launcher.ALLEY_WRAPPER",
                            wrapper):
                out = launcher.install_launcher(messages)
            self.assertEqual(out, wrapper)
            with open(wrapper) as fh:
                content = fh.read()
            self.assertIn("konsole", content)      # terminal detection
            self.assertIn("allycli", content)      # runs the assistant
            # executable bit
            self.assertTrue(os.stat(wrapper).st_mode & 0o111)
            self.assertTrue(messages[0][0])
        finally:
            os.remove(wrapper)
            os.rmdir(tmp)

    def test_desktop_entry_content(self):
        tmp = tempfile.mkdtemp(prefix="allydesktop")
        desktop = os.path.join(tmp, "my-ally-assistant.desktop")
        messages = []
        try:
            with mock.patch("packages.steamint.launcher.DESKTOP_FILE",
                            desktop):
                launcher.install_desktop_entry("/fake/wrapper", messages)
            with open(desktop) as fh:
                content = fh.read()
            self.assertIn("Name=My Ally Assistant", content)
            self.assertIn("Exec=/fake/wrapper", content)
            self.assertIn("Categories=Utility;Game;", content)
        finally:
            os.remove(desktop)
            os.rmdir(tmp)


class SteamPluginTest(PluginTest):
    def setUp(self):
        self.test = self.load_plugin(steam_plugin)

    def output(self):
        return "\n".join(str(t) for t in self.ally_api.say_history.view_text())

    def test_status(self):
        with mock.patch(STEAM + ".find_steam_users", return_value=[]):
            self.test(self.ally_api, "status")
        self.assertIn("Steam / Game Mode integration", self.output())

    def test_setup_runs_flow(self):
        with mock.patch("packages.steamint.steam_setup") as setup_mock:
            self.test(self.ally_api, "setup")
            setup_mock.assert_called_once()

    def test_remove(self):
        with mock.patch("packages.steamint.steam_remove") as remove_mock:
            self.test(self.ally_api, "remove")
            remove_mock.assert_called_once()

    def test_unknown(self):
        self.test(self.ally_api, "warpdrive")
        self.assertIn("Unknown steam command", self.output())


if __name__ == '__main__':
    unittest.main()
