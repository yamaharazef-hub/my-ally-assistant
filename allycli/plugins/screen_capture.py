import os

import pyautogui as pg
from plugin import LINUX, MACOS, WINDOWS, plugin, require


@require(platform=WINDOWS)
@plugin('screencapture')
def Screencapture_Windows(ally, s):
    """
    By holding Windows + Alt + R key we start screen capture in
    """
    def engine():
        pg.keyDown("win")
        pg.keyDown("alt")
        pg.press("r")
        pg.keyUp("alt")
        pg.keyUp("win")

    ally.say('Screen Recording Started')
    engine()
    n = input("Press Q to stop : ")
    if n == 'Q':
        engine()
        ally.say('Screen Recording Ended')


@require(platform=LINUX)
@plugin('screencapture')
def Scrrencapture_LINUX(ally, s):
    """
    By holding Ctrl + Alt + Shift + R key we start screen capture in
    """

    def engine():
        pg.keyDown("ctrl")
        pg.keyDown("alt")
        pg.keyDown("shift")
        pg.press("r")
        pg.keyDown("shift")
        pg.keyUp("alt")
        pg.keyUp("ctrl")

    ally.say('Screen Recording Started')
    engine()
    n = input("Press Q to stop : ")
    if n == 'Q':
        engine()
        ally.say('Screen Recording Ended')


@require(platform=MACOS)
@plugin('screencapture')
def Scrrencapture_MACOS(ally, s):
    """
    By holding Ctrl + Alt + Shift + R key we start screen capture in
    """

    def engine():
        pg.keyDown("command")
        pg.keyDown("shift")
        pg.press("5")
        pg.keyDown("shift")
        pg.keyUp("command")

    ally.say('Screen Recording Started')
    engine()
    n = input("Press Q to stop : ")
    if n == 'Q':
        engine()
        ally.say('Screen Recording Ended')
