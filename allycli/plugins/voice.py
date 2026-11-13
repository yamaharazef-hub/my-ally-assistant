from colorama import Fore
from plugin import LINUX, UNIX, MACOS, WINDOWS, plugin, require


@plugin('enable sound')
def enable_sound(ally, s):
    """Let Ally use his voice."""
    ally.speech = ally.enable_voice()
    ally.say(Fore.BLUE + "Ally uses Googles speech engine.\nDo you consent with data "
               + "collection when Ally talks out loud? If yes, type:" + Fore.RED + " gtts")
    ally.say(Fore.BLUE + "If not, Ally will talk using the built-in speech engine. "
               + " If you wish to disable GTTS, type: " + Fore.RED + "disable gtts")


@plugin('disable sound')
def disable_sound(ally, s):
    """Deny Ally his voice."""
    ally.disable_voice()


@plugin('say')
def say(ally, s):
    """Reads what is typed."""
    if not s:
        ally.say("What should I say?")
    else:
        voice_state = ally.is_voice_enabled()
        ally.enable_voice()
        ally.say(s)
        if not voice_state:
            ally.disable_voice()


@plugin('disable gtts')
def disable_gtts(ally, s):
    """Reads what is typed without using gtts."""
    voice_state = ally.is_voice_enabled
    ally.disable_gtts()
    ally.speech = ally.enable_voice()

    if not voice_state:
        ally.disable_voice()


@plugin('gtts')
def gtts(ally, s):
    """Reads what is typed using gtts."""
    voice_state = ally.is_voice_enabled
    ally.enable_gtts()

    if not voice_state:
        ally.disable_voice()


@require(platform=[LINUX, WINDOWS])
@plugin('talk faster')
def talk_faster(ally, s):
    """Make Ally' speech engine talk faster.
    """
    if ally.is_voice_enabled():
        ally.change_speech_rate(40)
    else:
        ally.say("Type 'enable sound' to allow Ally to talk out loud.",
                   Fore.BLUE)


@require(platform=[LINUX, WINDOWS])
@plugin('talk slower')
def talk_slower(ally, s):
    """Make Ally' speech engine talk slower.
    """
    if ally.is_voice_enabled():
        ally.change_speech_rate(-40)
    else:
        ally.say("Type 'enable sound' to allow Ally to talk out loud.",
                   Fore.BLUE)
