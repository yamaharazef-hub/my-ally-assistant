import random

from colorama import Fore

from plugin import plugin

from halo import Halo

import time

reds = [1, 3, 5, 7, 9, 12, 14, 16, 18,
        19, 21, 23, 25, 27, 30, 32, 34, 36]


@plugin("roulette")
def roulette(ally, s):
    print("")
    cash = 100
    ally.say("~> Hello, it's roulette game", Fore.RED)
    n = input("Press enter to play")
    start_game(ally, cash)


# this function adds "spinning animation" before presenting result
# animation consists of numbers available on roulette board in respective colors
# for 0 and 00 its green, and for others its alternating between red and grey (black wouldn't be visible in terminal)
def spinning_animation(duration):
    frames = [
                 "\033[92m00\033[0m"
             ] + [
                 f'\033[92m{i}\033[0m' if i == 0 or i == "00" else (
                     f'\033[90m{i}\033[0m' if i % 2 == 0 else f'\033[91m{i}\033[0m'
                 ) for i in random.sample(range(37), 37)
             ]

    spinner = Halo(
        text='Spinning...\n',
        spinner={'interval': 700, 'frames': frames}
    )
    spinner.start()
    time.sleep(duration)
    spinner.stop()


def start_game(ally, cash):
    print("")
    ally.say("~> Your start balance is $100", Fore.YELLOW)
    print("")

    while True:
        ally.say("1. Number (win: 36x)", Fore.YELLOW)
        ally.say("2. RED/BLACK (win: 2x)", Fore.YELLOW)
        ally.say("3. ODD/EVEN (win: 2x)", Fore.YELLOW)
        ally.say("4. 1-12 / 13-24 / 25-36 (win: 3x)", Fore.YELLOW)
        ally.say("5. 1-18 / 19-36 (win: 2x)", Fore.YELLOW)
        ally.say("6. Exit game", Fore.YELLOW)
        print("")

        if cash == 0:
            ally.say("You haven't enough money to play", Fore.RED)
            ally.say("Thanks for playing", Fore.RED)
            print("")
            return

        choice = get_user_choice(ally, cash)
        if choice == 6:
            return
        elif choice == 1:
            cash = first_choice(ally, cash)
            ally.say("Current Balance: " + str(cash), Fore.RED)
        elif choice == 2:
            cash = second_choice(ally, cash)
            ally.say("Current Balance: " + str(cash), Fore.RED)
        elif choice == 3:
            cash = third_choice(ally, cash)
            ally.say("Current Balance: " + str(cash), Fore.RED)
        elif choice == 4:
            cash = fourth_choice(ally, cash)
            ally.say("Current Balance: " + str(cash), Fore.RED)
        elif choice == 5:
            cash = fifth_choice(ally, cash)
            ally.say("Current Balance: " + str(cash), Fore.RED)


def get_user_choice(ally, cash):
    while True:
        try:
            option = int(ally.input("Enter your choice: ", Fore.GREEN))
            if option >= 1 and option <= 6:
                return option
            else:
                ally.say(
                    "Invalid input! Enter a number from the choices provided.", Fore.YELLOW)
        except ValueError:
            ally.say(
                "Invalid input! Enter a number from the choices provided.", Fore.YELLOW)


def first_choice(ally, cash):
    print("")
    choice = bet_number(ally)
    ally.say("Your choice: " + str(choice), Fore.RED)
    bet = bet_amount(ally, cash)
    ally.say("Your bet: $" + str(bet), Fore.RED)
    n = input("Press enter to spin roulette")
    result = random.randint(0, 36)
    cash -= bet

    spinning_animation(5)

    print("")
    ally.say("Result: " + str(result), Fore.YELLOW)

    if result == choice:
        cash += bet * 36
        ally.say("WIN: " + str(bet * 36), Fore.GREEN)
    else:
        ally.say("YOU LOST")

    print("")

    return cash


def second_choice(ally, cash):
    print("")
    ally.say("1. RED", Fore.GREEN)
    ally.say("2. BLACK", Fore.GREEN)
    choice = bet_two_choice(ally)

    if choice == 1:
        ally.say("Your choice: RED", Fore.RED)
    else:
        ally.say("Your choice: BLACK", Fore.RED)

    print("")
    bet = bet_amount(ally, cash)
    ally.say("Your bet: $" + str(bet), Fore.RED)
    print("")

    n = input("Press enter to spin roulette")
    result = random.randint(0, 36)
    cash -= bet

    spinning_animation(5)

    print("")
    ally.say("Result: " + str(result), Fore.YELLOW)

    is_red = False
    if result in reds:
        is_red = True

    if (choice == 1 and is_red and result != 0) or (choice == 2 and is_red is False and result != 0):
        cash += bet * 2
        ally.say("WIN: " + str(bet * 2), Fore.GREEN)
    else:
        ally.say("YOU LOST")

    print("")

    return cash


def third_choice(ally, cash):
    print("")
    ally.say("1. ODD", Fore.GREEN)
    ally.say("2. EVEN", Fore.GREEN)
    choice = bet_two_choice(ally)

    if choice == 1:
        ally.say("Your choice: ODD", Fore.RED)
    else:
        ally.say("Your choice: EVEN", Fore.RED)

    print("")
    bet = bet_amount(ally, cash)
    ally.say("Your bet: $" + str(bet), Fore.RED)
    print("")

    n = input("Press enter to spin roulette")
    result = random.randint(0, 36)
    cash -= bet

    spinning_animation(5)

    print("")
    ally.say("Result: " + str(result), Fore.YELLOW)

    if (choice == 1 and result % 2 == 1 and result != 0) or (choice == 2 and result % 2 == 0 and result != 0):
        cash += bet * 2
        ally.say("WIN: " + str(bet * 2), Fore.GREEN)
    else:
        ally.say("YOU LOST")

    print("")

    return cash


def fourth_choice(ally, cash):
    print("")
    ally.say("1. 1-12", Fore.GREEN)
    ally.say("2. 13-24", Fore.GREEN)
    ally.say("2. 25-36", Fore.GREEN)
    choice = bet_three_choice(ally)

    if choice == 1:
        ally.say("Your choice: 1-12", Fore.RED)
    elif choice == 2:
        ally.say("Your choice: 13-24", Fore.RED)
    else:
        ally.say("Your choice: 25-36", Fore.RED)

    print("")
    bet = bet_amount(ally, cash)
    ally.say("Your bet: $" + str(bet), Fore.RED)
    print("")

    n = input("Press enter to spin roulette")
    result = random.randint(0, 36)
    cash -= bet

    spinning_animation(5)

    print("")
    ally.say("Result: " + str(result), Fore.YELLOW)

    if choice == 1:
        if result >= 1 and result <= 12:
            cash += bet * 3
            ally.say("WIN: " + str(bet * 3), Fore.GREEN)
        else:
            ally.say("YOU LOST")
    elif choice == 2:
        if result >= 13 and result <= 24:
            cash += bet * 3
            ally.say("WIN: " + str(bet * 3), Fore.GREEN)
        else:
            ally.say("YOU LOST")
    else:
        if result >= 25 and result <= 36:
            cash += bet * 3
            ally.say("WIN: " + str(bet * 3), Fore.GREEN)
        else:
            ally.say("YOU LOST")

    print("")

    return cash


def fifth_choice(ally, cash):
    print("")
    ally.say("1. 1-18", Fore.GREEN)
    ally.say("2. 19-36", Fore.GREEN)
    choice = bet_two_choice(ally)

    if choice == 1:
        ally.say("Your choice: 1-18", Fore.RED)
    else:
        ally.say("Your choice: 19-36", Fore.RED)

    print("")
    bet = bet_amount(ally, cash)
    ally.say("Your bet: $" + str(bet), Fore.RED)
    print("")

    n = input("Press enter to spin roulette")
    result = random.randint(0, 36)
    cash -= bet

    spinning_animation(5)

    print("")
    ally.say("Result: " + str(result), Fore.YELLOW)

    if (choice == 1 and result >= 1 and result <= 18) or (choice == 2 and result >= 19 and result <= 36):
        cash += bet * 2
        ally.say("WIN: " + str(bet * 2), Fore.GREEN)
    else:
        ally.say("YOU LOST")

    print("")

    return cash


def bet_two_choice(ally):
    while True:
        try:
            print("")
            option = int(ally.input("Enter your choice: ", Fore.GREEN))
            if option == 1 or option == 2:
                return option
            else:
                ally.say(
                    "Invalid input! Enter a number from the choices provided.", Fore.YELLOW)
        except ValueError:
            ally.say(
                "Invalid input! Enter a number from the choices provided.", Fore.YELLOW)


def bet_three_choice(ally):
    while True:
        try:
            print("")
            option = int(ally.input("Enter your choice: ", Fore.GREEN))
            if option == 1 or option == 2 or option == 3:
                return option
            else:
                ally.say(
                    "Invalid input! Enter a number from the choices provided.", Fore.YELLOW)
        except ValueError:
            ally.say(
                "Invalid input! Enter a number from the choices provided.", Fore.YELLOW)


def bet_number(ally):
    while True:
        try:
            option = int(ally.input("Enter your choice (0-36): ", Fore.GREEN))
            if option >= 0 and option <= 36:
                return option
            else:
                ally.say(
                    "Invalid input! Enter a number from the choices provided.", Fore.YELLOW)
        except ValueError:
            ally.say(
                "Invalid input! Enter a number from the choices provided.", Fore.YELLOW)


def bet_amount(ally, cash):
    while True:
        try:
            bet = int(ally.input("Enter your bet: ", Fore.GREEN))
            if bet >= 1 and bet <= cash:
                return bet
            else:
                ally.say(
                    "Invalid input! Enter a bet amount from your cash", Fore.YELLOW)
        except ValueError:
            ally.say(
                "Invalid input! Enter a number from the choices provided.", Fore.YELLOW)
