import os
from colorama import Fore
from plugin import plugin, require, LINUX, MACOS

@require(native="gedit", platform=LINUX)
@plugin('open notes')
def open_notes__LINUX(ally, s):
    """Ally will open the notes application for you."""
    ally.say("Opening notes.......", Fore.GREEN)
    os.system("gedit")

@require(platform=MACOS)
@plugin('open notes')
def open_notes__MAC(ally, s):
    """Ally will open the Notes app for you."""
    ally.say("Opening Notes.......", Fore.GREEN)
    os.system('open /Applications/Notes.app')
