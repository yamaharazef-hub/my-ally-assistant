from plugin import plugin
from colorama import Fore


@plugin("binary")
def binary(ally, s):
    """
    Converts an integer into a binary number
    """

    if s == "":
        s = ally.input("What's your number? ")

    try:
        n = int(s)
    except ValueError:
        ally.say("This is no number, right?", Fore.RED)
        return
    else:
        if n < 0:
            ally.say("-" + bin(n)[3:], Fore.YELLOW)
        else:
            ally.say(bin(n)[2:], Fore.YELLOW)
