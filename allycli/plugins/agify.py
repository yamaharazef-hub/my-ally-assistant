import requests
from colorama import Fore
from plugin import plugin, require


@require(network=True)
@plugin("agify")
def agify(ally, s):
    """Tells the age of someone based on his name, powered by www.boredapi.com"""

    if s:
        req = requests.get("https://api.agify.io?name=" + s)
        data = req.json()
        if data == "":
            ally.say("Sorry, an error occured", Fore.BLUE)
            return
        response = "I think you are " + str(data.get('age'))

        ally.say(response, Fore.BLUE)

    else:
        ally.say("Please give me the name of someone", Fore.BLUE)
