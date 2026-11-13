import random
from plugin import plugin


@plugin('coin flip')
def coin_flip(ally, s):
    """
    Randomizes between Heads and Tails
    """

    options = ('Heads', 'Tails')

    rand_value = options[random.randint(0, 1)]

    ally.say(rand_value)
