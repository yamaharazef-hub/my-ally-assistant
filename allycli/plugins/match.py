from os import system
from colorama import Fore
from plugin import plugin, require


@require(native='grep')
@plugin('match')
def match(ally, string):
    """
    Matches a string pattern in a file using regex.
    Type "match" and you'll be prompted.
    """
    file_name = ally.input("Enter file name?:\n", Fore.RED)
    pattern = ally.input("Enter string:\n", Fore.GREEN)
    file_name = file_name.strip()
    if file_name == "":
        ally.say("Invalid Filename")
    else:
        system("grep '" + pattern + "' " + file_name)
