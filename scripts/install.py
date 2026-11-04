#!/usr/bin/env python3
"""Install a per-user desktop entry without touching the Bazzite base image."""
import os
from pathlib import Path
import shlex

root = Path(__file__).resolve().parent.parent
applications = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share')) / 'applications'
applications.mkdir(parents=True, exist_ok=True)
launcher = root / 'scripts' / 'launch.sh'
# Desktop Entry Exec uses double quotes with backslash escaping, not shell quoting.
def desktop_quote(path):
    return '"' + str(path).replace('\\', '\\\\').replace('"', '\\"').replace('`', '\\`').replace('$', '\\$').replace('%', '%%') + '"'
entry = applications / 'my-ally-assistant.desktop'
entry.write_text('[Desktop Entry]\nType=Application\nName=My Ally Assistant\nComment=Your voice and text companion\nExec=' + desktop_quote(launcher) + '\nIcon=' + str(root / 'static' / 'icon.svg') + '\nTerminal=false\nCategories=Utility;\n')
print(f'Installed {entry}. Keep this repository in {root}; the launcher uses it in place.')
