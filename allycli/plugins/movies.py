import os
from colorama import Fore
from plugin import plugin, require, LINUX


@require(platform=LINUX, native='ims')
@plugin('movies')
def movies(ally, s):
    """Ally will find a good movie for you"""
    movie_name = ally.input("What do you want to watch?\n", Fore.RED)
    os.system("ims " + movie_name)
