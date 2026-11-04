#!/usr/bin/env bash
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# Launch browser and keep serving for the whole Steam session. Exit the app from Steam to stop it.
exec python3 "$ROOT/app.py" --open
