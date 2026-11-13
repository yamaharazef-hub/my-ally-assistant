from plugin import plugin


@plugin("christmas")
def newyear(ally, s):
    tree = "     *\n"\
           "    ###\n"\
           "   #####\n"\
           "    ###\n"\
           "   #####\n"\
           "  #######\n"\
           "   #####\n"\
           "  #######\n"\
           "    ###\n"\
           "    ###"
    ally.say(tree)
