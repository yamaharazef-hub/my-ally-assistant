# -*- coding: utf-8 -*-
"""Hardware status dashboard — the Armoury Crate 'home screen'.

Everything here is read-only and stdlib-only (/proc, /sys, and a few
optional CLI tools), so it works on any Linux box and simply reports
'N/A' for capabilities the device does not have.
"""

import os

from packages.armoury.system import (
    detect_device, is_bazzite, find_hwmon, _read)
from packages.armoury.power import (
    get_power_profile, get_tdp, is_on_ac_power)
from packages.armoury.fan import get_fan_state
from packages.armoury.battery import get_battery_state
from packages.armoury.lighting import get_rgb_backends

# hwmon chips that report APU/CPU package temperature
TEMP_CHIP_HINTS = ("k10temp", "zenpower", "coretemp", "cpu_thermal",
                   "asus", "acpitz")


def _cpu_model():
    cpuinfo = _read("/proc/cpuinfo") or ""
    for line in cpuinfo.splitlines():
        if line.lower().startswith("model name"):
            return line.split(":", 1)[1].strip()
    return "Unknown CPU"


def _memory():
    """Return (total_mb, used_mb) from /proc/meminfo."""
    meminfo = _read("/proc/meminfo") or ""
    fields = {}
    for line in meminfo.splitlines():
        key, _, rest = line.partition(":")
        fields[key.strip()] = rest.strip()
    total = int(fields.get("MemTotal", "0 kB").split()[0]) // 1024
    available = int(fields.get("MemAvailable", "0 kB").split()[0]) // 1024
    return total, total - available


def _package_temp():
    """APU/CPU package temperature in °C (best guess across hwmons)."""
    for hwmon, chip in find_hwmon(TEMP_CHIP_HINTS):
        for entry in sorted(os.listdir(hwmon)):
            if not (entry.startswith("temp") and entry.endswith("_input")):
                continue
            # prefer the 'package' sensor (Tctl/Tdie) when labelled
            label = _read(os.path.join(hwmon, entry.replace("_input", "_label")))
            if label and label.lower() not in ("tctl", "tdie", "package id 0",
                                               "cpu"):
                continue
            raw = _read(os.path.join(hwmon, entry))
            if raw and raw.lstrip("-").isdigit():
                return round(int(raw) / 1000, 1), chip
    return None, None


def _uptime():
    raw = _read("/proc/uptime")
    if not raw:
        return None
    seconds = int(float(raw.split()[0]))
    hours, seconds = divmod(seconds, 3600)
    minutes, _ = divmod(seconds, 60)
    return f"{hours}h {minutes}m"


def get_status():
    """Collect the full hardware snapshot as a dict (all keys optional-safe)."""
    kind, product = detect_device()
    temp, temp_chip = _package_temp()
    total_mb, used_mb = _memory()
    battery = get_battery_state()

    return {
        "device_kind": kind,
        "device_model": product,
        "is_bazzite": is_bazzite(),
        "cpu": _cpu_model(),
        "temp_c": temp,
        "temp_chip": temp_chip,
        "mem_total_mb": total_mb,
        "mem_used_mb": used_mb,
        "power_profile": get_power_profile(),
        "on_ac": is_on_ac_power(),
        "tdp_w": get_tdp(),
        "fan": get_fan_state(),
        "battery": battery,
        "rgb_backends": get_rgb_backends(),
        "uptime": _uptime(),
    }
