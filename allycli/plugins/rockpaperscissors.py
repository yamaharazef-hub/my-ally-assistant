import random

from colorama import Back

from plugin import plugin


@plugin('rockpaperscissors')
class rockpaperscissors():
    """
    rockpaperscissors Dcoumentation.
    rockpaperscssors is the game Rock - Paper - Scissors that we all know with Ally as opponent.

    First of all you enter how many rounds you will play (max. 100).
    And then the game starts.
    In every round you will request to enter your move.

    'r' for rock.
    'p' for paper.
    's' for scissors.

    Also you can exit the game whenever you like by entering as move 'exit' and also you can display the score whenever
    you want by entering 'score'.

    You can display the current round by entering 'rounds'.

    """

    def __call__(self, ally, s):
        ally.say("!! Welcome to Rock Paper Scissors !!")
        ally.say("!A game to play with Ally as rival!")

        rounds = self.get_rounds("Enter how many rounds you will play (max. 100): ")

        ally.say("OK")
        ally.say("The game begins")

        user_score = 0
        ally_score = 0

        exit = False

        i = 1

        while(i <= int(rounds)):

            user_move = self.get_users("Enter your move: ")

            if (user_move == 'exit'):
                exit = True
                break

            if (user_move == "score"):
                txt = "You:" + str(user_score) + "  Ally:" + str(ally_score) + "  "
                if (user_score > ally_score):
                    txt = txt + Back.GREEN + "You Winning" + Back.RESET
                elif(user_score < ally_score):
                    txt = txt + Back.RED + "You Losing" + Back.RESET
                else:
                    txt = txt + Back.WHITE + "Tie" + Back.RESET

                ally.say(txt)
                continue

            if (user_move == "rounds"):
                ally.say("The current rounds is " + str(i) + "/" + str(rounds))
                continue

            ally_move = self.get_ally()
            ally.say("Ally move: " + ally_move)

            g = self.game(user_move, ally_move)

            if (g == "W"):
                user_score = user_score + 1
                ally.say("\t" + Back.GREEN + "You WIN" + Back.RESET)
                i = i + 1
            elif (g == "L"):
                ally_score = ally_score + 1
                ally.say("\t" + Back.RED + "Ally WIN" + Back.RESET)
                i = i + 1
            else:
                ally.say("\t" + Back.MAGENTA + "TIE" + Back.RESET)
                i = i + 1

        ally.say("")
        ally.say("\t\t" + "GAME OVER")
        ally.say("\t\t" + "--SCORE--")
        ally.say("\t" + "YOU: " + str(user_score) + "\t" + "ALLY: " + str(ally_score))

        if (user_score > ally_score):
            txt = Back.GREEN + "\t\tYOU WIN!!" + Back.RESET
        elif (user_score < ally_score):
            txt = Back.RED + "\t\tYOU LOSE!" + Back.RESET
        else:
            txt = Back.WHITE + "\t\tTIE" + Back.RESET

        if (exit is True):
            r = str(i - 1)

            if (r == "1"):
                r = r + "st"
            elif (r == "2"):
                r = r + "nd"
            elif (r == "3"):
                r = r + "rd"
            else:
                r = r + "th"
            ally.say("You terminate the game at " + r + " round")

        ally.say(txt)

    def get_rounds(self, prompt):

        while True:
            rounds = input(prompt)
            try:
                if (int(rounds) <= 100):
                    return rounds
                else:
                    prompt = 'Laps should be under 100 \n'
            except:
                prompt = 'Laps should be a number \n'

    def get_users(self, prompt):

        moves = ["rock", "r", "paper", "p", "scissors", "s", "exit", "score", "rounds"]

        while True:
            u = input(prompt).lower()
            if u in moves:
                if (u == "rock"):
                    u = "r"
                elif (u == "paper"):
                    u = "p"
                elif (u == "scissors"):
                    u = "s"
                else:
                    return u

                return u
            else:
                prompt = 'Please enter a valid move: '
                continue

    def get_ally(self):

        moves = ["r", "p", "s"]

        return moves[random.randint(0, 2)]

    def game(self, umove, jmove):

        condition = ""

        if (umove == jmove):
            condition = "T"

        else:
            moves_that_win = {'r': 's', 's': 'p', 'p': 'r'}
            if jmove == moves_that_win[umove]:
                condition = "W"
            else:
                condition = "L"

        return condition
