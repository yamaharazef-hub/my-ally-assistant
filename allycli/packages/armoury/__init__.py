# -*- coding: utf-8 -*-
"""
Armoury Crate for Bazzite Linux — recreated as part of My Ally Assistant.

A modular, stdlib-only reimplementation of ASUS Armoury Crate's core
features for Linux gaming devices (with first-class support for the
ROG Ally running Bazzite):

    * status    — hardware dashboard (APU, temps, fans, battery, profile)
    * profile   — Silent / Performance / Turbo operating modes
    * tdp       — APU TDP control via ryzenadj
    * fan       — fan control via hwmon PWM
    * rgb       — Aura-style RGB lighting (LED classdev / asusctl / OpenRGB)
    * battery   — battery charge limit (e.g. stop at 80%)

Every capability detects the underlying hardware/tools at runtime and
degrades gracefully with a helpful message when not available, so the
assistant never crashes on unsupported devices.
"""

from packages.armoury.system import (  # noqa: F401
    Device,
    detect_device,
    is_bazzite,
)
from packages.armoury.status import get_status  # noqa: F401
from packages.armoury.power import (  # noqa: F401
    PROFILES,
    get_power_profile,
    set_power_profile,
    get_tdp,
    set_tdp,
    apply_profile,
)
from packages.armoury.fan import get_fan_state, set_fan  # noqa: F401
from packages.armoury.lighting import set_rgb, get_rgb_backends, COLORS  # noqa: F401
from packages.armoury.battery import (  # noqa: F401
    get_charge_limit,
    set_charge_limit,
    get_battery_state,
)
