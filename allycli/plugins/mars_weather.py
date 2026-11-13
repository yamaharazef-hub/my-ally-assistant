import requests
from colorama import Fore
from plugin import plugin, require
import datetime

API_KEY = 'OsZ9DfFtdgR6zPlVjxFTch1Np5zAcqt9g9i34ga2'
headers = {'X-Auth-Token': API_KEY}
url = 'https://api.nasa.gov/insight_weather/?api_key=OsZ9DfFtdgR6zPlVjxFTch1Np5zAcqt9g9i34ga2&feedtype=json&ver=1.0'


@require(network=True)
@plugin('mars weather')
def mars_weather(ally, s):
    print("")
    ally.say("~> I'll show you MARS weather forecast", Fore.RED)
    print("")

    r = fetch()
    x = r['sol_keys']

    count = 0

    for i in x:
        dt = str(datetime.date.today() + datetime.timedelta(days=count))
        ally.say(dt, Fore.BLUE)

        season = "SEASON: " + r[i]['Season']
        ally.say(season, Fore.BLUE)
        print("")

        get_temperature(ally, r, i)
        print("")

        get_wind(ally, r, i)
        print("")

        get_pressure(ally, r, i)
        print("")

        count += 1


def fetch():
    r = requests.get(url, headers=headers)
    r = r.json()
    if "errorCode" in r.keys():
        return None
    return r


def get_temperature(ally, fulldata, sol):
    ally.say("TEMPERATURE:", Fore.RED)
    temperature = fulldata[sol]['AT']

    avg = "AVG temp: " + str(round(temperature['av'], 1)) + " ºF"
    ct = "Recorded samples: " + str(temperature['ct'])
    min_temp = "MIN temp: " + str(round(temperature['mn'], 1)) + " ºF"
    max_temp = "MAX temp: " + str(round(temperature['mx'], 1)) + " ºF"

    ally.say(avg, Fore.RED)
    ally.say(min_temp, Fore.RED)
    ally.say(max_temp, Fore.RED)
    ally.say(ct, Fore.RED)


def get_wind(ally, fulldata, sol):
    ally.say("WIND:", Fore.GREEN)
    wind = fulldata[sol]['HWS']

    avg = "AVG speed: " + str(round(wind['av'], 1)) + " mph"
    ct = "Recorded samples: " + str(wind['ct'])
    min_speed = "MIN speed: " + str(round(wind['mn'], 1)) + " mph"
    max_speed = "MAX speed: " + str(round(wind['mx'], 1)) + " mph"

    ally.say(avg, Fore.GREEN)
    ally.say(min_speed, Fore.GREEN)
    ally.say(max_speed, Fore.GREEN)
    ally.say(ct, Fore.GREEN)


def get_pressure(ally, fulldata, sol):
    ally.say("PRESSURE:", Fore.YELLOW)
    pressure = fulldata[sol]['PRE']

    avg = "AVG pressure: " + str(round(pressure['av'], 1)) + " Pa"
    ct = "Recorded samples: " + str(pressure['ct'])
    min_pressure = "MIN pressure: " + str(round(pressure['mn'], 1)) + " Pa"
    max_pressure = "MAX pressure: " + str(round(pressure['mx'], 1)) + " Pa"

    ally.say(avg, Fore.YELLOW)
    ally.say(min_pressure, Fore.YELLOW)
    ally.say(max_pressure, Fore.YELLOW)
    ally.say(ct, Fore.YELLOW)
