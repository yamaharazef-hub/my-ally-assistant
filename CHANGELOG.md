# Changelog

All notable changes to **My Ally Assistant** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
