"""
Ally plugin for clearing the terminal
"""
from plugin import plugin, require, WINDOWS, UNIX
import os


@require(platform=UNIX)
@plugin("clear")
def clear_unix(ally, s):
    # Unix/Linux/MacOS/BSD/etc
    os.system('clear')


@require(platform=WINDOWS)
@plugin("clear")
def clear_windows(ally, s):
    # DOS/Windows
    os.system("cls")
