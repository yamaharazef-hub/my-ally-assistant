# My Ally Assistant 🤖

Your personal command-line assistant for **Linux, macOS and Windows** — always on your side.

My Ally Assistant (or just **Ally**) is a personal assistant that lives in your terminal. Ally can talk to you if you enable voice, tell you the weather, find restaurants and places near you, play games, do math, manage files, and much more — all from the command line.

> 🌱 **Origin:** My Ally Assistant is an independent fork and rebrand of
> [`sukeesh/Jarvis`](https://github.com/sukeesh/Jarvis) (MIT License), rebuilt and
> maintained as my own version. Huge credit to Sukeesh and all original
> contributors — see [LICENSE](LICENSE).

## 🚀 15+ Different Tasks That Ally Can Do For You

1. **Entertainment & Suggestions**
   - Suggest activities if you're bored (`activity`, `bored`)
   - Ideas on what to draw, watch, or listen to (`prompt`, `top_media`, `taste dive`, `mood music`)

2. **Sports Updates**
   - Team rankings, match times, player stats (`basketball`, `cricket`, `soccer`, `tennis`)

3. **Games**
   - Blackjack, Connect Four, Hangman, Rock-Paper-Scissors, Wordle and more
     (`blackjack`, `connect_four`, `guess_number_game`, `hangman`, `rockpaperscissors`, `roulette`, `tic_tac_toe`, `word_game`, `wordle`)

4. **Health & Fitness**
   - Nutrition facts, recipes, workout programs, health trackers (`bmi`, `bmr`, `calories`, `food recipe`, `fruit`, `workout`)

5. **Cocktail Recipes**
   - Learn how to make cocktails (`cocktail`, `drink`)

6. **Random Generators**
   - Random lists, numbers, passwords (`random list`, `random number`, `random password`)

7. **Unit Conversions**
   - Binary, currency, hex, length, mass, speed, temperature, time (`binary`, `currencyconv`, `hex`, `lengthconv`, `massconv`, `speedconv`, `tempconv`, `timeconv`)

8. **Photography**
   - Take pictures and screenshots (`open camera`, `screencapture`)

9. **System Information**
   - Computer specs and network info (`battery`, `hostinfo`, `ip`, `scan_network`, `speedtest`, `os`, `check ram`, `systeminfo`)

10. **File Management**
    - Manage and organize files (`file manage`, `file organize`)

11. **Image Processing**
    - Upload, edit, and convert images (`imgur`, `image to pdf`, `image compressor`)

12. **PDF Conversion**
    - Webpages to PDF, PDFs to images (`htmltopdf`, `pdf to images`)

13. **Jokes & Facts**
    - Jokes and random facts (`dadjoke`, `joke daily`, `joke chuck`, `joke`, `fact`, `cat fact`)

14. **Calculations**
    - Calculations, equations, plotting, matrices (`calculate`, `factor`, `solve`, `equations`, `plot`, `matrix add`)

15. **QR Code Generation**
    - Generate QR codes for URLs (`qr`)

16. **Weather Updates**
    - Weather forecast (`weather report`)

17. **Language Translation**
    - Translate between languages (`translate`)

18. **Stock & Crypto**
    - Stock and cryptocurrency information (`stock`, `cryptotracker`)

…plus **185+ plugins** in total. Type `help` inside Ally to discover them all.

## ⚔️ Armoury Crate — recreated for Bazzite Linux

ASUS' **Armoury Crate** has no Linux version — so this project recreates it,
tuned for the **ROG Ally running Bazzite**, and working on ASUS laptops and
generic Linux hardware too. Everything auto-detects your hardware and degrades
gracefully with helpful hints when a feature isn't supported.

```
~> armoury
    ⚔  ARMOURY CRATE  —  Ally Edition (Bazzite/Linux)
    ROG Ally RC71L — ROG Ally detected ✓ | Bazzite ✓
    ────────────────────────────────────────────────────
    APU/CPU : AMD Ryzen Z1 Extreme
    Temp    : 44.5°C (k10temp)    Fan: 3200 RPM — 50% (auto)
    Profile : balanced   TDP: 30W   Source: AC
    Battery : 78% — Discharging (charge limit: 80%)
    ...
```

| Command | What it does |
|---|---|
| `armoury` / `armoury status` | Hardware dashboard (APU, temps, fan, battery, profile, TDP) |
| `armoury profile silent\|performance\|turbo` | Operating mode (power-profiles-daemon + TDP preset; turbo = 25W on battery, 30W on AC, like the real Armoury Crate) |
| `armoury tdp 15` | Direct APU TDP limit via `ryzenadj` (4–65W) |
| `armoury fan 60` / `armoury fan auto` | Manual fan speed or hardware auto-curve |
| `armoury rgb green` / `armoury rgb #FF8800` / `armoury rgb off` | Aura-style lighting (kernel LED classdev → `asusctl` → OpenRGB backends) |
| `armoury battery 80` | Battery care charge limit (like Armoury Crate's lifespan modes) |
| `armoury help` | Full command reference |

**Bazzite notes:** `powerprofilesctl` and `ryzenadj` ship with Bazzite
handheld images; TDP/fan/battery writes need root (Ally will use `sudo`
automatically). If you use [HHD](https://github.com/hhd-dev/hhd), avoid
double-managing TDP/fans from both tools. Works on non-Bazzite distros too —
just install the tools it asks for.

## 🛠️ Getting Started

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yamaharazef-hub/my-ally-assistant.git
   cd my-ally-assistant
   ```

2. **Run the installer**

   ```bash
   python installer
   ```

   If that doesn't work, try:

   ```bash
   python3 installer
   ```

   The installer creates a virtual environment (`env/`), installs all
   dependencies, downloads the required NLTK data, and generates an `ally`
   launcher (`ally.bat` on Windows).

### Running Ally

From anywhere (after adding to `$PATH` during install):

```bash
ally
```

Or from the project folder:

```bash
./ally
```

Type `help` inside the Ally command line to see everything Ally can do.

### First run

```
Ally' sound is by default disabled.
In order to let Ally talk out loud type: enable sound
Type 'help' for a list of available actions.

~> Hi, what can I do for you?
```

## ⚙️ Configuration

Ally reads optional integrations from environment variables:

| Variable | Purpose |
|---|---|
| `ALLY_TELEGRAM_BOT_TOKEN` | Telegram bot token for `send telegram` and startup notification |
| `ALLY_TELEGRAM_CHAT_ID` | Telegram chat ID for the messages above |
| `ALLY_GMAIL_ADDRESS` | Gmail address for `send gmail` |
| `ALLY_GMAIL_APP_PASSWORD` | Gmail app password for `send gmail` |

Other plugins (weather, imgur, news, …) use API keys stored in
`allycli/data/` — see `doc/PLUGINS.md`.

## 🧩 Writing Your Own Plugin

Create `custom/hello_world.py`:

```python
from plugin import plugin


@plugin("helloworld")
def helloworld(ally, s):
    """Repeats what you type"""
    ally.say(s)
```

Try it:

```bash
./ally
~> helloworld Ally is cool!
ally is cool
```

- 📘 [Plugin guide](doc/PLUGINS.md)
- 🧪 [Testing guide](doc/TESTING.md)
- 🔌 [API reference](doc/API.md)

## 🧪 Running Tests

```bash
./test.sh
```

or manually:

```bash
cd allycli
python -m unittest discover
```

## 🐳 Docker

```bash
[sudo] make build_docker
[sudo] make run_docker
```

## ❓ Frequently Encountered Issues

**Q: `ModuleNotFoundError` when starting Ally (Windows)**
A: Reinstall the missing package, e.g.

```bash
pip uninstall pywin32 && pip install pywin32
```

or add the package to your system `PATH`.

---

**Q: Installer fails with "please install virtual environment"**
A:

```bash
python3 -m pip install virtualenv
# or on Ubuntu/Debian:
sudo apt install python3-venv
```

then restart the installer.

## 🔌 Optional Dependencies

- Any `pyttsx3` text-to-speech engine (`sapi5`, `nsss` or `espeak`) so Ally can talk out loud (e.g. `sudo apt install espeak`)
- PortAudio + python-devel packages for voice control
- `notify-send` on Linux for nicer desktop notifications (`sudo apt install libnotify-bin`)
- `ffmpeg` so `music` downloads songs as `.mp3` instead of `.webm`

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) — starting with **v1.0.0 "My Ally"**, the full rebrand from Jarvis.

## 🤝 Contributing

Check out [CONTRIBUTING.md](CONTRIBUTING.md) to learn how you can help improve Ally!

## 📜 License

This project is licensed under the MIT License — see [LICENSE](LICENSE).
Based on [Jarvis](https://github.com/sukeesh/Jarvis) by **Sukeesh**, relicensed terms unchanged.
