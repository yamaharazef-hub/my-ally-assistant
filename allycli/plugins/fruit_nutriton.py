from plugin import plugin
from plugin import require,alias,complete
import requests

@require(network=True)
@alias("info on fruits")
@complete("complete0", "complete1")
@plugin("nutrition of fruits")
def nutrition_fruit(ally,s):
    """
    Args:
        ally (obj): Ally assistant 
        s (str): the name of the furit that the user inputs
    Used to retrive infomration about nutrition of fruits and can also be used to compae between fruits 
    """
    API_FRUIT_URL = "https://fruityvice.com/api/fruit/"
    print("Please give a fruit name: ")
    while True:
        # gets the input from user and formats it 
        fruit = input("").strip()
        fruit = fruit.lower()
        print("Loading fruit information...")
        # get info of the specific fruit using the API
        getinfo = requests.get(API_FRUIT_URL + fruit)
        if getinfo.status_code == 404:
            ally.say("Please enter a valid fruit name!.")
            break
        getinfo.raise_for_status()
        # parse the result 
        fruit_data = getinfo.json()
        
       # the fruit info and nutrition info to output 
        ally.say("\nClassifications:")
        ally.say(f"Order: {fruit_data['order']}")
        ally.say(f"Family: {fruit_data['family']}")
        ally.say(f"Genus: {fruit_data['genus']}")
        ally.say("\nnutritions of the fruit per 100 grams:")
        for descrip, value in fruit_data["nutritions"].items():
            ally.say(f"{descrip}: {value}")
        
        # more interactive features 
        prompt = ally.input("\nDo you want to compare this fruit to another fruit? (yes/no): ").strip().lower()
        if prompt == "yes":
            compare_fruit(ally, fruit_data)
            return
        else:
            print("Goodbye!")
            return

def compare_fruit(ally, original_fruit):
    """_summary_

    Args:
        ally (obj): Ally assistant 
        original_fruit (): _description_
    """

    API_FRUIT_URL = "https://fruityvice.com/api/fruit/"
    fruit2 = ally.input("Enter the second fruit for comparison: ").strip().lower()
    response = requests.get(API_FRUIT_URL + fruit2)
    if response.status_code == 404:
        ally.say("Invalid fruit name. Please enter a valid fruit name for comparison.")
    else:
        fruit2_data = response.json()
        ally.say(f"\nComparing {original_fruit['name']} to {fruit2_data['name']}:")
        for descrip, value1 in original_fruit["nutritions"].items():
            value2 = fruit2_data["nutritions"].get(descrip, 0)
            if value1 > value2:
                comparison = "higher"
            elif value1 < value2:
                comparison = "lower"
            else:
                comparison = "the same as"
            ally.say(f"{descrip}: {original_fruit['name']} is {comparison} than {fruit2_data['name']}")
