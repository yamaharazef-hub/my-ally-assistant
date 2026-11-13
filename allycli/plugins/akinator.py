from plugin import plugin, require
from colorama import Fore
import akinator
import subprocess
import sys


"""
Simple akinator text based game: think up a character, answer questions and akinator will find it !
https://pypi.org/project/akinator.py/
"""


@require(network=True)
@plugin("akinator")
def akinator_main(ally, s):

    opening_message(ally)
    ally.say('Press "g" to start, or "q" to quit !')
    while True:
        user_in = ally.input()
        if user_in == 'q':
            ally.say("See you next time :D", Fore.CYAN)
            break
        elif user_in == 'g':
            main_game(ally)
            break
        else:
            ally.say('Press "g" to start, or "q" to quit !')


# Helper methods


def opening_message(ally):
    ''' Messages displayed when akinator called '''

    ally.say('')
    ally.say('Let\'s play !')
    ally.say('You have to think of a public personality,' 
               + ' answer to some questions and I will try to guess who it is !')
    ally.say('Rules: ')
    print_help(ally)


def main_game(ally):
    ''' Handling of the akinator library '''

    aki = akinator.Akinator()
    try:
        q = aki.start_game()
    except (akinator.AkiServerDown, akinator.AkiTechnicalError):
        try:
            q = aki.start_game("en2")  # 2nd server if the 1st is down
        except (akinator.AkiServerDown, akinator.AkiTechnicalError):
            q = aki.start_game("en3")  # 3rd server if the 2nd is down

    # questions loop
    while aki.progression <= 80:
        try:
            a = input(q + "\n")
        except EOFError:
            a = "cantDoThat"
        if a == "b":
            try:
                q = aki.back()
            except akinator.CantGoBackAnyFurther:
                pass
        elif a == "h":
            print_help(ally)
        elif a == "q":
            ally.say("See you next time !")
            return
        else:
            try:
                q = aki.answer(akinator.Answer.from_str(a))
            except akinator.InvalidAnswerError:
                ally.say("answer not understood, type \"h\" for help", Fore.MAGENTA)

    aki.win()

    imageViewerFromCommandLine = {'linux': 'xdg-open',
                                  'win32': 'explorer',
                                  'darwin': 'open'}[sys.platform]  # get an image Viewer
    try:
        subprocess.run([imageViewerFromCommandLine, aki.picture])  # display image of answer
    except Exception:
        pass
    correct = ally.input(f"It's " + aki.first_guess.name +
                           " ! \n" + aki.first_guess.description + "\nWas I correct?\n")
    if correct.lower() == "yes" or correct.lower() == "y":
        ally.say("Yay !!! :D", Fore.GREEN)
    else:
        ally.say("Oups :(", Fore.GREEN)


def print_help(ally):
    ''' Print help '''
    ally.say("To answer, you have the following options: ", Fore.GREEN)
    ally.say("\t \"yes\" or \"y\" or \"0\" for YES", Fore.GREEN)
    ally.say("\t \"no\" or \"n\" or \"1\" for NO", Fore.GREEN)
    ally.say("\t \"i\" or \"idk\" or \"i dont know\" or \"2\" for I DON\'T KNOW", Fore.GREEN)
    ally.say("\t \"probably\" or \"p\" or \"3\" for PROBABLY", Fore.GREEN)
    ally.say("\t \"probably not\" or \"pn\" or \"4\" for PROBABLY NOT", Fore.GREEN)
    ally.say("\t \"q\" to QUIT", Fore.GREEN)
