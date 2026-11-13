# -*- coding: utf-8 -*-
"""Performance profiles & APU TDP control.

Armoury Crate on Windows offers Silent / Performance / Turbo modes.
On Bazzite Linux those map to:

    * power-profiles-daemon (powerprofilesctl) for the CPU governor
      and platform profile, and
    * ryzenadj for the APU's STAPM/long/short power limits
      (preinstalled on Bazzite handheld images).

Turbo mirrors Armoury Crate behaviour on the ROG Ally: 25 W on
battery, 30 W while plugged in.
"""

import glob
import re

from packages.armoury.system import run, run_privileged, which, _read

# name -> (power-profiles-daemon profile, TDP on battery W, TDP on AC W)
PROFILES = {
    "silent": ("power-saver", 10, 13),
    "performance": ("balanced", 15, 17),
    "turbo": ("performance", 25, 30),
}

# Safety limits (Watts) — wide enough for laptops, sane for handhelds
TDP_MIN = 4
TDP_MAX = 65


def get_power_profile():
    """Active power-profiles-daemon profile, or None when unavailable."""
    if not which("powerprofilesctl"):
        return None
    ok, out, _ = run(["powerprofilesctl", "get"])
    return out if ok else None


def set_power_profile(ppd_profile):
    """Set power-profiles-daemon profile. Returns (ok, message)."""
    if not which("powerprofilesctl"):
        return False, "power-profiles-daemon not found (it ships with Bazzite)"
    ok, _, err = run(["powerprofilesctl", "set", ppd_profile])
    if ok:
        return True, f"Power profile set to '{ppd_profile}'"
    return False, err or f"Failed to set power profile '{ppd_profile}'"


def is_on_ac_power():
    """Best-effort mains power detection."""
    for supply in glob.glob("/sys/class/power_supply/*"):
        ps_type = _read(f"{supply}/type") or ""
        if ps_type in ("Mains", "USB"):
            if _read(f"{supply}/online") == "1":
                return True
        if ps_type == "Battery" and (_read(f"{supply}/status") or "") in (
                "Charging", "Full"):
            return True
    return False


def set_tdp(watts):
    """Apply a sustained/stapn TDP limit via ryzenadj.

    Returns (ok, message). Values are clamped to [TDP_MIN, TDP_MAX].
    """
    if not which("ryzenadj"):
        return False, (
            "ryzenadj not found — it is preinstalled on Bazzite handheld "
            "images; otherwise install it first.")

    try:
        watts = int(watts)
    except (TypeError, ValueError):
        return False, "TDP must be a whole number of watts"
    watts = max(TDP_MIN, min(TDP_MAX, watts))

    milliwatts = watts * 1000
    ok, _, err = run_privileged([
        "ryzenadj",
        f"--stapm-limit={milliwatts}",
        f"--fast-limit={milliwatts}",
        f"--slow-limit={milliwatts}",
    ])
    if ok:
        return True, f"TDP set to {watts}W (STAPM/fast/slow aligned)"
    return False, err or "ryzenadj failed — root privileges are required"


def get_tdp():
    """Current STAPM limit in watts via `ryzenadj --info`, or None."""
    if not which("ryzenadj"):
        return None
    ok, out, _ = run_privileged(["ryzenadj", "--info"])
    if not ok:
        return None
    match = re.search(r"STAPM\s+LIMIT\s*\|\s*([\d.]+)", out)
    if match:
        return int(float(match.group(1)))
    return None


def apply_profile(name):
    """Apply an Armoury-Crate-style profile end to end.

    Returns a list of (ok, message) results for each action taken.
    """
    name = name.lower()
    if name not in PROFILES:
        return [(False,
                 f"Unknown profile '{name}'. Choose from: "
                 + ", ".join(sorted(PROFILES)))]

    ppd, tdp_dc, tdp_ac = PROFILES[name]
    results = [set_power_profile(ppd)]
    watts = tdp_ac if is_on_ac_power() else tdp_dc
    ok, msg = set_tdp(watts)
    if ok:
        msg = f"TDP preset applied: {watts}W ({'AC (plugged in)' if is_on_ac_power() else 'battery'})"
    else:
        msg = f"TDP step skipped: {msg}"
    results.append((ok, msg))
    return results
