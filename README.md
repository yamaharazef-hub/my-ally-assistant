# My Ally Assistant

A personal voice + text companion for the **ASUS ROG Ally X on Bazzite**. Ally runs as a local web app in Desktop Mode or as a non-Steam app in Gaming Mode. It sends your conversation to Arena's online API and can speak replies through your browser. The interface is touch-friendly and can also be used with a controller configured as a mouse.

> **First release / scope:** This is a chat assistant, not a system-level agent. It does not run commands, control games or settings, search the web, listen for a wake word, or work offline. It cannot see your device status. Never run a command it suggests without reviewing it. Live Arena access requires a separate API-enabled Arena workspace/key; an ordinary Arena chat account or free-router key may not be sufficient. API access, models and pricing are subject to Arena's terms.

## 1. What you need

- Bazzite installed on the Ally X, an internet connection, and **Desktop Mode** for initial setup.
- `git` and Python 3.9+ on the host. Check with `git --version` and `python3 --version` in Konsole. Bazzite's image-based filesystem should not be modified with `sudo pip` or regular `dnf`; consult [Bazzite's software installation guide](https://docs.bazzite.gg/Installing_and_Managing_Software/) for missing tools. The launcher must be able to find `python3` on the host, not only inside a Distrobox.
- Chrome or Chromium is recommended for voice input. Install a browser via Discover/Flathub, e.g. Google Chrome (`com.google.Chrome`), if needed. Microphone recognition varies by browser and provider; Chrome's recognition may send audio to its speech service. Text works without voice recognition. Browser text-to-speech availability and voices also vary.
- An [Arena API key](https://platform.arena.ai/dashboard/keys) with API access and an enabled model. Check [Arena's API documentation](https://platform.arena.ai/docs) and your workspace's model list. `coding-router-preview` is the default example; use a model available to **your key**, and note that free-router keys can be restricted to specific clients. API usage may incur charges.

## 2. Install on Bazzite

1. Switch to **Desktop Mode** and open Konsole.
2. Clone this repository to a permanent location under your home directory. The current work is on the branch below:

   ```bash
   cd ~
   git clone --branch arena/3448d451-my-ally-assistant https://github.com/yamaharazef-hub/my-ally-assistant.git
   cd my-ally-assistant
   ```

   If you already cloned it, use `cd ~/my-ally-assistant` and `git pull` on the same branch instead. The launcher points to this folder; don't delete or move it after installing. If you move it, rerun the installer from the new location.
3. Create an API key at [Arena's Keys page](https://platform.arena.ai/dashboard/keys). In Konsole run:

   ```bash
   ./scripts/setup.py
   ```

   Paste the key at the hidden prompt and press Enter. Choose the model enabled for your key (or press Enter for `coding-router-preview`). Your key is saved in `~/.config/my-ally-assistant/config.json` (or `$XDG_CONFIG_HOME/my-ally-assistant/config.json`) with owner-only file permissions, **outside Git**. Never paste it in chat, commit it, or share the config file. To change the key/model, run setup again and restart the assistant.
4. Install the per-user application shortcut:

   ```bash
   ./scripts/install.py
   ```

5. Start **My Ally Assistant** from the desktop application launcher. Alternatively, start it from Konsole:

   ```bash
   python3 app.py --open
   ```

   The launcher prefers an installed host or Flatpak Chrome/Chromium and falls back to your default browser. Open `http://127.0.0.1:8765/` manually if necessary. Keep the terminal open when starting manually; press **Ctrl+C** to stop. Close the app via Steam when launched from Gaming Mode. If launched from the desktop shortcut, the server continues until its process is stopped or you log out; close it with `pkill -f '[p]ython3 .*my-ally-assistant/app.py'` before launching again. Only one instance can use port 8765.
6. Send a message. The top status reports whether a key is configured; it does **not** verify connectivity or authorization. Use the microphone button to dictate, review the text, then send. Allow microphone access if prompted. Toggle **Voice off / Voice on** for spoken replies. Recognition isn't continuous; no wake word is active.

## 3. Add it to Gaming Mode

1. In Desktop Mode, open Steam and select **Add a Game → Add a Non-Steam Game**.
2. Select **My Ally Assistant** from the app list and add it. If it is not listed, restart Steam after installing the shortcut, then try again.
3. Return to Gaming Mode and find **My Ally Assistant** in Library → Non-Steam. Launch it like a game. It opens a browser app window backed by the local server; this is not a Steam overlay or Decky plugin.
4. Use the touch screen, or choose a Steam Input layout that maps a stick/trackpad to mouse and buttons to clicks. Open Steam's on-screen keyboard when needed (the configured Steam keyboard shortcut varies with your controller layout). Permit the browser microphone the first time. Exit the app through Steam when finished.

Gaming Mode browser focus, controller mapping, audio permissions and voice recognition differ by Bazzite/browser version; test on your own Ally X. No hardware-specific behavior has been validated in this repository's development environment.

## 4. Developing the assistant

No npm dependencies or Python packages are needed.

```bash
# From the repository
python3 app.py                     # local server: http://127.0.0.1:8765/
python3 -m unittest discover -s tests -v
```

- `app.py`: local-only HTTP server, origin/session checks and Arena API bridge.
- `static/`: HTML, CSS, UI logic and icon. Refresh the browser after changes. Restart the server after editing Python.
- `scripts/setup.py`: private config. Environment variables `ARENA_API_KEY` and `ARENA_MODEL` override the file for development; avoid entering secrets into shell history.
- `scripts/install.py`: desktop shortcut; `scripts/launch.sh`: launcher.
- `tests/`: standard-library tests using a **mocked** provider, no API key needed.

The server binds to `127.0.0.1` only. It does not expose the key to the browser or accept arbitrary provider URLs. It posts the system prompt and up to the last 30 messages to `https://api.arena.ai/v1/chat/completions`. API responses and errors may vary by model and account; the integration is based on Arena's OpenAI-compatible gateway and requires a real API-enabled account to validate end-to-end. Chat history is stored in the browser's local storage, unencrypted; **New conversation** clears it in that browser. Voice recognition and synthesis are browser features, and may involve external services. Do not send sensitive information unless you accept the relevant providers' privacy terms.

### Troubleshooting

- **Setup required:** Run `./scripts/setup.py` and restart. Check the config location and permissions. An Arena website login is not the same as an API key.
- **Arena HTTP 401/403/404/429:** Check the key, API access restrictions, model name, billing and rate limits in Arena. A free-router key may be limited to a specific client. Re-run setup after changes. No credentials are logged by Ally.
- **Microphone unavailable:** Use a supported Chrome/Chromium build, allow microphone permission, and check Bazzite sound input. Some Chromium builds do not support speech recognition. Typing still works.
- **Address already in use:** Stop the existing Ally server before launching again, or run `python3 app.py --port 8766` and open the displayed URL. The desktop shortcut uses 8765.
- **Browser opens but no response:** The server must stay running; open the local URL printed by it. Check internet access and the error shown in the app.

## 5. Update and uninstall

```bash
cd ~/my-ally-assistant
git pull                          # pulls the branch currently checked out
./scripts/install.py              # refresh the desktop shortcut if needed
```

To uninstall, remove the non-Steam entry in Steam, then run:

```bash
rm -f ~/.local/share/applications/my-ally-assistant.desktop
rm -rf ~/.config/my-ally-assistant # deletes your key; use $XDG_CONFIG_HOME if set
```

Delete the repository folder if desired and clear the browser's site data for `127.0.0.1:8765` to remove saved conversations. If you used a custom `XDG_DATA_HOME`, remove the shortcut from its `applications` directory instead.
