from plugin import plugin, alias, complete


@plugin()
def plugin0(ally, s):
    """
    Doku
    """
    ally.say("exec")


@plugin(network=True, native="native", python="python", platform="platform")
@complete("complete")
@alias("alias")
def plugin1(ally, s):
    """help"""
    pass
