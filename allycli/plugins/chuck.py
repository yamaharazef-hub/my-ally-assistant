import requests
from colorama import Fore
from plugin import alias, plugin, require


@alias("tell joke")
@require(network=True)
@plugin('joke chuck')
def chuck(ally, s):
    """Tell a joke about Chuck Norris"""
    req = requests.get("https://api.chucknorris.io/jokes/random")
    chuck_json = req.json()

    chuck_fact = chuck_json["value"]
    ally.say(chuck_fact, Fore.RED)
