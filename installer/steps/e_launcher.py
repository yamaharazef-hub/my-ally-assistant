from helper import *
from os.path import expanduser, exists
import unix_windows

def supported_shell_install(rc_line_to_add : str, confirm_addition: bool) -> bool:
    shell_rc = '{}/.{}rc'.format(expanduser("~"), user_shell)
    if not os.path.exists(shell_rc):
        print("NO .{}rc found!".format(user_shell))
        return False;
    line_already_exists = False

    with open(shell_rc, "r") as fr:
        for line in fr.readlines():
            if line.startswith(rc_line_to_add):
                line_already_exists = True

    if line_already_exists:
        print("Ally path already added to $PATH in .{}rc!".format(user_shell))
        return True;

    print("")
    if not confirm_user_input("Allow Ally installation to add {} to .{}rc?".format(rc_line_to_add, user_shell)):
        print('Ally will not add "{}" to .{}rc.'.format(shell_rc, user_shell))
        print('In order to use Ally please manually add \'{}\' to your $PATH'.format(rc_line_to_add))
        return False
    with open(shell_rc, 'a') as fw:
        fw.write(line_to_add)
        fw.write('\n')
    return True

# TODO Windows Install options?
if unix_windows.IS_WIN:
    fw = open('ally.bat', 'w')
    fw.write("""\
@ECHO off
CALL "{ALLYPATH}\\env\\Scripts\\activate.bat"
python "{ALLYPATH}\\allycli" %*
    """.format(ALLYPATH=os.getcwd()))
    section("FINISH")

    printlog("Installation Successful! Use 'ally' in cmd to start Ally!")
else:

    section("Write Ally starter")

    ALLY_MACRO = """\
#!/bin/bash
source "{PATH}/env/bin/activate"
python "{PATH}/allycli" "$@"
    """

    fw = open('ally', 'w')
    fw.write(ALLY_MACRO.format(PATH=os.getcwd()))
    fw.close()

    shell('chmod +x ally').should_not_fail()
    # get the SHELL of the current user
    user_shell = get_default_shell()
    _do_nothing_str = "Do nothing (Call Ally by full path)"
    install_options = [("Install ally /usr/local/bin starter (requires root)", 0), ]
    home = os.getenv("HOME")
    xdg_install_path = "{}/.local/bin".format(home)
    if user_shell in SUPPORTED_SHELLS:
        install_options += [
            ("Add {} to $PATH (.{}rc)".format(os.getcwd(), user_shell, ), 1),
        ]
        if home != None and os.path.exists(xdg_install_path):
            install_options += [("Install ally to {}/.local/bin".format(home), 2)]
        install_options += [(_do_nothing_str, 3)]
    else:
        install_options += [
            (_do_nothing_str, 1)
        ]
    selection = user_input(install_options)

    if selection == 0:
        os.system('sudo cp ally /usr/local/bin')
    elif user_shell in SUPPORTED_SHELLS:
        if selection == 1:
            line_to_add = 'export PATH="$PATH:{}"'.format(os.getcwd())
            supported_shell_install(line_to_add, True)
        elif selection == 2:
            os.system('cp ally {}'.format(xdg_install_path))
            line_to_add = 'export PATH="$PATH:{}"'.format(xdg_install_path)
            supported_shell_install(line_to_add, True)

    printlog('\n\nInstallation complete. Try using Ally!')
    if selection == 0 or (selection == 1 and user_shell in SUPPORTED_SHELLS):
        printlog('$ ally')
    else:
        printlog('$ {}/ally'.format(os.getcwd()))

