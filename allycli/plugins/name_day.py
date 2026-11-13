from colorama import Fore
from plugin import plugin, require
import requests
import re


@require(network=True)
@plugin("name day")
class NameDay:
    """
    Name Day plugin provides information about your country's name days

    You can see today's, tomorrow's, or any other day's name day.

    You can also see the name day of a specific name.
    """
    def __call__(self, ally, s):
        self.ally = ally
        self.main()

    def __init__(self):
        self.ally = None
        self.location = ""
        self.countries = {
            "Austria": "at",
            "Bulgaria": "bg",
            "Croatia": "hr",
            "Czech Republic": "cz",
            "Denmark": "dk",
            "Estonia": "ee",
            "Finland": "fi",
            "France": "fr",
            "Germany": "de",
            "Greece": "gr",
            "Hungary": "hu",
            "Italy": "it",
            "Latvia": "lv",
            "Lithuania": "lt",
            "Poland": "pl",
            "Russia": "ru",
            "Slovakia": "sk",
            "Spain": "es",
            "Sweden": "se",
            "United States": "us"
        }

    def main(self):

        if self.location == "":
            self.get_location()
        while True:
            # main menu
            self.ally.say("It appears you are in " + self.location, color=Fore.BLUE)
            self.ally.say("1 See Today's name days")
            self.ally.say("2 See Tomorrow's name days")
            self.ally.say("3 Chose specific date")
            self.ally.say("4 Chose specific name")
            self.ally.say("5 Chose an other country")
            self.ally.say("6 Exit")

            # get user input
            try:
                inp = int(self.ally.input("Select the desired number: ", color=Fore.GREEN))
            except ValueError:
                self.ally.say("Please select a number")
                continue

            # handle input
            if inp == 1:
                self.today()
            elif inp == 2:
                self.tomorrow()
            elif inp == 3:
                self.specific_date()
            elif inp == 4:
                self.specific_name()
            elif inp == 5:
                self.change_country()
                continue
            elif inp == 6:
                break
            else:
                self.ally.say("Please select a valid number")

            # ask user if he wants to continue
            inp = self.ally.input("Do you want to continue? (Y/N)", color=Fore.RED)
            if inp.lower() == "n":
                break

    def get_country_code(self):
        """Return the two letter country code"""
        return self.countries[self.location]

    def get_location(self):
        """
        Get the location of the user.
        If the user is in a supported country, the country is saved in location class variable.
        otherwise, the user is asked to enter a country from the supported list.
        """
        self.ally.say("Getting Location ... ")
        send_url = 'http://api.ipstack.com/check?access_key=f16ebe59174140a634827d674e605350&output=json&legacy=1'
        js = requests.get(send_url).json()
        loc = js["country_name"]

        if loc in self.countries.keys():
            self.location = loc
        else:
            self.ally.say("It appears you are in " + loc)
            self.ally.say("Your Country is not supported")
            self.ally.say("Please chose an other country")
            self.change_country()

    def today(self):
        """
        Show the name days for today.
        """
        country_code = self.get_country_code()
        j = requests.get("https://nameday.abalin.net/api/V1/today",
                         params={"country": country_code}).json()
        names = j["nameday"][country_code]
        if names != "n/a":
            self.ally.say("Say some kind words to " + names)
        else:
            self.ally.say("No name days today in " + str(self.location))

    def tomorrow(self):
        """
        Show the name days for tomorrow.
        """
        country_code = self.get_country_code()
        j = requests.get("https://nameday.abalin.net/api/V1/tomorrow",
                         params={"country": country_code}).json()
        names = j["nameday"][country_code]
        if names != "n/a":
            self.ally.say("Say some kind words to " + names)
        else:
            self.ally.say("No name days for tomorrow in " + str(self.location))

    def specific_date(self):
        """
        Show the name days for a specific date.
        """
        country_code = self.get_country_code()
        self.ally.say("Please enter day/month")
        try:
            day, month = re.split(r'[ /-]+', self.ally.input().strip())
            self.check_if_date_is_valid(day, month)
        except ValueError:
            self.specific_date()
            return
        j = requests.get("https://nameday.abalin.net/api/V1/getdate",
                         params={"country": country_code, "day": day, "month": month}).json()
        names = j["nameday"][country_code]
        if names != "n/a":
            self.ally.say("Say some kind words to " + names + " on " + day + "/" + month)
        else:
            self.ally.say("No name days at " + day + "/" + month + " in " + self.location)

    def specific_name(self):
        """
        Show the name days for a specific name.
        """
        country_code = self.get_country_code()
        self.ally.say("Please enter name")
        name = self.ally.input().strip()
        j = requests.get("https://nameday.abalin.net/api/V1/getname",
                         params={"country": country_code, "name": name}).json()

        # the same name may have multiple name days
        if j["0"]:
            dates = ""
            for s in j["0"]:
                date = str(s["day"]) + "/" + str(s["month"]) + " "
                dates += date.strip()
            self.ally.say("Say some kind words to " + name + " at " + dates)
        else:
            self.ally.say("No name days found for " + name)

    def change_country(self):
        """
        Change the location of the user manually.
        """
        self.ally.say("Select your country number from the list below:")
        for i, key in enumerate(self.countries.keys(), start=1):
            self.ally.say(str(i) + " " + key)
        self.ally.say(str(len(self.countries) + 1) + " Cancel")

        while True:
            country = int(self.ally.input("Select your country number: "))
            if country in range(1, len(self.countries) + 2):
                break
            else:
                self.ally.say("Please select a valid country number")

        if country == len(self.countries) + 1:
            return
        self.location = list(self.countries.keys())[country - 1]

    def check_if_date_is_valid(self, day, month):
        """
        Check if the date taken for user is valid.
        :raise ValueError: if the date is invalid.
        """
        day = int(day)
        month = int(month)
        m31 = [1, 3, 5, 7, 8, 10, 12]
        m30 = [4, 6, 9, 11]
        if month in m31:
            if 0 > day or day > 31:
                self.ally.say("Please enter a valid date")
                raise ValueError
        elif month in m30:
            if 0 > day or day > 30:
                self.ally.say("Please enter a valid date")
                raise ValueError
        elif month == 2:
            if 0 > day or day > 29:
                self.ally.say("Please enter a valid date")
                raise ValueError
        else:
            self.ally.say("Please enter a valid date")
            raise ValueError
