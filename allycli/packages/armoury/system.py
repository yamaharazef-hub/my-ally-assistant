# -*- coding: utf-8 -*-
"""Device detection and low-level helpers for the Armoury package.

Only Python's standard library is used. All hardware access goes
through sysfs (/sys) or well-known command line tools that Bazzite
ships by default (powerprofilesctl, ryzenadj) or commonly available
utilities (asusctl, OpenRGB).
"""

import glob
import os
import shutil
import subprocess


class Device:
    """Detected device classes — decides which backends we prefer."""
    ALLY = "ally"                  # ROG Ally 2023 (RC71L) — Ryzen Z1 Extreme
    ALLY_X = "ally-x"              # ROG Ally X 2024 (RC72LA) — Ryzen Z1 Extreme
    XBOX_ALLY = "xbox-ally"        # ROG Xbox Ally (RC73YA) — Ryzen Z2 A Go
    XBOX_ALLY_X = "xbox-ally-x"    # ROG Xbox Ally X (RC73XA) — Ryzen AI Z2 Extreme
    ASUS_LAPTOP = "asus-laptop"    # ROG/TUF laptop (asusctl territory)
    GENERIC = "generic"            # anything else


# DMI product-name prefixes -> device class
_HANDHELD_PREFIXES = {
    "RC73XA": Device.XBOX_ALLY_X,
    "RC73YA": Device.XBOX_ALLY,
    "RC73": Device.XBOX_ALLY,      # catch-all for the 2025 Xbox Ally family
    "RC72": Device.ALLY_X,
    "RC71": Device.ALLY,
}

# Human-friendly labels per device class
DEVICE_LABELS = {
    Device.ALLY: "ROG Ally (2023)",
    Device.ALLY_X: "ROG Ally X (2024)",
    Device.XBOX_ALLY: "ROG Xbox Ally (2025)",
    Device.XBOX_ALLY_X: "ROG Xbox Ally X (2025)",
    Device.ASUS_LAPTOP: "ASUS laptop",
    Device.GENERIC: "generic Linux device",
}

# Devices we consider handhelds (used to pick TDP presets)
HANDHELD_DEVICES = (Device.ALLY, Device.ALLY_X,
                    Device.XBOX_ALLY, Device.XBOX_ALLY_X)


def _read(path):
    """Read a sysfs/procfs file, returning stripped text or None."""
    try:
        with open(path, "r") as fh:
            return fh.read().strip()
    except (OSError, UnicodeDecodeError):
        return None


def _write(path, value):
    """Write to a sysfs file. Returns True on success.

    Falls back to `sudo tee` when the file is not writable, which is
    the usual case for hardware control knobs.
    """
    try:
        with open(path, "w") as fh:
            fh.write(str(value))
            fh.flush()
        return True
    except OSError:
        pass

    tee = shutil.which("tee")
    sudo = shutil.which("sudo")
    if tee and sudo:
        result = subprocess.run(
            [sudo, "-n", tee, path],
            input=str(value),
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    return False


def file_writable_or_sudoable(path):
    """Return 'user', 'sudo' or None depending on how we can write."""
    if os.access(path, os.W_OK):
        return "user"
    if shutil.which("sudo"):
        return "sudo"
    return None


def which(cmd):
    """Locate an executable (None if not installed)."""
    return shutil.which(cmd)


def run(cmd, timeout=10):
    """Run a command, returning (ok, stdout, stderr). Never raises."""
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout)
        return proc.returncode == 0, proc.stdout.strip(), proc.stderr.strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, "", str(exc)


def run_privileged(cmd, timeout=10):
    """Run a command as root: directly when already root, else via sudo."""
    if os.geteuid() == 0:
        return run(cmd, timeout)
    sudo = shutil.which("sudo")
    if sudo:
        return run([sudo] + cmd, timeout)
    return False, "", "root privileges required (run Ally with sudo or enable sudo)"


def detect_device():
    """Best-effort device identification via DMI data.

    Returns (Device-kind, product-name). Handhelds are matched against
    ASUS model codes: RC71L = Ally 2023, RC72LA = Ally X 2024,
    RC73XA = Xbox Ally X, RC73YA = Xbox Ally (2025).
    """
    vendor = (_read("/sys/class/dmi/id/sys_vendor") or "").lower()
    product = _read("/sys/class/dmi/id/product_name") or ""
    if "asus" in vendor:
        for code in sorted(_HANDHELD_PREFIXES, key=len, reverse=True):
            if code in product:
                return _HANDHELD_PREFIXES[code], product
        return Device.ASUS_LAPTOP, product
    return Device.GENERIC, product or "Unknown device"


def device_label(kind=None):
    """Display label for a device kind (auto-detected if not given)."""
    if kind is None:
        kind, _ = detect_device()
    return DEVICE_LABELS.get(kind, "generic Linux device")


def is_bazzite():
    """True when running on Bazzite (Fedora Atomic gaming variant)."""
    os_release = _read("/etc/os-release") or ""
    return "bazzite" in os_release.lower()


def find_hwmon(name_hints=()):
    """Yield (hwmon_dir, chip_name) for hwmons whose name matches hint.

    name_hints is matched case-insensitively against the `name` file;
    empty means: yield everything.
    """
    for hwmon in sorted(glob.glob("/sys/class/hwmon/hwmon*")):
        name = (_read(os.path.join(hwmon, "name")) or "").lower()
        if not name_hints or any(hint in name for hint in name_hints):
            yield hwmon, name


def glob_first(pattern):
    """First match for a glob pattern or None."""
    matches = sorted(glob.glob(pattern))
    return matches[0] if matches else None
