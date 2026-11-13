# -*- coding: utf-8 -*-
"""Battery charge limiting, like Armoury Crate's battery care modes.

ASUS devices (including the ROG Ally with recent kernels) expose
`charge_control_end_threshold` on the battery power_supply node, which
stops charging at e.g. 80% to preserve long-term battery health.
"""

import glob
import os

from packages.armoury.system import _read, _write

THRESHOLD_MIN = 50
THRESHOLD_MAX = 100


def _battery_nodes():
    """Battery power_supply nodes that support a charge threshold."""
    for node in sorted(glob.glob("/sys/class/power_supply/*")):
        ps_type = _read(os.path.join(node, "type"))
        if ps_type != "Battery":
            continue
        threshold = os.path.join(node, "charge_control_end_threshold")
        if os.path.exists(threshold):
            yield node, threshold


def get_charge_limit():
    """Current charge limit in percent, or None when unsupported."""
    for _, threshold in _battery_nodes():
        value = _read(threshold)
        if value and value.isdigit():
            return int(value)
    return None


def set_charge_limit(percent):
    """Set battery charge end threshold. Returns (ok, message)."""
    nodes = list(_battery_nodes())
    if not nodes:
        return False, (
            "Battery charge limit not supported on this device/kernel "
            "(needs charge_control_end_threshold — the ROG Ally supports "
            "this on Bazzite's kernel)")

    try:
        percent = int(percent)
    except (TypeError, ValueError):
        return False, "Charge limit must be a number between 50 and 100"
    if not THRESHOLD_MIN <= percent <= THRESHOLD_MAX:
        return False, f"Charge limit must be between {THRESHOLD_MIN} and {THRESHOLD_MAX}%"

    ok_all = all(_write(threshold, percent) for _, threshold in nodes)
    if ok_all:
        if percent >= 100:
            return True, "Charge limit removed — battery charges to 100%"
        return True, (f"Battery care enabled: charging stops at {percent}% "
                      "(like Armoury Crate's 'Balanced/Maximum Lifespan' mode)")
    return False, "Charge limit not writable (try running Ally with sudo)"


def get_battery_state():
    """Capacity/status of the first battery found, or None."""
    nodes = sorted(glob.glob("/sys/class/power_supply/*"))
    for node in nodes:
        if _read(os.path.join(node, "type")) != "Battery":
            continue
        capacity = _read(os.path.join(node, "capacity"))
        status = _read(os.path.join(node, "status"))
        state = {
            "name": os.path.basename(node),
            "percent": int(capacity) if capacity and capacity.isdigit() else None,
            "status": status,
            "charge_limit": get_charge_limit(),
        }
        return state
    return None
