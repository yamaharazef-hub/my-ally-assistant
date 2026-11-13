import os
from plugin import plugin, require, LINUX


@require(platform=LINUX)
@plugin('open')
def open(ally, s):

    if s != "":
        string = "gtk-launch " + "/usr/share/applications/" + s + ".desktop"
        os.system(string)
    else:
        ally.say("avaliable options are:")
        os.system("ls -1 /usr/share/applications/ | sed -e 's/\\.desktop$//'")
