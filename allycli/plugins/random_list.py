from plugin import plugin
import random
from colorama import Fore


@plugin("random list")
def generate_random_list(ally, str):
    ls = get_user_input(ally)

    if len(ls) <= 1:
        ally.say("Enter at least 2 strings", Fore.RED)
    else:
        random.shuffle(ls)
        for i in ls:
            ally.say(i, Fore.GREEN)


def get_user_input(ally):
    ls = list()
    while True:
        try:
            user_input = ally.input("Enter string (enter \"AllyStop\" to end): ")
            if user_input == "AllyStop":
                break
            ls.append(user_input)
        except ValueError:
            ally.say("Sorry, I didn't understand that.", Fore.RED)
            continue

    return ls
