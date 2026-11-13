import requests
import datetime
from plugin import plugin, require
from colorama import Fore
from packages.memory.memory import Memory

URL = "https://api-basketball.p.rapidapi.com/"


@require(network=True)
@plugin("basketball")
class basketball():
    """
    Basketball Plugin for getting information about leagues,games and teams
    !!! needs api.basketball.com API_KEY for usage

    """

    def __call__(self, ally, s):
        print("Basketball data provided by the api-basketball.com\n")
        self.get_api_key(ally)
        while True:
            option = self.get_option(ally)
            if option is None:
                return
            self.procces_chosen_option(option, ally)

    def get_headers(self):
        return {"x-rapidapi-host": "api-basketball.p.rapidapi.com", "x-rapidapi-key": self.key}

    def fetch_data(self, route):
        r = requests.get(URL + route, headers=self.get_headers())
        r = r.json()
        if "errorCode" in r.keys():
            return None
        return r

    def get_api_key(self, ally):
        m = Memory("basketball.json")
        if m.get_data("API_KEY") is None:
            user_api_key = ally.input("Enter Api-BasketBall.com API_KEY: ", Fore.GREEN)
            m.add_data("API_KEY", user_api_key)
            m.save()
            self.key = user_api_key
        else:
            self.key = m.get_data("API_KEY")

    def procces_chosen_option(self, option, ally):
        if option == "search_team":
            self.search_team(ally)
        elif option == "list_leagues":
            self.list_leagues(ally)
        elif option == "todays_games":
            self.todays_games(ally)
        elif option == "search_league":
            self.search_league(ally)
        elif option == "new_key":
            self.update_api_key(ally)
        else:
            return

    def update_api_key(self, ally,):
        user_api_key = ally.input("Enter New Api-BasketBall.com API_KEY: ", Fore.GREEN)
        m = Memory("basketball.json")
        m.update_data("API_KEY", user_api_key)
        m.save()
        self.key = user_api_key

    def list_leagues(self, ally):
        ally.spinner_start('Fetching...')
        response = self.fetch_data("leagues")
        if response is None:
            ally.spinner_stop("Error While Loadin Data - Try Again Later.", Fore.YELLOW)
            return
        total_count = response["results"]
        leagues = response["response"]
        ally.spinner_stop("Found {} Leagues".format(total_count))
        for i in range(total_count):
            print(" {}. {} {}".format(i + 1, leagues[i]["country"]["name"], leagues[i]["name"]))

    def search_request(self, ally, query, search_name):
        value = ally.input("Enter {} Name: ".format(search_name), Fore.GREEN)
        while len(value.strip()) < 3:
            print()
            print("The Search {} must be at least 3 characters in length", search_name.lower())
            value = ally.input("Enter {} Name: ".format(search_name), Fore.GREEN)
        ally.spinner_start('Searching...')
        response = self.fetch_data("{}?search={}".format(query, value.strip()))
        if response is None:
            ally.spinner_stop("Error While Searching {} - Try Again Later.".format(search_name), Fore.YELLOW)
            return
        return response

    def search_team(self, ally):
        response = self.search_request(ally, "teams", "Team")
        if response is None:
            return
        found_count = response["results"]
        if found_count == 0:
            ally.spinner_stop("Nothing was Found With Given Name", Fore.YELLOW)
            return
        ally.spinner_stop("Found {} Teams".format(found_count))
        teams = response["response"]
        for i in range(found_count):
            team = teams[i]
            print(" {}. '{}' Country: {}".format(i + 1, team["name"], team["country"]["name"]))

    def search_league(self, ally):
        response = self.search_request(ally, "leagues", "League")
        if response is None:
            return
        found_count = response["results"]
        if found_count == 0:
            ally.spinner_stop("Nothing was Found With Given Name", Fore.YELLOW)
            return
        ally.spinner_stop("Found {} Leagues".format(found_count))
        leagues = response["response"]
        for i in range(found_count):
            league = leagues[i]
            name = league["name"]
            seasons = league["seasons"]
            print(" {}. {} {}".format(i + 1, league["country"]["name"], name))
            if len(seasons) > 0:
                print("  Last {} {} Seasons".format(len(seasons), name))
                for j in range(len(seasons)):
                    print("   Season: {} Start: {} End: {}".format(seasons[j]["season"], seasons[j]["start"], seasons[j]["end"]))

    def todays_games(self, ally):
        ally.spinner_start('Fetching...')
        date = datetime.datetime.now().strftime('%Y-%m-%d')
        response = self.fetch_data("games?date={}".format(date))
        if response is None:
            ally.spinner_stop("Error While Loading Matches - Try Again Later.", Fore.YELLOW)
            return
        total_count = response["results"]
        matches = response["response"]
        if total_count == 0:
            ally.spinner_stop("There is No Matches Today", Fore.YELLOW)
            return
        ally.spinner_stop("Found {} Matches".format(total_count))
        for i in range(total_count):
            match = matches[i]
            time = match["time"]
            country = match["country"]["name"]
            league = match["league"]["name"]
            teams = "{} VS {}".format(match["teams"]["home"]["name"], match["teams"]["away"]["name"])
            print(" {}. {} {} {} {}".format(i + 1, country, league, time, teams))

    def get_option(self, ally):
        options = {1: "todays_games", 2: "search_team", 3: "list_leagues", 4: "search_league", 5: "new_key"}

        print()
        ally.say("How Can I Help You?", Fore.BLUE)
        print()
        print("1: List Todays Games")
        print("2: Search Team By Name")
        print("3: List All Avaliable Leagues")
        print("4: Search League By Name")
        print("5: Insert New API_KEY")
        print("6: Exit ")
        print()
        choice = self.get_choice(ally)
        if choice == -1:
            return
        else:
            return options[choice]

    def get_choice(self, ally):
        while True:
            try:
                inserted_value = int(ally.input("Enter your choice: ", Fore.GREEN))
                if inserted_value == 6:
                    return -1
                elif inserted_value == 1 or inserted_value == 2 or inserted_value == 3 or inserted_value == 4 or inserted_value == 5:
                    return inserted_value
                else:
                    ally.say(
                        "Invalid input! Enter a number from the choices provided.", Fore.YELLOW)
            except ValueError:
                ally.say(
                    "Invalid input! Enter a number from the choices provided.", Fore.YELLOW)
            print()
