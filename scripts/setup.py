#!/usr/bin/env python3
"""Store an Arena API key outside the repository without echoing it."""
import getpass
import json
import os
from pathlib import Path

config_dir = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')) / 'my-ally-assistant'
config_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
print('Create an API key at https://platform.arena.ai/dashboard/keys')
print('Your workspace must allow API access; a regular Arena chat login may not suffice.')
key = getpass.getpass('Arena API key (input hidden): ').strip()
if not key:
    raise SystemExit('No key entered. Nothing saved.')
model = input('Arena model [coding-router-preview]: ').strip() or 'coding-router-preview'
path = config_dir / 'config.json'
fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
os.fchmod(fd, 0o600)
with os.fdopen(fd, 'w') as file:
    json.dump({'api_key': key, 'model': model}, file)
print(f'Saved configuration to {path}. Keep this file private.')
