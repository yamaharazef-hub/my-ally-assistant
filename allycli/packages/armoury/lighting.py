# -*- coding: utf-8 -*-
"""Aura-style RGB lighting control.

Backend priority on Bazzite:

1. Kernel LED class devices — ROG Ally joystick rings are exposed by
   the in-kernel `hid-asus-ally` driver under /sys/class/leds with a
   `multi_intensity` RGB file. Other ASUS boards expose similar nodes.
2. asusctl (`asusctl aura`) — Asus Linux stack for ROG/TUF laptops.
3. OpenRGB (`openrgb`) — universal fallback if the user has it.

Colour names mirror Armoury Crate's quick palette; raw #RRGGBB also
accepted (e.g. `armoury rgb #FF8800`).
"""

import glob
import os
import re

from packages.armoury.system import run, which, _read, _write

COLORS = {
    "off": (0, 0, 0),
    "white": (255, 255, 255),
    "red": (255, 0, 0),
    "orange": (255, 80, 0),
    "yellow": (255, 200, 0),
    "green": (0, 200, 0),
    "aqua": (0, 255, 255),
    "blue": (0, 80, 255),
    "purple": (150, 0, 255),
    "pink": (255, 0, 140),
}

LED_NAME_HINTS = ("ally", "asus", "aura", "rgb")


def parse_color(value):
    """Parse a colour name or hex string into (r, g, b). None if invalid."""
    if value is None:
        return None
    value = str(value).strip().lower()
    if value in COLORS:
        return COLORS[value]
    match = re.fullmatch(r"#?([0-9a-f]{6})", value)
    if match:
        hexstr = match.group(1)
        return tuple(int(hexstr[i:i + 2], 16) for i in (0, 2, 4))
    return None


# ---------------------------------------------------------------- LED class

def _led_nodes():
    """Yield candidate /sys/class/leds entries with RGB capability."""
    for led in sorted(glob.glob("/sys/class/leds/*")):
        name = os.path.basename(led).lower()
        if not any(hint in name for hint in LED_NAME_HINTS):
            continue
        if os.path.exists(os.path.join(led, "multi_intensity")):
            yield led


def _set_rgb_leds(r, g, b):
    leds = list(_led_nodes())
    if not leds:
        return False, "no LED class devices"
    failures = 0
    for led in leds:
        ok_intensity = _write(os.path.join(led, "multi_intensity"),
                              f"{r} {g} {b}")

        # brightness scale differs per driver (some are 0-255, Ally
        # joystick rings are 0-100) — always drive at the node maximum
        max_brightness = _read(os.path.join(led, "max_brightness")) or "255"
        if not max_brightness.isdigit():
            max_brightness = "255"

        if r or g or b:
            # switch to steady static colour where the driver exposes
            # an effect list (Ally rings: monocolor, breathe, rainbow...)
            effect = os.path.join(led, "effect")
            available = (_read(os.path.join(led, "effect_index")) or "").lower()
            if os.path.exists(effect) and "monocolor" in available:
                _write(effect, "monocolor")
            target_brightness = max_brightness
        else:
            target_brightness = "0"
        ok_bright = _write(os.path.join(led, "brightness"), target_brightness)

        # disable any blinking trigger -> steady static light
        trigger = os.path.join(led, "trigger")
        if (r or g or b) and os.path.exists(trigger):
            _write(trigger, "none")
        if not (ok_intensity and ok_bright):
            failures += 1
    if failures == len(leds):
        return False, "LED nodes not writable (try running Ally with sudo)"
    return True, f"applied to {len(leds) - failures} LED zone(s)"


# ------------------------------------------------------------- asusctl

def _set_rgb_asusctl(r, g, b):
    if not which("asusctl"):
        return False, "asusctl not installed"
    if (r, g, b) == (0, 0, 0):
        args = ["asusctl", "aura", "static", "-c", "000000", "-z", "0"]
        ok, _, err = run(args)
    else:
        ok, _, err = run(
            ["asusctl", "aura", "static", "-c", f"{r:02X}{g:02X}{b:02X}"])
    return (True, "set via asusctl") if ok else (False, err or "asusctl failed")


# ------------------------------------------------------------- OpenRGB

def _set_rgb_openrgb(r, g, b):
    if not which("openrgb"):
        return False, "openrgb not installed"
    if (r, g, b) == (0, 0, 0):
        args = ["openrgb", "--mode", "off"]
    else:
        args = ["openrgb", "--mode", "static",
                "--color", f"{r:02X}{g:02X}{b:02X}"]
    ok, _, err = run(args, timeout=20)
    return (True, "set via OpenRGB") if ok else (False, err or "OpenRGB failed")


BACKENDS = (
    ("kernel LEDs (ROG Ally / ASUS)", _set_rgb_leds),
    ("asusctl aura", _set_rgb_asusctl),
    ("OpenRGB", _set_rgb_openrgb),
)


def get_rgb_backends():
    """Names of RGB backends that could work on this system."""
    available = []
    if list(_led_nodes()):
        available.append(BACKENDS[0][0])
    if which("asusctl"):
        available.append(BACKENDS[1][0])
    if which("openrgb"):
        available.append(BACKENDS[2][0])
    return available


def set_rgb(value):
    """Set device lighting. Returns (ok, message).

    value: colour name from COLORS, 'off', or #RRGGBB.
    """
    rgb = parse_color(value)
    if rgb is None:
        return False, (
            f"Unknown colour '{value}'. Try: "
            + ", ".join(sorted(COLORS)) + "  — or hex like #FF8800")

    errors = []
    for name, backend in BACKENDS:
        ok, msg = backend(*rgb)
        if ok:
            colour = "off" if rgb == (0, 0, 0) else (f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}")
            return True, f"Lighting {colour} ({name}: {msg})"
        errors.append(msg)

    return False, (
        "No working RGB backend found (checked kernel LEDs, asusctl, OpenRGB). "
        + "; ".join(errors))
