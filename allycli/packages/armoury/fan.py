# -*- coding: utf-8 -*-
"""Fan control via Linux hwmon PWM interfaces.

Targets the asus-armoury / asus-nb-wmi hwmon used by the ROG Ally and
ROG/TUF laptops (Bazzite's kernel ships both), while remaining a
no-op with a friendly message on other devices.
"""

import os

from packages.armoury.system import find_hwmon, _read, _write

# hwmon chips known to expose a controllable fan PWM
FAN_CHIP_HINTS = ("asus", "asus-armoury", "asus_nb", "k10temp", "thinkpad")

PWM_MANUAL = 1
PWM_AUTO_TRY_ORDER = (2, 0)     # asus-wmi: 2 = automatic; thinkpad: 0


def _find_fan_pwm():
    """Return (pwm_file, pwm_enable_file, label) for the first usable fan."""
    for hwmon, chip in find_hwmon(FAN_CHIP_HINTS):
        for idx in range(1, 4):
            pwm = os.path.join(hwmon, f"pwm{idx}")
            enable = os.path.join(hwmon, f"pwm{idx}_enable")
            if os.path.exists(pwm):
                return pwm, enable if os.path.exists(enable) else None, chip
    return None, None, None


def get_fan_state():
    """Current fan information, or None when no controllable fan exists."""
    pwm_file, enable_file, chip = _find_fan_pwm()
    if pwm_file is None:
        return None

    pwm_dir = os.path.dirname(pwm_file)
    idx = os.path.basename(pwm_file)[3:]
    raw = _read(pwm_file)
    rpm = _read(os.path.join(pwm_dir, f"fan{idx}_input"))
    mode = _read(enable_file) if enable_file else None
    percent = round(int(raw) * 100 / 255) if raw and raw.isdigit() else None
    return {
        "chip": chip,
        "pwm": raw,
        "percent": percent,
        "rpm": int(rpm) if rpm and rpm.isdigit() else None,
        "manual": mode == str(PWM_MANUAL),
        "pwm_file": pwm_file,
    }


def set_fan(value):
    """Set fan speed: 'auto' or a percentage 0-100.

    Returns (ok, message).
    """
    pwm_file, enable_file, chip = _find_fan_pwm()
    if pwm_file is None:
        return False, (
            "No controllable fan found (needs asus-armoury/asus-nb-wmi hwmon; "
            "on Bazzite handhelds you can also use HHD's fan controls).")

    value = str(value).strip().lower()
    if value == "auto":
        for auto_value in PWM_AUTO_TRY_ORDER:
            if enable_file is None or _write(enable_file, auto_value):
                return True, "Fan set to automatic (hardware curve)"
        return False, f"Could not restore automatic fan control ({pwm_file})"

    try:
        percent = int(value)
    except ValueError:
        return False, "Fan speed must be 'auto' or a percentage 0-100"
    if not 0 <= percent <= 100:
        return False, "Fan speed must be between 0 and 100 percent"

    if enable_file is not None and not _write(enable_file, PWM_MANUAL):
        return False, f"Fan is not writable (try running Ally with sudo): {enable_file}"

    pwm_value = round(percent * 255 / 100)
    if not _write(pwm_file, pwm_value):
        return False, f"Fan is not writable (try running Ally with sudo): {pwm_file}"

    if percent == 0:
        return True, ("WARNING: fan set to 0% — monitor temperatures closely "
                      f"(chip: {chip})")
    return True, f"Fan set to {percent}% (chip: {chip})"
