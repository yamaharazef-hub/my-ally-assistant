# -*- coding: utf-8 -*-
"""
Steam / Game Mode integration for My Ally Assistant.

Makes Ally appear as a proper game tile inside Steam — which on Bazzite
means it shows up in **Game Mode** (the SteamOS-style console UI that the
Steam Deck and ROG Ally handhelds boot into).

    steam setup    — desktop entry + Steam shortcut + library artwork
    steam status   — show what is installed
    steam remove   — remove the integration again

The implementation talks directly to Steam's files (no Steam client API
needed): shortcuts.vdf (non-Steam games) and the config/grid artwork
folders, following the same file layout Steam ROM Manager uses.

Artwork is only installed when the image files are present in the repo
(icons/steam_*.png) — generate or replace them to customise the tile.
"""

from packages.steamint.steam import (  # noqa: F401
    APP_NAME,
    find_steam_users,
    shortcut_id,
    appid64,
    steam_setup,
    steam_status,
    steam_remove,
)
from packages.steamint.launcher import (  # noqa: F401
    find_terminal,
    install_launcher,
    install_desktop_entry,
    ALLEY_WRAPPER,
    DESKTOP_FILE,
)
