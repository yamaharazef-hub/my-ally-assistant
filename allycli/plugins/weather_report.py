import requests
from plugin import plugin, alias, require
from colorama import Fore


@require(network=True)
@alias("forecast")
@plugin("weather report")
class WeatherReport:
    """The user will input a location as a string, and the WeatherDB database will be
    used to make a GET request and fetch data. Then, the user can see the weather
    forecast for the upcoming week if they wish."""

    def __call__(self, ally: "AllyAPI", s: str) -> None:
        self.print_weather(ally)

    def print_weather(self, ally: "AllyAPI"):
        ally.say("What city are you located in?")
        ally.say("(Only type the city name, not country/province/state.)")
        loc = ally.input("Enter city name: ")
        loc = loc.lower()
        x = requests.get('https://weatherdbi.herokuapp.com/data/weather/' + loc)
        y = x.json()
        if 'status' in y and y['status'] == 'fail':
            ally.say("Invalid location entered!", color=Fore.RED)
        else:
            ally.say("Location: ", Fore.BLUE)
            ally.say(y['region'] + ", ")
            ally.say("Approx.time: ", Fore.BLUE)
            ally.say(y['currentConditions']['dayhour'] + ", ")
            ally.say("Temperature: ", Fore.BLUE)
            ally.say(str(y['currentConditions']['temp']['c']) + " deg. C, ")
            ally.say("Precipitation: ", Fore.BLUE)
            ally.say(str(y['currentConditions']['precip']) + ", ")
            ally.say("Humidity: ", Fore.BLUE)
            ally.say(str(y['currentConditions']['humidity']) + ", ")
            ally.say("Wind: ", Fore.BLUE)
            ally.say(str(y['currentConditions']['wind']['km']) + " km/h")
            self.ask_for_forecast(ally, y)

    def ask_for_forecast(self, ally: "AllyAPI", jason):
        selected_days = ally.input(
            "Would you like to see the weather forecast "
            "for the next week? Y/N ")
        selected_days = selected_days.lower()
        if selected_days == 'y':
            for p in jason['next_days']:
                ally.say(p['day'] + ": ", Fore.BLUE)
                ally.say(p['comment'] + ", with a min. temp. of " + str(p['min_temp']['c']) +
                           " deg. C and a max.temp. of " + str(p['max_temp']['c']) + " deg. C.")
        elif selected_days == 'n':
            ally.say("Thank you! Goodbye.")
        else:
            ally.say("Invalid input.", color=Fore.RED)
