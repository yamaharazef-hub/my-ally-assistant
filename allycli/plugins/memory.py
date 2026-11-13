from plugin import plugin
import time
import random
import sys


@plugin('memory')
class Memory:
    """
    Welcome to the Short-Term Memory Trainer! Here you can find
    all the functionalities of this plugin.
    Usage: Type memory, press enter and follow the instructions
    Functionalities: You can train your memory by recalling a
    random generated number.
    Find out how many digits you can remember.
    """

    def __call__(self, ally, s):
        ally.say("Welcome to Memory Trainer.")
        ally.say("We will train you by giving a number to remember.")
        ally.say("The number won't be visible for very long.")
        ally.say("Each time the number will get 1 more digit.")
        answer = self.get_answer(ally)
        if answer == 1:
            self.trainer(ally)
        else:
            return

    def get_answer(self, ally):
        """
        Asks the user you check if he is ready to start the game
        1 for ready, 2 for not ready
        """
        ally.say("Are you ready to play?")
        while True:
            try:
                ally.say("Press 1 for Yes. \nPress 2 for No.")
                c = int(input("Your choice: "))
                if c != 1 and c != 2:
                    raise ValueError('Please give a valid input')
                break
            except ValueError:
                print("Please give a valid input")
        return c

    def trainer(self, ally):
        """
        User guesses the number, checks if the guess is correct.
        First wrong guess means the user has lost.
        """
        lost = False
        number = ""
        while not lost:
            number = self.create_number(ally, number)
            print("The number will only be visible for a few seconds.")
            sys.stdout.write(number)
            sys.stdout.flush()
            time.sleep(2 * len(number))
            sys.stdout.write('\r')
            sys.stdout.flush()
            ally.say("Time ended.")
            guess = str(input("Type your guess:"))
            if guess == number:
                ally.say("Correct guess of " + str(len(number)) + " digits")
            else:
                ally.say("Wrong guess.")
                ally.say("You remembered " + str(len(number) - 1) + " digits")
                ally.say("Be sure to train again.")
                lost = True
        return

    def create_number(self, ally, number):
        """
        Creates new number with one more digit
        """
        new = ""
        i = 0
        while i <= len(number):
            digit = str(random.randint(0, 9))
            new = new + digit
            i = i + 1
        return new
