# All plugins should inherite from this library
import requests, json
from colorama import Fore
from plugin import alias, plugin, require
# This is the standard form of a plugin for ally

# Anytime you make a change REMEMBER TO RESTART Ally

# You can run it through ally by the name
# in the @plugin tag.


class ProtonCompatibleGame:

    def getAppIdFromTitle(self,ally):
        ally.say("Warning: This option may not find the game or find an incorrect game. "
                   + "Find the game's AppId from Steam for accurate results!"
                   ,color=Fore.RED)
        title=ally.input("Enter Game Title: ",color=Fore.GREEN).strip();
        games = requests.get("https://protondb.max-p.me/games").text
        games = json.loads(games) 
        for game in games:
            if (game["title"]==title):
                return game["appId"]
        return -1

    def getRating(self,ally,appid):
        try:
            ally.say("Game appId: "+str(appid),Fore.YELLOW)
            url="https://www.protondb.com/api/v1/reports/summaries/"+str(appid)+".json"
            rating=requests.get(url).json()
            ally.say("ProtonDB Rating: "+rating["tier"],Fore.YELLOW)
        except:
            ally.say("Invalid AppId or there are no ratings for this game",color=Fore.RED)

    def run(self,ally):
        ally.say("1. Give Steam game AppId",color=Fore.YELLOW)
        ally.say("2. Give Steam game Title",color=Fore.YELLOW)
        ally.say("3. Close.",color=Fore.YELLOW)
        choice=ally.input("Enter your choice: ",color=Fore.GREEN).strip();
        while (choice<"1" or choice>"3"):
            ally.say("Invalid choice!",color=Fore.RED)
            choice=ally.input("Enter your choice: ",color=Fore.GREEN).strip();
        if (choice =="1"):
            id=ally.input("Enter Game AppId: ",color=Fore.GREEN).strip();
            self.getRating(ally,id)
        elif (choice == "2"):
            appid=self.getAppIdFromTitle(ally)
            if (appid!=-1):
                self.getRating(ally,appid)
            else:
                ally.say(
                    "This game does not exist or there are no ratings for this game",
                    color=Fore.RED
                )

@alias('Proton compatible game')
@require(network=True)
@plugin('Proton game')

def my_plugin(ally, s):
    ProtonCompatibleGame().run(ally)

