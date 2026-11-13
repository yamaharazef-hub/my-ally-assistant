import os
from plugin import plugin, require, LINUX, MACOS, WINDOWS


@require(platform=LINUX)
@plugin('shutdown')
def shutdown_LINUX(ally, s):
    """
    Shutdown the system
    Uses:
    shutdown : asks for time
    shutdown -c : cancels shutdown
    """
    if s == '':
        s = ally.input('In how many minutes?: ')
    if s == '-c':
        os.system('sudo shutdown -c')
        ally.say('Shutdown operation cancelled')
        return
    string = 'sudo shutdown -t ' + str(s)
    os.system(string)


@require(platform=MACOS)
@plugin('shutdown')
def shutdown_MACOS(ally, s):
    """
    Shutdown the system
    Uses:
    shutdown : asks for time
    shutdown -c : cancels shutdown
    """
    if s == '':
        s = ally.input('In how many minutes?: ')
    if s == '-c':
        os.system('sudo killall shutdown')
        ally.say('Shutdown operation cancelled')
        return
    string = 'sudo shutdown -h +' + str(s)
    os.system(string)


@require(platform=WINDOWS)
@plugin('shutdown')
def shutdown_WIN32(ally, s):
    """
    Shutdown the system
    Uses:
    shutdown : asks for time
    shutdown -c : cancels shutdown
    """
    if s == '':
        s = ally.input('In how many seconds?: ')
    if s == '-c':
        os.system('shutdown /a')
        ally.say('Shutdown operation cancelled')
        return
    string = 'sudo shutdown /s /t ' + str(s)
    os.system(string)


@require(platform=LINUX)
@plugin('reboot_computer')
def reboot_LINUX(ally, s):
    """Reboot the system"""
    if s == '':
        s = ally.input('In how many minutes?: ')
    string = 'sudo shutdown -r -t ' + str(s)
    os.system(string)


@require(platform=MACOS)
@plugin('reboot_computer')
def reboot_MACOS(ally, s):
    """Reboot the system"""
    if s == '':
        s = ally.input('reboot? y/n: ')
        if s == 'y':
            ally.say('rebooting system')
            string = 'sudo shutdown -r now'
            os.system(string)
        if s == 'n':
            ally.say('reboot cancelled')
            return


@require(platform=WINDOWS)
@plugin('reboot_computer')
def reboot_WIN32(ally, s):
    """Reboot the system"""
    if s == '':
        s = ally.input('In how many seconds?: ')
    string = 'shutdown /r /t ' + str(s)
    os.system(string)


@require(native="systemctl", platform=LINUX)
@plugin('hibernate')
def hibernate_LINUX(ally, s):
    """
    Hibernate - also known as "Suspend to Disk"

    Saves everything running to disk and performs shutdown.
    Next reboot computer will restore everything - including
    Programs and open files like the shutdown never happened.
    """
    os.system('sudo systemctl hibernate')


@require(platform=WINDOWS)
@plugin('hibernate')
def hibernate_WIN32(ally, s):
    """Hibernates the system"""
    string = 'shutdown /h'
    os.system(string)


@require(native="systemctl", platform=LINUX)
@plugin('hybridsleep')
def hybridsleep_LINUX(ally, s):
    """
    Hybrid sleep.
    Will quickly wake up but also survive power cut.
    Performs both suspend AND hibernate.
    Will quickly wake up but also survive power cut.
    """
    os.system("sudo systemctl hybrid-sleep")


@require(platform=WINDOWS)
@plugin('hybridsleep')
def hybridsleep_WIN32(ally, s):
    """Performs shutdown and prepares forfast startup"""
    string = 'shutdown /hybrid'
    os.system(string)


@require(platform=WINDOWS)
@plugin('log off')
def log_off_WIN32(ally, s):
    """Log off the system"""
    string = 'shutdown /l'
    os.system(string)


@require(native="systemctl", platform=LINUX)
@plugin('suspend')
def suspend_LINUX(ally, s):
    """
    Suspend (to RAM) - also known as Stand By or Sleep mode.

    Operate PC on a minimum to save power but quickly wake up.
    """
    os.system('sudo systemctl suspend')
