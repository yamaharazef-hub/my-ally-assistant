import os
from plugin import plugin, require


@require(native='wmctrl')
@plugin("go to")
def go_to(ally, s):
    os.system("wmctrl -a " + s)  # switch to already opened app/software.


@require(native='wmctrl')
@plugin("workspace")
def workspace(ally, s):
    if s == 'one':
        s = 1
    num = str(int(s) - 1)
    os.system("wmctrl -s " + num)  # switch workspace.


@plugin("run")
def run(ally, s):
    """
    Run commands in terminal(use shell)
    e.g. run echo hello
    """
    os.system(s)
