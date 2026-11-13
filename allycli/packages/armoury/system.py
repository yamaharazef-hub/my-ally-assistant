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
    ROG_ALLY = "rog-ally"          # ROG Ally handheld (RC71L / RC72LA / X)
    ASUS_LAPTOP = "asus-laptop"    # ROG/TUF laptop (asusctl territory)
    GENERIC = "generic"            # anything else


ROG_ALLY_PRODUCTS = ("RC71", "RC72")


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
    """Best-effort device identification via DMI data."""
    vendor = (_read("/sys/class/dmi/id/sys_vendor") or "").lower()
    product = (_read("/sys/class/dmi/id/product_name") or "")
    if "asus" in vendor:
        if product[:4] in ROG_ALLY_PRODUCTS:
            return Device.ROG_ALLY, product
        return Device.ASUS_LAPTOP, product
    return Device.GENERIC, product or "Unknown device"


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
