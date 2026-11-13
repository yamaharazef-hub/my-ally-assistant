from plugin import plugin
import requests
import json
import random
import nltk
from nltk.corpus import words

nltk.download('words')
english_words = set(words.words())

@plugin("word chain game")
def word_chain_game(ally, s):
    if s:
        ally.say("This command does not take arguments. Just type 'word chain game' to start.")
        return

    def is_valid_word(word_to_check):
        api_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word_to_check}"
        try:
            response = requests.get(api_url)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def get_ally_word(starting_letter, used_words):
        possible_words = [word for word in english_words
                          if word.startswith(starting_letter) and word.lower() not in used_words]
        if possible_words:
            return random.choice(possible_words).lower()
        return None

    def get_initial_word():
        initial_words = [
            "example", "banana", "grape", "orange", "kiwi", "apple", "lemon", "melon", "olive", "peach",
            "rhythm", "synergy", "wizard", "oxygen", "quartz", "sphinx", "voyage", "utopia", "yacht", "zebra",
            "azure", "bronze", "crimson", "daisy", "ebony", "frost", "golden", "hazel", "indigo", "jade",
            "amber", "beige", "coral", "denim", "ivory", "khaki", "lavender", "magenta", "ochre", "pearl",
            "apricot", "burgundy", "cyan", "fuchsia", "ginger", "lime", "maroon", "navy", "orchid", "plum"
        ]
        return random.choice(initial_words).lower()

    ally.say("\nLet's play Word Chain! No word repeats allowed in this game.")
    word_chain = []
    score = 0
    last_letter = None
    used_words = set()

    initial_word = get_initial_word()
    current_word = initial_word
    word_chain.append(current_word)
    used_words.add(current_word)
    score += 1
    last_letter = current_word[-1].lower()
    ally.say(f"I'll start! My word is: {current_word}.")

    while True:
        prompt_letter = last_letter.upper() if last_letter else "?"
        user_word = ally.input(f"Your word starting with '{prompt_letter}'? (or 'stop') ").strip().lower()

        if user_word.lower() == 'stop':
            ally.say("Game stopped by player.")
            break

        if not user_word:
            ally.say("You didn't enter a word. Try again or type 'stop'.")
            continue

        if last_letter and user_word[0].lower() != last_letter:
            ally.say(f"Invalid! Word must start with '{prompt_letter}'. Game Over!")
            break

        if user_word in used_words:
            ally.say(f"Invalid! '{user_word}' used already. No repeats! Game Over!")
            break

        if not is_valid_word(user_word):
            ally.say(f"Invalid! '{user_word}' not recognized. Game Over!")
            break

        word_chain.append(user_word)
        used_words.add(user_word)
        score += 1
        last_letter = user_word[-1].lower()
        ally.say(f"Valid word! '{user_word}'. My turn...")

        next_word = get_ally_word(last_letter, used_words)
        if next_word:
            current_word = next_word
            word_chain.append(current_word)
            used_words.add(current_word)
            score += 1
            last_letter = current_word[-1].lower()
            ally.say(f"My word is: {current_word}. Your turn starting with '{last_letter.upper()}'?")
        else:
            ally.say(f"I'm stuck! You win this round!")
            break

    ally.say("\nGame Over!")
    ally.say(f"Word Chain: {', '.join(word_chain)}")
    ally.say(f"Your Score: {score}")
