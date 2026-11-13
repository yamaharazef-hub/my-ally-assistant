from colorama import Fore

from Ally import HISTORY_FILENAME
from plugin import plugin


@plugin('cat his')
def cat_history(ally, s):
    """Prints the history of commands"""
    HISTORY_FILENAME.seek(0)
    history = str(HISTORY_FILENAME.read())
    ally.say(history, Fore.BLUE)
