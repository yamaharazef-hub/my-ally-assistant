from plugin import plugin
from colorama import Fore
import requests



@plugin("fact")
def hello_world(ally,s):
    url = 'https://uselessfacts.jsph.pl/random.json?language=en'
    resp = requests.get(url)

    if resp.status_code == 200:
        data = resp.json()
        ally.say(data['text'])

    else:
        ally.say("No fact was encountered",Fore.RED)


                