# -*- coding: utf-8 -*-
"""
Armoury Crate — recreated for Bazzite Linux.

ASUS' Armoury Crate controls performance modes, TDP, fans, RGB
lighting and battery care. This plugin brings the same experience to
Bazzite (and other Linux distros), tuned for the ROG Ally but working
on ASUS laptops and generic hardware too.

Commands:
    armoury                    Status dashboard + quick menu
    armoury status             Hardware dashboard
    armoury profile <mode>     silent | performance | turbo
    armoury tdp <watts>        Set APU TDP limit (4-65W, needs root)
    armoury fan <0-100|auto>   Fan speed percent or automatic mode
    armoury rgb <colour|#hex>  Aura-style lighting colour ('off' to disable)
    armoury battery <50-100>   Battery charge limit (100 removes limit)
    armoury help               Show this help

Aliases: armory
"""

from colorama import Fore, Style

from plugin import LINUX, alias, complete, plugin, require
from packages import armoury

SUBCOMMANDS = ("status", "profile", "tdp", "fan", "rgb", "battery", "help")


def _fmt_temp(status):
    if status["temp_c"] is None:
        return "N/A"
    return f"{status['temp_c']}°C ({status['temp_chip']})"


def _fmt_battery(status):
    battery = status["battery"]
    if battery is None:
        return "N/A"
    line = f"{battery['percent']}% — {battery['status']}"
    if battery.get("charge_limit") not in (None, 100):
        line += f" (charge limit: {battery['charge_limit']}%)"
    return line


def _show_dashboard(ally):
    status = armoury.get_status()

    ally.say("")
    ally.say(Fore.MAGENTA + Style.BRIGHT
             + "    ⚔  ARMOURY CRATE  —  Ally Edition (Bazzite/Linux)" + Fore.RESET)
    label = armoury.device_label(status["device_kind"])
    known = status["device_kind"] != armoury.Device.GENERIC
    bazzite_tag = (" | Bazzite ✓" if status["is_bazzite"]
                   else " | (not Bazzite — works anyway)")
    model = status["device_model"]
    if model != "Unknown device":
        device_line = f"{model} — {label}"
    else:
        device_line = label
    if known:
        device_line += " ✓"
    ally.say(Fore.CYAN + f"    {device_line}{bazzite_tag}"
             + Fore.RESET)
    ally.say(Fore.MAGENTA + "    " + "─" * 52 + Fore.RESET)

    fan = status["fan"]
    fan_text = "N/A"
    if fan:
        rpm = f"{fan['rpm']} RPM" if fan["rpm"] is not None else "speed set"
        fan_text = f"{rpm} — {fan['percent']}% ({'manual' if fan['manual'] else 'auto'})"

    tdp = f"{status['tdp_w']}W" if status["tdp_w"] is not None else "N/A (needs sudo/ryzenadj)"
    profile = status["power_profile"] or "N/A"
    ac = "AC" if status["on_ac"] else "battery"

    ally.say(f"    APU/CPU : {status['cpu']}")
    ally.say(f"    Temp    : {_fmt_temp(status)}    Fan: {fan_text}")
    ally.say(f"    Profile : {profile}   TDP: {tdp}   Source: {ac}")
    ally.say(f"    Battery : {_fmt_battery(status)}")
    ally.say(f"    Memory  : {status['mem_used_mb']} / {status['mem_total_mb']} MB"
             f"    Uptime: {status['uptime'] or 'N/A'}")
    rgb = ", ".join(status["rgb_backends"]) if status["rgb_backends"] else "none detected"
    ally.say(f"    RGB     : {rgb}")
    ally.say(Fore.MAGENTA + "    " + "─" * 52 + Fore.RESET)
    ally.say(Fore.CYAN + "    Quick actions:" + Fore.RESET)
    ally.say("      armoury profile silent|performance|turbo")
    ally.say("      armoury tdp 15        armoury fan 60")
    ally.say("      armoury rgb green     armoury battery 80")
    ally.say(Fore.CYAN + "    ('armoury help' for the full command list)" + Fore.RESET)


def _show_help(ally):
    ally.say(Fore.CYAN + "⚔ Armoury Crate commands (Bazzite/Linux):" + Fore.RESET)
    for line in (
        "  armoury                    — status dashboard + quick menu",
        "  armoury status             — hardware dashboard",
        "  armoury profile silent|performance|turbo",
        "                               (power-profiles-daemon + TDP preset with",
        "                                your device's official wattage, e.g. turbo",
        "                                = 25W battery / 35W AC on Xbox Ally X)",
        "  armoury tdp <4-65>         — APU TDP limit in watts (sudo)",
        "  armoury fan <0-100|auto>   — fan speed % (sudo)",
        "  armoury rgb <colour>       — " + ", ".join(sorted(armoury.COLORS)),
        "  armoury rgb #FF8800        — custom static colour",
        "  armoury battery <50-100>   — battery care charge limit (sudo)",
    ):
        ally.say(line)


def _report_results(ally, results):
    overall_ok = True
    for ok, message in results:
        ally.say((Fore.GREEN if ok else Fore.RED) + message + Fore.RESET)
        overall_ok = overall_ok and ok
    return overall_ok


@require(platform=LINUX)
@alias("armory")
@complete(*SUBCOMMANDS)
@plugin("armoury")
def armoury_crate(ally, s):
    """Armoury Crate recreated for Bazzite Linux: profiles, TDP, fan, RGB, battery care."""
    args = s.strip().split()
    sub = args[0].lower() if args else "status"

    if sub == "status":
        _show_dashboard(ally)
    elif sub == "help":
        _show_help(ally)
    elif sub == "profile":
        if len(args) < 2:
            current = armoury.get_power_profile() or "unknown"
            ally.say(f"Current power profile: {current}")
            ally.say("Usage: armoury profile silent|performance|turbo")
            return
        _report_results(ally, armoury.apply_profile(args[1]))
    elif sub == "tdp":
        if len(args) < 2:
            tdp = armoury.get_tdp()
            ally.say(f"Current TDP: {tdp}W" if tdp is not None
                     else "Current TDP unreadable (needs sudo/ryzenadj)")
            ally.say("Usage: armoury tdp <watts>   e.g. armoury tdp 15")
            return
        _report_results(ally, [armoury.set_tdp(args[1])])
    elif sub == "fan":
        if len(args) < 2:
            ally.say("Usage: armoury fan <0-100>|auto")
            return
        _report_results(ally, [armoury.set_fan(args[1])])
    elif sub == "rgb":
        if len(args) < 2:
            backends = armoury.get_rgb_backends()
            ally.say("RGB backends: " + (", ".join(backends) if backends else "none"))
            ally.say("Usage: armoury rgb <colour>|off|#RRGGBB")
            return
        _report_results(ally, [armoury.set_rgb(args[1])])
    elif sub == "battery":
        if len(args) < 2:
            limit = armoury.get_charge_limit()
            ally.say(f"Current charge limit: {limit}%" if limit is not None
                     else "Charge limit not supported on this device")
            ally.say("Usage: armoury battery <50-100>")
            return
        _report_results(ally, [armoury.set_charge_limit(args[1])])
    else:
        ally.say(f"Unknown armoury command '{sub}'.")
        _show_help(ally)
