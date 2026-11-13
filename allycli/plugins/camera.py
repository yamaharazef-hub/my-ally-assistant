import os
from colorama import Fore
from plugin import plugin, require, LINUX, MACOS, WINDOWS


@require(native="cheese", platform=LINUX)
@plugin('open camera')
def open_camera__LINUX(ally, s):
    """Ally will open the camera for you."""
    ally.say("Opening cheese.......", Fore.RED)
    os.system("cheese")


@require(platform=MACOS)
@plugin('open camera')
def open_camera__MAC(ally, s):
    """Ally will open the camera for you."""
    os.system('open /Applications/Photo\\ Booth.app')


@require(platform=WINDOWS)
@plugin('open camera')
def open_camera__WINDOWS(ally, s):
    """Ally will open the camera for you."""
    ally.say("Opening Camera app...", Fore.RED)
    os.system('start microsoft.windows.camera:')
