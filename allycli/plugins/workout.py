import time

from colorama import Fore

from plugin import plugin
from utilities.notification import notify, NOTIFY_NORMAL


def push_compute_rest(maximum):
    if(maximum < 25):
        rest = 30
    elif(maximum < 50):
        rest = 45
    elif(maximum < 75):
        rest = 60
    elif(maximum < 100):
        rest = 75
    else:
        rest = 90
    return rest


def push_compute_num(maximum, ally):
    num = maximum * 2 // 5
    num = int(num)
    return num


def pull_compute_rest(maximum):
    if(maximum < 10):
        rest = 30
    elif(maximum < 15):
        rest = 45
    elif(maximum < 20):
        rest = 60
    elif(maximum < 25):
        rest = 75
    else:
        rest = 90
    return rest


def pull_compute_num(maximum, ally):
    num = maximum * 1.5 // 5
    num = int(num)
    return num


def timer(rest):
    for i in range(rest, 0, -1):
        print(i, "sec left")
        time.sleep(1)


def pushups(ally, s):
    try:
        maximum = int(s)
    except BaseException:
        ally.say("Please enter an integer only!", Fore.BLUE)
        quit(ally)
        return
    if(maximum < 15):
        ally.say(
            "Firstly, try to reach your maximum to at least 15, then call me again!", Fore.BLUE)
        quit(ally)
        return
    num = push_compute_num(maximum, ally)
    rest = push_compute_rest(maximum)
    ally.say("Your program for today is [" + str(num + 2) + ", " + str(num + 1) + ", " + str(num) + ", " + str(
        num - 1) + ", " + str(num - 2) + "] and " + str(rest) + " sec rest in between", Fore.BLUE)
    s = ally.input("Type 's' to start and 'q' for quit\n", Fore.GREEN)
    if (s == "'q'" or s == "q"):
        quit(ally)
    elif (s == "'s'" or s == "s"):
        for i in range(1, 6):
            notify("Start Set " + str(i), "Do " + str(num + 3 - i) +
                   " pushups", urgency=NOTIFY_NORMAL)
            ally.say("Start Set " + str(i) + " - Do " +
                       str(num + 3 - i) + " pushups", Fore.BLUE)
            ally.input("Press enter after finishing", Fore.GREEN)
            ally.say("Rest: " + str(rest) + " sec...", Fore.BLUE)
            ally.say(
                "I will notice you when to start the next set", Fore.BLUE)
            timer(rest)
        ally.say("Well done, you performed " +
                   str(num * 5) + " pushups", Fore.BLUE)
        quit(ally)
    else:
        ally.say(
            "Incorrect input, please write either 'push' or 'pull'", Fore.BLUE)
        quit(ally)


def pullups(ally, s):
    try:
        maximum = int(s)
    except BaseException:
        ally.say("Please enter an integer only!", Fore.BLUE)
        quit(ally)
        return
    if(maximum < 7):
        ally.say(
            "Firstly, try to reach your maximum to at least 7, then call me again!", Fore.BLUE)
        quit(ally)
        return
    num = pull_compute_num(maximum, ally)
    rest = pull_compute_rest(maximum)
    ally.say("Your program for today is [" + str(num + 2) + ", " + str(num + 1) + ", " + str(num) + ", " + str(
        num - 1) + ", " + str(num - 2) + "] and " + str(rest) + " sec rest in between", Fore.BLUE)
    s = ally.input("Type 's' to start and 'q' for quit\n", Fore.GREEN)
    if (s == "'q'" or s == "q"):
        quit(ally)
    elif (s == "'s'" or s == "s"):
        for i in range(1, 6):
            if (num + 3 - i == 0):
                break
            notify("Start Set " + str(i), "Do " + str(num + 3 - i) +
                   " pullups", urgency=NOTIFY_NORMAL)
            ally.say("Start Set " + str(i) + " - Do " +
                       str(num + 3 - i) + " pullups", Fore.BLUE)
            ally.input("Press enter after finishing", Fore.GREEN)
            ally.say("Rest: " + str(rest) + " sec...", Fore.BLUE)
            ally.say(
                "I will notice you when to start the next set", Fore.BLUE)
            timer(rest)
        ally.say("Well done, you performed " +
                   str(num * 5) + " pullups", Fore.BLUE)
        quit(ally)
    else:
        ally.say("Incorrect input, please write either 'push' or 'pull'")
        quit(ally)


def quit(ally):
    ally.say("Stay fit - do workout!", Fore.BLUE)


@plugin("workout")
def workout(ally, s):
    """Provides a workout programm according to user's abilities
    Formula to generate a relevant program is taken from:
    https://www.gbpersonaltraining.com/how-to-perform-100-push-ups/"""
    s = ally.input(
        "Choose an exercise. Write 'push' for pushups, 'pull' for pullups and 'q' for quit\n", Fore.GREEN)
    if (s == "'q'" or s == "q"):
        quit(ally)
    elif (s == "'push'" or s == "push"):
        s = ally.input(
            "How many times can you push up? Please enter an integer!\n", Fore.GREEN)
        pushups(ally, s)
    elif (s == "'pull'" or s == "pull"):
        s = ally.input(
            "How many times can you pull up? Please enter an integer!\n", Fore.GREEN)
        pullups(ally, s)
    else:
        ally.say(
            "Incorrect input, please write either 'push' or 'pull'", Fore.BLUE)
        quit(ally)
