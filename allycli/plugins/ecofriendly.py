from plugin import plugin
from colorama import Fore


@plugin('ecofriendly')
class Ecofriendly:
    QUESTIONS = [
        "Do you regularly reduce your water consumption?",
        "Do you turn off lights and electronic devices when you're not using them?",
        "Do you buy products in bulk or with minimal packaging?",
        "Do you try to buy local and seasonal products?",
        "Do you often use sustainable transportation (walking, cycling, public transportation)?",
        "Do you systematically recycle household waste?",
        "Do you compost food scraps or organic waste?",
        "Have you reduced your meat consumption?",
        "Do you avoid plastic bottles and prefer reusable water bottles?",
        "Do you participate in environmental actions in your community?"
    ]

    def __call__(self, ally, s):
        self.intro(ally)
        score = self.ask_questions(ally)
        self.display_score(ally, score)

    def intro(self, ally):
        ally.say("Welcome to the Eco Habits Quiz!", Fore.BLUE)
        ally.say("You'll be asked a series of simple yes/no questions", Fore.BLUE)
        ally.say("to assess how eco-friendly your daily habits are.", Fore.BLUE)
        ally.say("Please answer with 'y' for yes or 'n' for no.", Fore.BLUE)

    def ask_questions(self, ally):
        score = 0
        for question in self.QUESTIONS:
            ally.say(question)
            response = input().lower().strip()
            if response == 'y':
                score += 1
            elif response != 'n':
                ally.say("Please answer with 'y' or 'n'.", Fore.RED)
        return score

    def display_score(self, ally, score):
        if score <= 3:
            ally.say("\nProfile: Beginner", Fore.RED)
            ally.say("Tips: Start with small actions like turning off lights and avoiding single-use plastic.", Fore.GREEN)
        elif score <= 7:
            ally.say("\nProfile: Moderate Eco-Friendly", Fore.CYAN)
            ally.say("Tips: Explore new ways to reduce your carbon footprint, such as composting your waste.", Fore.GREEN)
        else:
            ally.say("\nProfile: Eco-Engaged", Fore.YELLOW)
            ally.say("Tips: Share your experience with others to inspire those around you to follow your example.", Fore.GREEN)

