from colorama import Back, Style

from plugin import plugin


@plugin('bmi')
class Bmi:
    """
    Welcome to the Body Mass Index plugin documentation! Here you can find all the functionalitites
    of this plugin.
    Usage: Type bmi, press enter and follow the instructions
    Functionalities: You can calculate your BMI both on metric and imperial system.
    For metric system: Type your height in centimetres and the your weight in kilos,
        they should be both Integers!
    For imperial system: Type your height in feets and inches and then your weight in lbs
        all measurements should be Integers!
    Find out your BMI number and your body state.
    """

    def __call__(self, ally, s):
        ally.say("Welcome. Lets check your BMI")
        system = self.get_system(ally)
        if system == 'metric':
            bmi = self.calc_bmi('m', *self.ask_measurements(ally, "m"))
        elif system == 'imperial':
            bmi = self.calc_bmi('i', *self.ask_measurements(ally, "i"))
        else:
            return
        self.print_body_state(ally, bmi)

    def get_system(self, ally):
        """
        Asks user to choose which system they want to use
        """
        syst = {1: 'metric', 2: 'imperial'}
        ally.say("Metric system: Type your height in centimeter, weight in kg")
        ally.say("Imperial system: Type your height in ft and inches, weight in lbs")
        ally.say("All measurements should be Integers. Default is Metric system")
        print()
        prompt = ("Please choose the system you would like to use.\n"
             " 1: Metric system\n"
             " 2: Imperial system\n"
             " 3: Exit")
        valid_input = False
        while not valid_input:
            try:
                print(prompt)
                c = int(input("Your choice: "))
                print()
                if c != 3:
                    return syst.get(c, 'metric')
                valid_input = True
            except ValueError:
                print("Invalid Input. Please Enter the number")

    def calc_bmi(self, system, height, weight):
        """
        Calculates the bmi for metric system using the common bmi function
        """
        if system == 'm':
            height = height / 100.0
            bmi = 1.0 * weight / height ** 2
        elif system == 'i':
            bmi = 1.0 * weight / height ** 2 * 703
        bmi = round(bmi, 1)
        return bmi

    def print_body_state(self, ally, bmi):
        """
        According the bmi number, print_body_state finds out the state of the body
        and prints it to the user
        """
        print("BMI:", str(bmi))
        if bmi < 16:
            print(Back.RED, " " * 2, Style.RESET_ALL)
            ally.say('Severe thinness')
        elif bmi < 18.5:
            print(Back.YELLOW, " " * 2, Style.RESET_ALL)
            ally.say('Mild thinness')
        elif bmi < 25:
            print(Back.GREEN, " " * 2, Style.RESET_ALL)
            ally.say('Healthy')
        elif bmi < 30:
            print(Back.YELLOW, " " * 2, Style.RESET_ALL)
            ally.say('Pre-obese')
        else:
            print(Back.RED, " " * 2, Style.RESET_ALL)
            ally.say('Obese')

    def ask_measurements(self, ally, s):
        """
        Asks user to input their measurements according to their units.
        """
        if s == "m":
            ally.say("Please insert your height in centimeter: ")
            height = ally.input()
            while True:
                try:
                    height = int(height)
                    if height <= 0:
                        raise ValueError('Please only positive numbers')
                    break
                except ValueError:
                    print("Please, insert a positive integer: ")
                    height = ally.input()
            ally.say("Please insert your weight in kg: ")
            weight = ally.input()
            while True:
                try:
                    weight = int(weight)
                    if weight <= 0:
                        raise ValueError('Please only positive numbers')
                    break
                except ValueError:
                    print("Error on input type for weight, please insert an integer: ")
                    weight = ally.input()
        else:
            ally.say("Please insert your height in ft: ")
            feet = ally.input()
            while True:
                try:
                    feet = int(feet)
                    if feet < 0:
                        raise ValueError('Please only positive numbers!')
                    break
                except ValueError:
                    print("Error on input type for feet, please insert an integer: ")
                    feet = ally.input()
            ally.say("Please insert your height in inches: ")
            inches = ally.input()
            while True:
                try:
                    inches = int(inches)
                    if inches < 0:
                        raise ValueError('Please only positive numbers')
                    break
                except ValueError:
                    print("Error on input type for inches, please insert an integer: ")
                    inches = ally.input()
            ally.say("Please insert your weight in lbs: ")
            weight = ally.input()
            while True:
                try:
                    weight = int(weight)
                    if weight < 0:
                        raise ValueError('Please only positive numbers')
                    break
                except ValueError:
                    print("Error on input type for weight, please insert an integer: ")
                    weight = ally.input()
            height = int(feet) * 12 + int(inches)
            weight = int(weight)
        return height, weight
