# Changelog

All notable changes to **My Ally Assistant** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] — "Game Mode" — 2026-11-13

### Added

- **Steam / Game Mode integration** — new `steam` plugin
  (aliases: `gamemode`, `steamdeck`) that makes My Ally Assistant a
  first-class tile in the Steam library on Bazzite / Steam Deck:
  - `steam setup` — installs a DE-agnostic terminal wrapper
    (`~/.local/bin/ally-terminal`: Konsole/Ptyxis/kgx/gnome-terminal/
    alacritty/xterm auto-detect), a `.desktop` entry, a non-Steam-game
    shortcut written directly into `shortcuts.vdf` (with `.bak` backup,
    idempotent — re-runs never duplicate) and library artwork keyed by
    Steam's shortcut-id algorithm (crc32 → appid64), for every local
    Steam account found (native + Flatpak layouts)
  - `steam status` / `steam remove` — inspect or fully uninstall
  - custom AI-generated artwork set in `icons/`: `ally_icon.png`,
    `steam_grid.png`, `steam_capsule.png`, `steam_hero.png`,
    `steam_logo.png` (Ally robot mascot, cyan/purple neon)
- `allycli/packages/steamint/` — stdlib-only binary `shortcuts.vdf`
  parser/writer (lossless round-trip), Steam userdata discovery,
  launcher + desktop-entry generators
- 17 new tests (vdf round-trip incl. signed appids, shortcut ids,
  setup/status/remove lifecycle, launcher/desktop generation)

## [1.2.0] — "Xbox Ally X" — 2026-11-13

### Added

- **ROG Xbox Ally X (RC73XA, Ryzen AI Z2 Extreme) first-class support**
  - DMI model-code detection for the whole Ally family:
    RC71L (Ally 2023), RC72LA (Ally X 2024), RC73YA (Xbox Ally),
    RC73XA (Xbox Ally X) — plus catch-alls for future variants
  - Per-device official Armoury Crate wattage presets; Xbox Ally X gets
    Turbo 25W battery / **35W on AC** (its real Windows values)
- `doc/INSTALL_BAZZITE.md` — complete step-by-step installation guide
  for Bazzite on the Xbox Ally X (also covers Ally/Ally X), including
  venv setup, launcher, NLTK data, sudo rules, HHD co-existence and
  troubleshooting
- 8 new detection/preset tests (28 armoury tests total)

### Fixed

- RGB LED driver handling: respect `max_brightness` scale (Ally joystick
  rings are 0-100, not 0-255) and select the static `monocolor` effect
  when the driver exposes one
- `armoury profile` no longer force-applies handheld TDP presets on
  laptops/unknown devices (uses power-profiles-daemon only there)

## [1.1.0] — "Armoury" — 2026-11-13

### Added

- **Armoury Crate recreated for Bazzite Linux** — new `armoury` plugin
  (alias: `armory`) with a modular backend package
  `allycli/packages/armoury/`:
  - `armoury status` — Armoury-Crate-style hardware dashboard (device
    detection for ROG Ally / ASUS laptops / generic Linux, APU temp, fan
    RPM, power profile, TDP, battery, memory, uptime, RGB backends)
  - `armoury profile silent|performance|turbo` — operating modes mapping
    to power-profiles-daemon + TDP presets; Turbo mirrors the real
    Armoury Crate on the Ally (25W on battery, 30W plugged in)
  - `armoury tdp <watts>` — APU TDP control via `ryzenadj`
  - `armoury fan <0-100|auto>` — fan control via hwmon PWM
    (asus-armoury / asus-nb-wmi)
  - `armoury rgb <colour|#RRGGBB|off>` — Aura-style lighting via kernel
    LED class devices (hid-asus-ally), `asusctl`, or OpenRGB
  - `armoury battery <50-100>` — battery care charge limit
    (`charge_control_end_threshold`)
  - Every capability detects hardware/tools at runtime and degrades
    gracefully with actionable hints; stdlib-only, no new dependencies
- 20 new unit tests (`allycli/tests/test_armoury.py`), all mocked and
  fully offline
- README section documenting the Armoury commands and Bazzite notes

## [1.0.0] — "My Ally" — 2026-11-13

Initial standalone release of **My Ally Assistant**, forked and rebranded from
[`sukeesh/Jarvis`](https://github.com/sukeesh/Jarvis) (MIT License).

### Changed (rebrand from upstream Jarvis)

- Renamed the main package `jarviscli/` → `allycli/`
- Renamed core module `Jarvis.py` → `Ally.py`
- Renamed main class `Jarvis` → `Ally` and plugin API class `JarvisAPI` → `AllyAPI`
- Renamed built-in plugin `jarvis_tour` → `ally_tour` (command: `ally tour`)
- Renamed test suite file `test_jarvis_api.py` → `test_ally_api.py`
- The installer now generates an `ally` launcher (`ally.bat` on Windows)
- Environment variables renamed:
  - `JARVIS_TELEGRAM_BOT_TOKEN` → `ALLY_TELEGRAM_BOT_TOKEN`
  - `JARVIS_TELEGRAM_CHAT_ID` → `ALLY_TELEGRAM_CHAT_ID`
  - `JARVIS_GMAIL_ADDRESS` → `ALLY_GMAIL_ADDRESS`
  - `JARVIS_GMAIL_APP_PASSWORD` → `ALLY_GMAIL_APP_PASSWORD`
- All user-facing strings, prompts and greetings now say "Ally"
  (including the `~> Hi, what can I do for you?` prompt)
- Replaced legacy Travis CI (`.travis.yml`) with GitHub Actions
  (`.github/workflows/ci.yml`), testing Python 3.9 and 3.11 on Linux and Windows
- Rewrote `README.md` for My Ally Assistant
- Updated `LICENSE`: original MIT attribution to Sukeesh preserved, added
  copyright line for the modified work
- Modernized `Makefile` with `install` / `run` / `test` / `lint` / `clean` /
  `help` targets (Docker image now tagged `ally`)

### Attribution

- Based on the work of **Sukeesh** and all Jarvis contributors.
- Original project: <https://github.com/sukeesh/Jarvis> — MIT License.
