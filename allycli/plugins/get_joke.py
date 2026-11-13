import pyjokes
from colorama import Fore
from plugin import plugin, require


@require(network=True)
@plugin('joke')
def joke(ally, s):
    """Tells a random joke"""
    joke = pyjokes.get_joke()

    ally.say(joke, Fore.BLUE)
