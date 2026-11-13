# -*- coding: utf-8 -*-
"""
Steam / Game Mode integration.

Makes My Ally Assistant appear as a game tile in your Steam library —
on Bazzite and Steam Deck that means the Game Mode (SteamOS-style)
console UI. Adds the shortcut to every local Steam account and drops in
library artwork.

Commands:
    steam setup     install terminal wrapper + desktop entry + Steam
                    shortcut + artwork (CLOSE Steam first!)
    steam status    show what is installed
    steam remove    remove the integration

Aliases: gamemode, game mode
"""

from colorama import Fore

from plugin import LINUX, alias, complete, plugin, require
from packages import steamint

SUBCOMMANDS = ("setup", "status", "remove")


def _report(ally, results):
    for ok, message in results:
        ally.say((Fore.GREEN if ok else Fore.RED) + message + Fore.RESET)


@require(platform=LINUX)
@alias("gamemode", "steamdeck")
@complete(*SUBCOMMANDS)
@plugin("steam")
def steam(ally, s):
    """Integrate My Ally Assistant with Steam Game Mode (Bazzite/Steam Deck)."""
    args = s.strip().split()
    sub = args[0].lower() if args else "status"

    if sub == "status":
        ally.say(Fore.CYAN + "Steam / Game Mode integration:" + Fore.RESET)
        _report(ally, steamint.steam_status())
    elif sub == "setup":
        msg = ("Close Steam before continuing "
               "(it overwrites shortcuts.vdf on exit).")
        ally.say(Fore.YELLOW + msg + Fore.RESET)
        messages = []
        steamint.steam_setup(messages)
        _report(ally, messages)
    elif sub == "remove":
        messages = []
        steamint.steam_remove(messages)
        _report(ally, messages)
    else:
        ally.say(f"Unknown steam command '{sub}'.")
        ally.say("Try: steam setup | steam status | steam remove")
