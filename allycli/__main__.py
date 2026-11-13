# -*- coding: utf-8 -*-
import Ally
import colorama
import sys
from plugins.message import send_join_message


def check_python_version():
    return sys.version_info[0] == 3


def main():
    # enable color on windows
    colorama.init()
    # start Ally
    ally = Ally.Ally()

    # Send Telegram message on startup
    send_join_message()

    command = " ".join(sys.argv[1:]).strip()
    ally.executor(command)


if __name__ == '__main__':
    if check_python_version():
        main()
    else:
        print("Sorry! Only Python 3 supported.")
