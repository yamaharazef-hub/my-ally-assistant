import random
from plugin import plugin
from colorama import Fore


def delay():  # method to pause after a series of actions have been completed.
    n = input("Press enter to continue")


def wiped_slate(player):  # resets all hands and bets
    player['hands'] = []
    player['suits'] = []
    player['bets'] = []
    return player


def pprinthand(hand, suit, type='visible'):  # returns hand as a string which may or may not be hidden.
    temphand = hand[:]
    for i in range(len(temphand)):
        if temphand[i] == 1 or temphand[i] == 11:
            temphand[i] = 'A'  # 1 or 11 is value of ace.
        temphand[i] = str(temphand[i]) + " of " + suit[i]
    if type == 'visible':
        return str(temphand)
    elif type == 'partially-visible':
        return '[' + str(temphand[0]) + ',hidden]'


def pprinthandlist(handlist, suitlist):  # returns handlist as a string
    newhandlist = []
    for i in range(len(handlist)):
        newhandlist.append(pprinthand(handlist[i], suitlist[i]))
    return str(newhandlist)


def blackjacksum(orig_hand):  # computes the sum by assuming appropriate value of Ace.
    hand = orig_hand[:]
    for i in range(len(hand)):
        if str(hand[i]) in 'JQK':  # converts face card to their value,that is,10.
            hand[i] = 10
    if sum(hand) <= 11:  # of Ace card(either 1 or 11) acc. to the sum.
        for i in range(len(hand)):
            if hand[i] == 1:
                hand[i] = 11
                orig_hand[i] = 11
                break
    elif sum(hand) > 21:
        for i in range(len(hand)):
            if hand[i] == 11:
                hand[i] = 1
                orig_hand[i] = 1
                break
    return sum(hand), orig_hand


def handle_hit(hand, suit, cards, suits, bet):
    newcard = random.choice(cards)
    newsuit = random.choice(suits)
    print("Newcard is", str(newcard) + " of " + newsuit)
    hand[0].append(newcard)
    suit[0].append(newsuit)
    print("Updated hand is", pprinthand(hand[0], suit[0]))
    sum_, hand[0] = blackjacksum(hand[0])
    return move(hand, suit, cards, suits, bet)

def handle_double_down(hand, suit, cards, suits, bet):
    newcard = random.choice(cards)
    newsuit = random.choice(suits)
    print("Newcard is", str(newcard) + " of " + newsuit)
    hand[0].append(newcard)
    suit[0].append(newsuit)
    print("Updated hand is", pprinthand(hand[0], suit[0]))
    sum_, hand[0] = blackjacksum(hand[0])
    print("Your sum is", sum_)
    if sum_ > 21:
        print("You got busted!")
    bet[0] = bet[0] * 2
    print("Your new bet is", bet[0])
    return hand, suit, bet

def handle_split(hand, suit, cards, suits, bet):
    if hand[0][0] != hand[0][1]:
        print("Sorry, you can only split hands with identical cards")
        return move(hand, suit, cards, suits, bet)
    
    if hand[0][0] == 1:
        print("Sorry,you can't split aces")
        return move(hand, suit, cards, suits, bet)

    splitHand1, splitHand2 = [[hand[0][0], random.choice(cards)]], [[hand[0][1], random.choice(cards)]]
    splitSuit1, splitSuit2 = [[suit[0][0], random.choice(suits)]], [[suit[0][1], random.choice(suits)]]
    
    print(f"Newcard for first split is {splitHand1[0][1]} of {splitSuit1[0][1]}")
    print(f"Newcard for second split is {splitHand2[0][1]} of {splitSuit2[0][1]}")
    print("Split hands are", pprinthand(splitHand1[0], splitSuit1[0]), ",", pprinthand(splitHand2[0], splitSuit2[0]))
    
    sum1, splitHand1[0] = blackjacksum(splitHand1[0])
    sum2, splitHand2[0] = blackjacksum(splitHand2[0])
    print(f"Your sum for split 1 is {sum1}")
    print(f"Your sum for split 2 is {sum2}")
    
    bet1, bet2 = bet[:], bet[:]
    splitHand1, splitSuit1, bet1 = move(splitHand1, splitSuit1, cards, suits, bet1)
    splitHand2, splitSuit2, bet2 = move(splitHand2, splitSuit2, cards, suits, bet2)
    
    splitHand1.extend(splitHand2)
    splitSuit1.extend(splitSuit2)
    bet1.extend(bet2)
    return splitHand1, splitSuit1, bet1

def move(hand, suit, cards, suits, bet):
    sum_, hand[0] = blackjacksum(hand[0])
    print("Your hand is", pprinthand(hand[0], suit[0]))
    print("Your sum is", sum_)
    print('---------------------------')
    
    if sum_ > 21:
        print("You got busted!")
        return hand, suit, bet
    if sum_ == 21 and len(hand) == 2:
        print("Blackjack!")
        return hand, suit, bet

    while True:
        choice = input("Press H to Hit, S to Stand, D to Double-Down, P to sPlit\n").upper()
        if choice == 'H':
            return handle_hit(hand, suit, cards, suits, bet)
        elif choice == 'S':
            return hand, suit, bet
        elif choice == 'D':
            return handle_double_down(hand, suit, cards, suits, bet)
        elif choice == 'P':
            return handle_split(hand, suit, cards, suits, bet)
        else:
            print("Please try again with a valid choice.")

@plugin('blackjack')
def blackjack(ally, s):
    ally.say("Welcome to the casino! Let's play blackjack!", Fore.GREEN)
    player = {"hands": [], "suits": [], "bets": [], 'profit': []}
    cards = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K']
    suits = ['spades', 'hearts', 'diamonds', 'clubs']
    choice = 'y'
    delay()

    # Instructions
    ally.say('How to play:', Fore.GREEN)
    ally.say('-->The goal of blackjack is to beat the dealer\'s hand without going over 21.', Fore.CYAN)
    ally.say('-->Face cards are worth 10. Aces are worth 1 or 11, whichever makes a better hand.', Fore.CYAN)
    ally.say('-->Each player starts with two cards, one of the dealer\'s cards is hidden until the end.', Fore.CYAN)
    ally.say('-->To \'Hit\' is to ask for another card. To \'Stand\' is to hold your total and end your turn.',
               Fore.CYAN)
    ally.say('-->If you go over 21 you bust, and the dealer wins regardless of the dealer\'s hand.', Fore.CYAN)
    ally.say('-->If you are dealt 21 from the start (Ace & 10), you got a blackjack.', Fore.CYAN)
    ally.say('-->Blackjack means you win 1.5 the amount of your bet.', Fore.CYAN)
    ally.say('-->Dealer will hit until his/her cards total 17 or higher.', Fore.CYAN)
    ally.say('-->Doubling is like a hit, only the bet is doubled and you only get one more card.', Fore.CYAN)
    ally.say('-->Split can be done when you have two of the same card - the pair is split into two hands.', Fore.CYAN)
    ally.say('-->Splitting also doubles the bet, because each new hand is worth the original bet.', Fore.CYAN)
    ally.say('-->You cannot split two aces.', Fore.CYAN)
    ally.say('-->You can double on a hand resulting from a split, tripling or quadrupling you bet.', Fore.CYAN)

    while choice in "Yy":
        ally.say('Shuffling the cards....', Fore.BLUE)
        ally.say("Let's start the game!", Fore.BLUE)
        # Bets
        ally.say("How much are you betting?", Fore.BLUE)
        bet = ally.input_number()
        player['bets'].append(bet)
        delay()
        ally.say('---------------------------')

        # Cards
        ally.say("Dealing the cards............", Fore.BLUE)
        ally.say("Your cards....", Fore.BLUE)
        hand = [random.choice(cards), random.choice(cards)]
        suit = [random.choice(suits), random.choice(suits)]
        player["hands"].append(hand)
        player["suits"].append(suit)
        ally.say(pprinthand(hand, suit))
        delay()
        ally.say('---------------------------')

        # Dealer's cards
        dealerhand = [random.choice(cards), random.choice(cards)]
        dealersuit = [random.choice(suits), random.choice(suits)]
        ally.say("Dealer hand: " + pprinthand(dealerhand, dealersuit, type='partially-visible'), Fore.MAGENTA)
        delay()
        ally.say('---------------------------')

        # Players' moves
        ally.say("It's your turn, make your choice!", Fore.BLUE)
        player['hands'], player['suits'], player['bets'] = move(player['hands'], player['suits'], cards, suits,
                                                                player['bets'])
        ally.say("Your hands and respective bets for this round are:", Fore.BLUE)
        ally.say(pprinthandlist(player['hands'], player['suits']) + "      " + str(player['bets']), Fore.BLUE)
        delay()
        ally.say('---------------------------')

        # Dealer's moves
        ally.say("Dealer hand: " + pprinthand(dealerhand, dealersuit), Fore.MAGENTA)
        dealersum, dealerhand = blackjacksum(dealerhand)
        ally.say("Dealer's sum is " + str(dealersum), Fore.MAGENTA)
        while dealersum < 17 or (
                dealersum == 17 and 11 in dealerhand):  # condition which determines if dealer hits or not.
            ally.say("Dealer draws another card", Fore.MAGENTA)
            dealerhand.append(random.choice(cards))
            dealersuit.append(random.choice(suits))
            ally.say("Newcard is " + str(dealerhand[-1]) + " of " + str(dealersuit[-1]), Fore.MAGENTA)
            dealersum, dealerhand = blackjacksum(dealerhand)
            ally.say("Dealer's sum is " + str(dealersum), Fore.MAGENTA)
            ally.say("Dealer's hand is " + pprinthand(dealerhand, dealersuit), Fore.MAGENTA)
        delay()
        ally.say('---------------------------')

        # Profit Calculation
        ally.say("Let's see your results ", Fore.BLUE)
        for j in range(len(player['hands'])):
            hand = player['hands'][j]
            suit = player['suits'][j]
            bet = player['bets'][j]
            sum_, hand = blackjacksum(hand)
            dealersum, dealerhand = blackjacksum(dealerhand)
            ally.say("For the hand- " + pprinthand(hand, suit) + '  sum is-' + str(sum_), Fore.BLUE)
            if len(hand) == 2 and sum_ == 21:
                ally.say("Blackjack!", Fore.BLUE)
                profit = bet * 1.5
                player['profit'].append(bet * 1.5)
            elif sum_ > 21:
                ally.say("Busted", Fore.BLUE)
                profit = bet * -1
                player['profit'].append(bet * -1)
            elif dealersum > 21:
                ally.say("Dealer Busted", Fore.BLUE)
                profit = bet * 1
                player['profit'].append(bet * 1)
            elif dealersum > sum_:
                ally.say("You lost", Fore.BLUE)
                profit = bet * -1
                player['profit'].append(bet * -1)
            elif sum_ > dealersum:
                ally.say("You win", Fore.BLUE)
                profit = bet * 1
                player['profit'].append(bet * 1)
            elif sum_ == 21 and dealersum == 21 and len(dealerhand) == 2 and len(hand) > 2:
                ally.say("You lost", Fore.BLUE)
                profit = bet * -1
                player['profit'].append(bet * -1)
            elif sum_ == dealersum:
                ally.say("Push", Fore.BLUE)
                profit = bet * 0
                player['profit'].append(bet * 0)
            ally.say("Profit is- " + str(profit), Fore.BLUE)
        players = wiped_slate(player)
        choice = ally.input("Do you wish to play another round?Y/n \n", Fore.GREEN)

    ally.say("OK then, Let's see the results", Fore.GREEN)
    ally.say('---------------------------')
    profit = sum(player['profit'])
    if profit >= 0:
        ally.say("Your total profit is " + str(profit), Fore.GREEN)
    else:
        ally.say("Your total loss is " + str(profit * -1), Fore.GREEN)
    ally.say("Goodbye, Let's play again sometime!", Fore.GREEN)
