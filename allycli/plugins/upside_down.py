from plugin import plugin
from colorama import Fore


@plugin('upside down')
def generate_random_list(ally, str):
    user_input = ally.input(
        "Enter string to be converted to upside-down "
        "(only english letters will be converted): "
    )
    result = convert_input(ally, user_input)
    ally.say(result, Fore.GREEN)


def convert_input(ally, u_input):
    upside_str = 'zʎxʍʌnʇsɹbdouɯןʞſıɥbɟǝpɔqɐ'
    normal_str = 'abcdefghijklmnopqrstuvwxyz'
    upside_str = upside_str[::-1]
    converter_dict = {a: b for a, b in zip(normal_str, upside_str)}
    result = ''
    for letter in u_input:
        if letter in converter_dict:
            result += converter_dict[letter]
    return result[::-1]
