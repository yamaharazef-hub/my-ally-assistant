from plugin import alias, plugin


@alias("bye", "goodbye", "q", "quit")
@plugin('exit')
def exit(ally, s):
    """Closing ally"""
    ally.exit()
