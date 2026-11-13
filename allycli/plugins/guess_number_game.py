from plugin import plugin
import random
from colorama import Fore


@plugin("guess_number_game")
def helloworld(ally, s):
    display_welcome_message(ally)
    num = random.randint(1, 100)
    lives = get_game_mode(ally)
    
    if lives == 0:  # User chose to exit
        return
        
    start = 1
    end = 100
    show(1, 101, ally)
    ally.say("\n")
    
    number = get_valid_number_input(ally)
    play_game(ally, num, number, lives, start, end)

def display_welcome_message(ally):
    ally.say("Hello let's play  guess the number.", Fore.BLUE)
    ally.say("I am thinking of a number between 1-100 and you have to guess it.", Fore.BLUE)
    ally.say("Every time you guess, i will inform you if the number you guessed", Fore.BLUE)
    ally.say("is bigger or smaller than the one i am thinking.", Fore.BLUE)
    ally.say("Let's start the game!", Fore.BLUE)
    ally.say("To Exit the game type exit.", Fore.BLUE)
    ally.say("----------------------------", Fore.BLUE)

def get_game_mode(ally):
    hearts = ally.input("Choose mode: Hard(6 lives) or Normal(8 lives)", Fore.GREEN).lower()
    while hearts not in ['hard', 'normal', 'exit']:
        ally.say("I can't understand you. Can you tell me again?", Fore.BLUE)
        hearts = ally.input("Choose mode: Hard(6 lives) or Normal(8 lives)", Fore.GREEN).lower()
    
    if hearts == 'hard':
        return 6
    elif hearts == 'normal':
        return 8
    return 0  # Exit case

def get_valid_number_input(ally, prompt="give me a number between(1-100):"):
    number = ally.input(prompt, Fore.GREEN)
    while not number.isnumeric():
        ally.say("Your input was not a number", Fore.BLUE)
        number = ally.input(prompt, Fore.GREEN)
    return int(number)

def play_game(ally, num, number, lives, start, end):
    while number != num and lives > 1:
        if number < start or number > end:
            ally.say("Your number is out of bounds")
            output = f"Give a number between[{start}-{end}]"
            ally.say(output, Fore.BLUE)
            number = get_valid_number_input(ally)
            continue

        lives -= 1
        if num < number:
            ally.say("The number that i am thinking is smaller than the one you guessed", Fore.BLUE)
            end = number - 1
        else:
            ally.say("The number that i am thinking is bigger than the one you guessed", Fore.BLUE)
            start = number + 1
            
        show(start, end + 1, ally)
        ally.say("")
        ally.say(f"make the next guess (lives:{lives})", Fore.BLUE)
        number = get_valid_number_input(ally)

    if number == num:
        ally.say("You found it!", Fore.BLUE)
    elif lives == 1:
        ally.say("You lost!", Fore.BLUE)

def show(start, end, ally):
    c = 1
    output = ""
    if start > 1:
        for i in range(0, start - 1, 1):
            output += "X   "
            if c % 20 == 0 and i != 0:
                output += "\n"

            c = c + 1
    for i in range(start, end, 1):
        output += str(i) + "  "
        if i % 20 == 0:
            output += "\n"
        if i < 10:
            output += " "
        c = c + 1
    if end <= 100:
        for i in range(end, 101, 1):
            output += "X   "
            if c % 20 == 0 and i != 0:
                output += "\n"
            c = c + 1

    ally.say(output)
