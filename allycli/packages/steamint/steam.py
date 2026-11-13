# -*- coding: utf-8 -*-
"""Steam Game Mode integration: shortcut + artwork management.

Adds/reads/removes a non-Steam-game shortcut for My Ally Assistant in
every local Steam account found, and drops the library artwork into
`userdata/<id>/config/grid/` so the tile looks native in Game Mode
(Bazzite, SteamOS/Steam Deck, desktop Steam).

Steam must be CLOSED while shortcuts.vdf is edited, otherwise the client
overwrites the file on exit — the plugin tells the user this.
"""

import glob
import os
import shutil
import zlib

from packages.steamint import vdf
from packages.steamint.launcher import (
    ALLIE_ICON, install_launcher, install_desktop_entry)

APP_NAME = "My Ally Assistant"

# artwork roles -> target filename pattern in config/grid/
# (<appid> = 64-bit shortcut id, same scheme Steam ROM Manager uses)
ARTWORK = {
    "icons/steam_grid.png": "{}.png",        # landscape tile (920x430)
    "icons/steam_capsule.png": "{}p.png",    # portrait capsule (600x900)
    "icons/steam_hero.png": "{}_hero.png",   # detail banner (3840x1240)
    "icons/steam_logo.png": "{}_logo.png",   # game logo overlay
}


def shortcut_id(exe, appname):
    """Steam's non-Steam-game id algorithm: crc32 of Exe+AppName, high bit set.

    `exe` must be the exact string stored in shortcuts.vdf (incl. quotes).
    """
    crc = zlib.crc32((exe + appname).encode("utf-8")) & 0xFFFFFFFF
    return crc | 0x80000000


def appid64(shortcut):
    """64-bit id Steam uses for artwork file names."""
    return ((shortcut & 0xFFFFFFFF) << 32) | 0x02000000


def find_steam_users():
    """All local Steam userdata/<account> dirs, across install variants."""
    roots = [
        "~/.steam/steam/userdata",
        "~/.local/share/Steam/userdata",
        "~/.var/app/com.valvesoftware.Steam/.local/share/Steam/userdata",
        "~/.var/app/com.valvesoftware.Steam/.steam/steam/userdata",
    ]
    users = []
    for root in roots:
        root = os.path.expanduser(root)
        for account in sorted(glob.glob(os.path.join(root, "*"))):
            if os.path.isdir(account):
                users.append(account)
    return users


def _shortcut_vdf(user_dir):
    return os.path.join(user_dir, "config", "shortcuts.vdf")


def _repo_root():
    return os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def build_entry(exe, start_dir, icon_path=""):
    """The shortcut entry for My Ally Assistant."""
    entry = {
        "_index": "0",
        "appid": 0,
        "AppName": APP_NAME,
        "Exe": exe,
        "StartDir": start_dir,
        "icon": icon_path,
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
        "tags": ["Assistant", "Armoury"],
    }
    sid = shortcut_id(exe, APP_NAME)
    # stored as signed int32
    entry["appid"] = sid - (1 << 32) if sid >= (1 << 31) else sid
    return entry, sid


def _entry_is_ours(entry):
    return entry.get("AppName") == APP_NAME


def steam_setup(messages):
    """Install launcher + desktop entry + Steam shortcut + artwork.

    messages: list of (ok, message) tuples the caller reports to the user.
    """
    wrapper = install_launcher(messages)
    install_desktop_entry(wrapper, messages)

    users = find_steam_users()
    if not users:
        messages.append((False, "No Steam installation found — is Steam "
                                "installed? (Bazzite images include it)"))
        return

    exe = f'"{wrapper}"'
    start_dir = f'"{os.path.dirname(wrapper)}"'
    icon = os.path.join(_repo_root(), ALLIE_ICON)
    if not os.path.exists(icon):
        icon = ""

    entry, sid = build_entry(exe, start_dir, icon)
    art_id = appid64(sid)

    for user in users:
        vdf_path = _shortcut_vdf(user)
        os.makedirs(os.path.dirname(vdf_path), exist_ok=True)
        entries = []
        if os.path.exists(vdf_path):
            shutil.copy2(vdf_path, vdf_path + ".bak")
            try:
                entries = vdf.load_shortcuts(vdf_path)
            except vdf.VDFError:
                entries = entries or []
                messages.append((False, f"Could not parse {vdf_path} "
                                        f"(backup kept at {vdf_path}.bak)"))
                continue

        if any(_entry_is_ours(e) for e in entries):
            messages.append((True, f"Steam shortcut already present — refreshed "
                                   f"({user})"))
        else:
            entries.append(entry)
            vdf.save_shortcuts(vdf_path, entries)
            messages.append((True, f"Steam shortcut added ({user})"))

        _install_artwork(user, art_id, messages)

    messages.append((True, "Restart Steam (or reboot into Game Mode) — Ally "
                           "now appears in your Steam library ⚔"))
    messages.append((True, "Tip: in Steam, right-click the tile → Manage → "
                           "set launch options or custom artwork anytime."))


def _install_artwork(user_dir, art_id, messages):
    grid = os.path.join(user_dir, "config", "grid")
    installed = 0
    for src_rel, pattern in ARTWORK.items():
        src = os.path.join(_repo_root(), src_rel)
        if not os.path.exists(src):
            continue
        os.makedirs(grid, exist_ok=True)
        shutil.copy2(src, os.path.join(grid, pattern.format(art_id)))
        installed += 1
    if installed:
        messages.append((True, f"Library artwork installed "
                               f"({installed} image(s) → {grid})"))
    else:
        messages.append((False,
                         "No artwork images found in repo (icons/steam_*.png); "
                         "shortcut still added — assign art later in Steam."))


def steam_status():
    """Report integration state. Returns list of (ok, message)."""
    messages = []
    wrapper = os.path.expanduser("~/.local/bin/ally-terminal")
    messages.append((os.path.exists(wrapper), f"terminal wrapper: {wrapper}"))

    desktop = os.path.expanduser(
        "~/.local/share/applications/my-ally-assistant.desktop")
    messages.append((os.path.exists(desktop), f"desktop entry: {desktop}"))

    users = find_steam_users()
    if not users:
        messages.append((False, "no Steam userdata dirs found"))
        return messages

    for user in users:
        vdf_path = _shortcut_vdf(user)
        if not os.path.exists(vdf_path):
            messages.append((False, f"{user}: no shortcuts.vdf yet"))
            continue
        try:
            entries = vdf.load_shortcuts(vdf_path)
        except vdf.VDFError as exc:
            messages.append((False, f"{user}: unreadable shortcuts.vdf ({exc})"))
            continue
        ours = [e for e in entries if _entry_is_ours(e)]
        messages.append((bool(ours),
                         f"{user}: shortcut {'present' if ours else 'missing'} "
                         f"({len(entries)} non-Steam game(s) total)"))
        if ours:
            sid = ours[0]["appid"] & 0xFFFFFFFF
            grid = os.path.join(user, "config", "grid")
            art = glob.glob(os.path.join(grid, f"{appid64(sid)}*.png"))
            messages.append((bool(art), f"{user}: {len(art)} artwork file(s)"))
    return messages


def steam_remove(messages):
    """Remove the shortcut and its artwork (keeps .desktop entry? also removed)."""
    users = find_steam_users()
    if not users:
        messages.append((False, "No Steam installation found"))
    for user in users:
        vdf_path = _shortcut_vdf(user)
        if not os.path.exists(vdf_path):
            continue
        try:
            entries = vdf.load_shortcuts(vdf_path)
        except vdf.VDFError:
            continue
        ours = [e for e in entries if _entry_is_ours(e)]
        rest = [e for e in entries if not _entry_is_ours(e)]
        if not ours:
            messages.append((True, f"{user}: nothing to remove"))
            continue
        shutil.copy2(vdf_path, vdf_path + ".bak")
        vdf.save_shortcuts(vdf_path, rest)
        for e in ours:
            sid = e["appid"] & 0xFFFFFFFF
            grid = os.path.join(user, "config", "grid")
            for art in glob.glob(os.path.join(grid, f"{appid64(sid)}*.png")):
                os.remove(art)
        messages.append((True, f"{user}: shortcut + artwork removed"))

    for path in (os.path.expanduser("~/.local/bin/ally-terminal"),
                 os.path.expanduser(
                     "~/.local/share/applications/my-ally-assistant.desktop")):
        if os.path.exists(path):
            os.remove(path)
            messages.append((True, f"removed {path}"))
    messages.append((True, "Restart Steam to apply."))
