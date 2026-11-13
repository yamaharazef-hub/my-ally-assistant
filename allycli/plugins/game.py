from random import randint

from colorama import Fore

from plugin import alias, plugin


# function for generating 4-digit number
def gen_num():
    a = randint(1, 9)
    b = randint(0, 9)
    c = randint(0, 9)
    d = randint(0, 9)
    while b == a:
        b = randint(0, 9)
    while c == b or c == a:
        c = randint(0, 9)
    while d == a or d == b or d == c:
        d = randint(0, 9)
    return a, b, c, d


# function for checking if there is any match
def check(checker, guess_num, div, md, true_rank, cows, bulls):
    r = int(guess_num % md / div)
    if checker[r] > 0:
        if checker[r] == true_rank:
            bulls += 1
        else:
            cows += 1
    return cows, bulls


@alias("bulls")
@plugin("game")
def bulls_and_cows(ally, s):
    """"""
    ally.say('')
    ally.say('Welcome to text game Bulls and Cows!\n', Fore.GREEN)
    ally.say('Rules of the game:\n', Fore.CYAN)
    ally.say('* You should guess 4-digit number where all digits are different.')
    ally.say('* After each try you will receive the number of matches.')
    ally.say(
        '* If the matching digits are in their right positions, they are "bulls"')
    ally.say('* Otherwise, if in different positions, they are "cows".')
    ally.say('Example:', Fore.CYAN)
    ally.say(
        '\tSecret number: 4271\n\tYour try: 1234\n\tAnswer: 1 bull and 2 cows.')
    ally.say('\tThe bull is "2", the cows are "4" and "1".')
    ally.say('Lets start? Type "g" to start or "q" to quit:', Fore.CYAN)

    while True:
        st = ally.input()
        if st == 'q':
            ally.say('Thank you for playing! New games are coming soon!', Fore.CYAN)
            break
        else:
            tries = int(0)
            a, b, c, d = gen_num()

            # set 'checker' with 10 entries for digits 0-9
            checker = [0] * 10
            checker[a] = int(1)
            checker[b] = int(2)
            checker[c] = int(3)
            checker[d] = int(4)
            ally.say('Secret number was generated!', Fore.CYAN)

            # loop while the secret number is found or user quits
            while True:
                ally.say('Enter your guess, please (type "q" to quit):', Fore.CYAN)
                guess_num = ally.input()
                if guess_num == 'q':
                    ally.say('Thank you for playing!', Fore.CYAN)
                    return

                try:
                    guess_num = int(guess_num)
                except ValueError:
                    ally.say(Fore.RED + 'Invalid guess! ' + Fore.RESET + '(should be a number)')
                    continue

                tries += 1

                cows = int(0)
                bulls = int(0)
                cows, bulls = check(
                    checker, guess_num, 1000, 10000, checker[a], cows, bulls)
                cows, bulls = check(
                    checker, guess_num, 100, 1000, checker[b], cows, bulls)
                cows, bulls = check(
                    checker, guess_num, 10, 100, checker[c], cows, bulls)
                cows, bulls = check(
                    checker, guess_num, 1, 10, checker[d], cows, bulls)
                ally.say(
                    Fore.CYAN
                    + 'Cows: '
                    + str(cows)
                    + '\tBulls: '
                    + str(bulls)
                    + '\n')
                if bulls == 4:
                    ally.say('Congratulations! Your guess is right:', Fore.CYAN)
                    ally.say(
                        '\t'
                        + Fore.GREEN
                        + str(a)
                        + str(b)
                        + str(c)
                        + str(d))
                    ally.say(
                        Fore.CYAN
                        + 'You made '
                        + Fore.GREEN
                        + str(tries)
                        + Fore.CYAN
                        + ' tries.')
                    ally.say('Start a new game or quit? (Type "s" or "q"):', Fore.CYAN)
                    break
