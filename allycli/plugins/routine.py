from plugin import plugin


ROUTINES = "routines"


def create_routine(ally, commands, name):
    """
    Saves a new routine to memory with a name and a list of instructions.
    :return: Nothing to return.
    """
    routines = ally.get_data(ROUTINES)
    if routines is None:
        ally.add_data(ROUTINES, {name: commands})
    else:
        routines[name] = commands
        ally.update_data(ROUTINES, routines)


def execute_routine(ally, name):
    """
    Executes a routine saved in memory based on its name.
    If the routine doesn't exist, returns False.

    :return: Whether or not the requested routine exists.
    """
    routines = ally.get_data(ROUTINES)
    try:
        routine = routines[name]
    except (TypeError, KeyError) as e:
        return False
    for command in routine:
        ally.eval(command)
    return True


@plugin("create routine")
def new_routine(ally, s):
    if s == "":
        ally.say("You forgot to give a name.")
        return
    commands = []
    while True:
        ally.say("Type a command, or press enter to finish the routine.")
        command = ally.input()
        if command == "":
            break
        commands.append(command)
    create_routine(ally, commands, s)


@plugin("call routine")
def call_routine(ally, s):
    success = execute_routine(ally, s)
    if not success:
        ally.say("The routine you requested doesn't seem to exist.")


@plugin("list routines")
def list_routines(ally, s):
    routines = ally.get_data(ROUTINES)
    for i in routines.keys():
        ally.say(str(i))


@plugin("delete routine")
def delete_routines(ally, s):
    routines = ally.get_data(ROUTINES)
    if s in routines:
        routines.pop(s)
        ally.update_data(ROUTINES, routines)
    else:
        ally.say("Invalid routine name")
