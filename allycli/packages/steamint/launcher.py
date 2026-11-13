# -*- coding: utf-8 -*-
"""Terminal launcher + desktop entry for Game Mode integration.

Game Mode (gamescope) can run regular windowed apps — but Ally is a CLI,
so we wrap it in whichever terminal emulator the image provides
(Konsole on Bazzite-KDE, Ptyxis on Bazzite-GNOME, ...). A tiny wrapper
script picks the terminal at runtime, so the same Steam shortcut works
across Bazzite variants.
"""

import os
import shutil
import stat

ALLEY_WRAPPER = os.path.expanduser("~/.local/bin/ally-terminal")
DESKTOP_FILE = os.path.expanduser(
    "~/.local/share/applications/my-ally-assistant.desktop")

# terminal -> exec template (first found wins)
TERMINALS = [
    ("konsole", "{bin} --profile Shell --hide-menubar -e '{wrapper}'"),
    ("ptyxis", "{bin} --new-window -- '{wrapper}'"),
    ("kgx", "{bin} -- '{wrapper}'"),
    ("gnome-terminal", "{bin} -- '{wrapper}'"),
    ("alacritty", "{bin} -e '{wrapper}'"),
    ("xterm", "{bin} -e '{wrapper}'"),
]

ALLIE_ICON = "icons/ally_icon.png"

WRAPPER_TEMPLATE = """\
#!/bin/bash
# My Ally Assistant — Game Mode terminal wrapper (auto-generated)
# Finds an available terminal emulator and runs Ally inside it.
ALLY_HOME="{ally_home}"

ALLY_CMD="source '$ALLY_HOME/env/bin/activate' 2>/dev/null; \
python '$ALLY_HOME/allycli'; exec bash"

for t in konsole ptyxis kgx gnome-terminal alacritty xterm; do
  if command -v "$t" >/dev/null 2>&1; then
    case "$t" in
      konsole)         exec "$t" --hide-menubar -e bash -lc "$ALLY_CMD";;
      ptyxis|kgx)      exec "$t" -- bash -lc "$ALLY_CMD";;
      gnome-terminal)  exec "$t" -- bash -lc "$ALLY_CMD";;
      alacritty|xterm) exec "$t" -e bash -lc "$ALLY_CMD";;
    esac
  fi
done
echo "My Ally Assistant: no terminal emulator found (konsole/ptyxis/kgx/...)" >&2
exit 1
"""


def find_terminal():
    """First available terminal emulator binary name, or None."""
    for name, _ in TERMINALS:
        if shutil.which(name):
            return name
    return None


def _repo_root():
    here = os.path.abspath(__file__)
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(here))))


def install_launcher(messages):
    """Write ~/.local/bin/ally-terminal. Returns the wrapper path."""
    ally_home = _repo_root()
    os.makedirs(os.path.dirname(ALLEY_WRAPPER), exist_ok=True)
    with open(ALLEY_WRAPPER, "w") as fh:
        fh.write(WRAPPER_TEMPLATE.format(ally_home=ally_home))
    os.chmod(ALLEY_WRAPPER, os.stat(ALLEY_WRAPPER).st_mode
             | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    messages.append((True, f"terminal wrapper installed: {ALLEY_WRAPPER}"))
    return ALLEY_WRAPPER


def install_desktop_entry(wrapper, messages):
    """Create the .desktop entry so 'Add a Non-Steam Game' finds Ally."""
    terminal = find_terminal()
    icon = os.path.join(_repo_root(), ALLIE_ICON)
    if not os.path.exists(icon):
        icon = "utilities-terminal"

    # With terminal detection fail-safe: desktop entry runs the wrapper,
    # which itself locates a terminal (robust across DE variants).
    exec_line = wrapper

    content = "\n".join([
        "[Desktop Entry]",
        "Type=Application",
        "Name=My Ally Assistant",
        "GenericName=Personal assistant + Armoury Crate",
        "Comment=Launch Ally (Armoury Crate for Bazzite) in a terminal",
        f"Exec={exec_line}",
        f"Icon={icon}",
        "Terminal=false",
        "Categories=Utility;Game;",
        "Keywords=ally;assistant;armoury;bazzite;",
        "StartupNotify=false",
        "",
    ])
    os.makedirs(os.path.dirname(DESKTOP_FILE), exist_ok=True)
    with open(DESKTOP_FILE, "w") as fh:
        fh.write(content)
    messages.append((True, f"desktop entry installed: {DESKTOP_FILE} "
                           f"(terminal: {terminal or 'auto-detect at run'})"))
    return DESKTOP_FILE
