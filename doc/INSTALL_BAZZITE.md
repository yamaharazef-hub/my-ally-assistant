# 🎮 Step-by-Step: My Ally Assistant + Armoury Crate on Bazzite

Complete walkthrough for the **ROG Xbox Ally X** (RC73XA, Ryzen AI Z2 Extreme)
running **Bazzite**. Works identically on ROG Ally / Ally X and other
handhelds — device-specific bits are auto-detected.

---

## Part 0 — Bazzite (skip if already installed)

1. Download the Bazzite handheld image from <https://bazzite.gg>
   (choose *Handheld/HTPC → ASUS → ROG Ally* — it covers the whole Ally
   family including Xbox Ally X).
2. Flash it to a USB stick with Fedora Media Writer (or Balena Etcher).
3. Boot the Ally from USB (hold **volume down + power** → boot menu),
   install, update, done.

> Already on the Ally with Windows? Bazzite dual-boots fine — just shrink
> the Windows partition first.

---

## Part 1 — Install My Ally Assistant

### Step 1: Open a terminal

Boot into **Desktop Mode** and open a terminal:

- Bazzite KDE image → **Konsole**
- Bazzite GNOME image → **Ptyxis**

(Or SSH in from another computer: `ssh bazzite@ally-ip` — handy for typing.)

### Step 2: Verify the base tools (preinstalled on Bazzite)

```bash
python3 --version     # expect Python 3.12+
git --version
```

### Step 3: Get the code

```bash
cd ~
git clone https://github.com/yamaharazef-hub/my-ally-assistant.git
cd my-ally-assistant
```

### Step 4: Create the Python environment

```bash
python3 -m venv env
source env/bin/activate
```

If `python3 -m venv env` fails on your image (missing `ensurepip`):

```bash
python3 -m pip install --user virtualenv
python3 -m virtualenv env
source env/bin/activate
```

### Step 5: Install dependencies

**Recommended on a handheld (lean set — everything Armoury needs, plus
the assistant core):**

```bash
pip install colorama nltk pluginmanager requests pick python-dateutil \
    pytimeparse beautifulsoup4 markdown tabulate gtts pyttsx3 mock distro psutil
```

**Full plugin set (bigger download, enables every plugin like plotting,
camera, PDF tools):**

```bash
pip install -r installer/requirements.txt
```

Then the small NLTK dictionary data the assistant uses for language tricks:

```bash
python -m nltk.downloader -d allycli/data/nltk wordnet punkt
```

### Step 6: Create the `ally` launcher

```bash
mkdir -p ~/.local/bin
cat > ~/.local/bin/ally << 'EOF'
#!/bin/bash
ALLY_HOME="$HOME/my-ally-assistant"
source "$ALLY_HOME/env/bin/activate" 2>/dev/null || true
exec python "$ALLY_HOME/allycli" "$@"
EOF
chmod +x ~/.local/bin/ally
```

Make sure `~/.local/bin` is on your PATH (once, then restart the terminal):

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Step 7: First run 🎉

```bash
ally
```

You should see:

```
Ally' sound is by default disabled.
...
~> Hi, what can I do for you?
```

Type `help` to list everything. Quit with `quit`.

### Step 8: Try Armoury Crate

```bash
ally armoury status
```

On the Xbox Ally X the banner shows
`ROG Xbox Ally X (2025) ✓ | Bazzite ✓`, your Z2 Extreme temp, fan RPM,
power profile, TDP and the 80Wh battery state.

---

## Part 2 — Armoury Crate features on the Xbox Ally X

| Command | Default on Xbox Ally X |
|---|---|
| `armoury profile silent` | 13W (15W on AC) — quiet indie/title mode |
| `armoury profile performance` | 17W (20W on AC) — the sweet spot for this chip |
| `armoury profile turbo` | 25W on battery, **35W plugged in** — official Armoury Crate values |
| `armoury tdp 20` | any manual limit 4–65W (e.g. 20W-25W is a great docked sweet spot) |
| `armoury fan 70` / `armoury fan auto` | manual fan speed / hardware curve |
| `armoury rgb purple` — or `#RRGGBB`, `off` | joystick-ring lighting |
| `armoury battery 80` | stop charging at 80% (great for the 80Wh pack's longevity) |

### Root access for hardware writes

TDP, fan and charge-limit writes need root. Ally calls `sudo` for you;
with sudo configured to prompt, just type your password when asked.

**Optional — passwordless TDP changes** (handy when Ally launches games
from Game Mode):

```bash
command -v ryzenadj    # note the printed path, usually /usr/bin/ryzenadj
echo "$USER ALL=(ALL) NOPASSWD: /usr/bin/ryzenadj" | sudo tee /etc/sudoers.d/ally-armoury
sudo chmod 440 /etc/sudoers.d/ally-armoury
```

### Notes specific to Bazzite

- `powerprofilesctl` and `ryzenadj` are already in Bazzite handheld
  images — nothing extra to install.
- The fan/battery sysfs knobs come from the in-kernel `asus-armoury` /
  `asus-wmi` drivers that Bazzite ships.
- **HHD co-existence**: Bazzite ships HHD which also manages TDP/fans.
  Pick one manager at a time. To pause HHD while using `armoury`:
  `systemctl --user stop hhd` (start it again with `start` after).
- Kernel LED nodes for the joystick rings appear as
  `/sys/class/leds/*:rgb:*` when the `hid-asus-ally` driver is active —
  `armoury rgb` finds them automatically.

### Optional: launch from Game Mode

Add a non-Steam shortcut that opens Konsole running Ally:

- Konsole profile command: `ally`
- or a `.desktop` entry in `~/.local/share/applications/` so Ally shows
  up in your Steam library via "Add a non-Steam game".

---

## Part 3 — Updating / uninstalling

```bash
# update
cd ~/my-ally-assistant && git pull && source env/bin/activate && pip install -U -r installer/requirements.txt

# uninstall
rm -rf ~/my-ally-assistant ~/.local/bin/ally
sudo rm -f /etc/sudoers.d/ally-armoury
sed -i '/.local\/bin:\$PATH/d' ~/.bashrc   # optional PATH cleanup
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| `ryzenadj not found` | You're on a non-handheld Bazzite image → `which ryzenadj`; if missing, layer it: `rpm-ostree install ryzenadj` then reboot. |
| `Fan is not writable` | Root required → password prompt should appear; or apply the sudoers rule above. |
| Dashboard shows "generic Linux device" | Check `cat /sys/class/dmi/id/product_name` — Armoury auto-detects RC71L / RC72LA / RC73XA / RC73YA. |
| `power-profiles-daemon not found` | Non-Bazzite distro → install `power-profiles-daemon` via your package manager. |
| Nothing RGB happens | Keyboard/RGB hardware varies; run `armoury rgb` alone to list detected backends. |
