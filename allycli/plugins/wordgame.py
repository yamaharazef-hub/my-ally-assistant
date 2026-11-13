import requests
from wonderwords import RandomWord
import time
import enchant
from plugin import plugin, complete, require
from colorama import Fore


    
def generateWord(letter):
    r = RandomWord()
    new_word=r.word(starts_with=letter)
    return new_word

@plugin("word_game")
def word_game(ally,s):
    d = enchant.Dict("en_US")

    continue_playing='Y'
    while continue_playing=='Y' or continue_playing=='y':
        max_seconds_to_answer=int(ally.input("Give how many seconds you would like to have to find your answers \n",color=Fore.GREEN))
        rounds=int(ally.input("Give the number of rounds after which you will win the game \n",color=Fore.GREEN))
        current_rounds=1
        
        while True:
            word=ally.input("Give a word: \n",color=Fore.GREEN)
            if not ((not d.check(word)) or len(word)<2):
                break
            else:
                ally.say("Give a proper word!",color=Fore.RED)

        while current_rounds<=rounds:
            ally.say("Round "+str(current_rounds),color=Fore.YELLOW)
            ally_answer=generateWord(word[len(word)-1])
            ally.say("Ally' answer is: "+ally_answer,color=Fore.YELLOW)

            start_time=time.time()
            word=ally.input("Give a word starting with the letter: \""+str(ally_answer[len(ally_answer)-1])+"\" , You have "+str(max_seconds_to_answer)+" seconds to answer! \n",color=Fore.GREEN)
            end_time=time.time()
            time_to_answer=end_time-start_time
            current_rounds+=1

            if time_to_answer>max_seconds_to_answer:
                ally.say("You were too late to answer! You lost. ",color=Fore.RED)
                break

            if word[0]!=ally_answer[len(ally_answer)-1]:
                ally.say("Your word does not start with the last letter of ally' word! You lost. ",color=Fore.RED)
                break
                
            if (not d.check(word)) or len(word)<2:
                ally.say("Wrong word! You lost. ",color=Fore.RED)
                break 

        if current_rounds>rounds:
            ally.say("Congratulations! You won all "+str(rounds)+" rounds against ally!",color=Fore.YELLOW)

        continue_playing=ally.input("If you want to continue playing press Y/y, otherwise press N/n \n")
        
