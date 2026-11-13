# Converts a given string to a given case.
from plugin import plugin
from colorama import Fore


@plugin("string_convert")
def string_convert(ally, s):
    inputString = str(
        ally.input(
            "Give me a string to convert to another case (supported: UPPER/lower/Title/Sentence)"
        )
    )
    ally.say("1. UPPER CASE")
    ally.say("2. lower case")
    ally.say("3. Title Case")
    ally.say("4. Sentence case")
    userCase = int(ally.input("Enter the number (1-4): "))
    res = ""

    if userCase == 1:
        # UPPER CASE
        res = inputString.upper()
    elif userCase == 2:
        res = inputString.lower()
    elif userCase == 3:
        res = inputString.title()
    else:
        res = inputString.capitalize()

    ally.say("Here is your converted sentence:")
    ally.say(res)
