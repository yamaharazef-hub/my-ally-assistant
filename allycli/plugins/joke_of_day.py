import requests
from colorama import Fore

from plugin import plugin, require


@require(network=True)
@plugin('joke daily')
class joke_of_day:
    """
    Provides you with a joke of day to help you laugh amidst the
    daily boring schedule

    Enter 'joke daily' to use

    """

    def __call__(self, ally, s):
        ally.say("Welcome To The Plugin Joke Of Day!", Fore.CYAN)
        ally.say("Jokes provided by jokes.one API", Fore.CYAN, False)
        print()
        joke_fetch = self.get_joke(ally)
        if joke_fetch is not None:
            self.joke(ally, joke_fetch)

    def get_joke(self, ally):
        while True:
            url = "https://api.jokes.one/jod"
            ally.spinner_start('Fetching')
            r = requests.get(url)
            if r is None:
                ally.spinner.stop()
                ally.say(
                    "Error in fetching joke - try again! later", Fore.RED)
            ally.spinner_stop()
            return r.json()

    def joke(self, ally, joke_fetch):
        title = joke_fetch["contents"]["jokes"][0]["joke"]["title"]
        joke = joke_fetch["contents"]["jokes"][0]["joke"]["text"]
        print()
        ally.say("Title: " + title, Fore.BLUE)
        print()
        ally.say(joke, Fore.YELLOW)
