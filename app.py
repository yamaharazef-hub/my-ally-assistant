#!/usr/bin/env python3
"""Local-only web UI and Arena API bridge; Python standard library only."""
import argparse
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
CONFIG = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')) / 'my-ally-assistant' / 'config.json'
SYSTEM = ('You are Ally, a helpful, concise voice and text assistant for an ASUS ROG Ally X running Bazzite Linux. '
          'Be practical and transparent. Never claim to have controlled the device, searched the web, or performed '
          'an action unless you actually did. Explain commands and ask before suggesting destructive changes.')
MAX_BODY = 100_000


def settings():
    try:
        config = json.loads(CONFIG.read_text())
        if not isinstance(config, dict):
            config = {}
    except (OSError, ValueError):
        config = {}
    return {'key': os.environ.get('ARENA_API_KEY', config.get('api_key', '')),
            'model': os.environ.get('ARENA_MODEL', config.get('model', 'coding-router-preview'))}


def chat(messages, config):
    payload = json.dumps({'model': config['model'], 'messages': [{'role': 'system', 'content': SYSTEM}] + messages, 'stream': False}).encode()
    request = urllib.request.Request('https://api.arena.ai/v1/chat/completions', data=payload,
        headers={'Authorization': 'Bearer ' + config['key'], 'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(request, timeout=90) as response:
        result = json.load(response)
    reply = result['choices'][0]['message']['content']
    if not isinstance(reply, str) or not reply.strip():
        raise ValueError('The AI returned an empty response.')
    return reply


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Do not log prompts, API keys, or URLs containing query parameters.
        return

    def send_json(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def local_host(self):
        return self.headers.get('Host', '') in (f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}')

    def do_GET(self):
        if not self.local_host():
            return self.send_json(403, {'error': 'Invalid host.'})
        if self.path == '/api/status':
            config = settings()
            return self.send_json(200, {'configured': bool(config['key']), 'model': config['model'], 'token': self.server.token})
        files = {'/': ('index.html', 'text/html; charset=utf-8'), '/style.css': ('style.css', 'text/css; charset=utf-8'), '/app.js': ('app.js', 'text/javascript; charset=utf-8'), '/icon.svg': ('icon.svg', 'image/svg+xml')}
        if self.path not in files:
            return self.send_json(404, {'error': 'Not found.'})
        filename, content_type = files[self.path]
        data = (ROOT / 'static' / filename).read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Security-Policy', "default-src 'self'; connect-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if not self.local_host():
            return self.send_json(403, {'error': 'Invalid host.'})
        origin = self.headers.get('Origin', '')
        allowed = (f'http://127.0.0.1:{self.server.server_port}', f'http://localhost:{self.server.server_port}')
        if origin not in allowed or not secrets.compare_digest(self.headers.get('X-Ally-Token', ''), self.server.token):
            return self.send_json(403, {'error': 'Invalid request origin or session.'})
        if self.path != '/api/chat':
            return self.send_json(404, {'error': 'Not found.'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length <= 0 or length > MAX_BODY:
                raise ValueError('Request is too large or empty.')
            data = json.loads(self.rfile.read(length))
            messages = data['messages']
            if not isinstance(messages, list) or not 1 <= len(messages) <= 30:
                raise ValueError('Send between 1 and 30 messages.')
            if any(not isinstance(m, dict) or m.get('role') not in ('user', 'assistant') or not isinstance(m.get('content'), str) or not 0 < len(m['content']) <= 8000 for m in messages):
                raise ValueError('Invalid message.')
            if messages[-1]['role'] != 'user':
                raise ValueError('The last message must be from the user.')
            config = settings()
            if not config['key']:
                return self.send_json(503, {'error': 'Arena API key not configured. Run ./scripts/setup.py, then restart Ally.'})
            reply = chat([{'role': m['role'], 'content': m['content']} for m in messages], config)
            self.send_json(200, {'reply': reply})
        except urllib.error.HTTPError as exc:
            # Avoid forwarding raw provider bodies, which could expose sensitive data.
            self.send_json(502, {'error': f'Arena returned HTTP {exc.code}. Check your API access, key, model and usage limits.'})
        except (urllib.error.URLError, TimeoutError, socket.timeout):
            self.send_json(502, {'error': 'Could not reach Arena. Check your internet connection and try again.'})
        except (ValueError, KeyError, TypeError, json.JSONDecodeError):
            self.send_json(400, {'error': 'Invalid request or unexpected AI response. Check the model and try again.'})


def open_browser(url):
    # Prefer Chromium for Web Speech recognition; fall back to the default browser.
    import shutil
    for name in ('chromium', 'chromium-browser', 'google-chrome', 'google-chrome-stable'):
        path = shutil.which(name)
        if path:
            subprocess.Popen([path, '--app=' + url], start_new_session=True)
            return
    if shutil.which('flatpak'):
        for app in ('com.google.Chrome', 'org.chromium.Chromium'):
            if subprocess.run(['flatpak', 'info', app], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
                subprocess.Popen(['flatpak', 'run', app, '--app=' + url], start_new_session=True)
                return
    subprocess.Popen(['xdg-open', url], start_new_session=True)


def main():
    parser = argparse.ArgumentParser(description='Run Ally locally')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--open', action='store_true', help='open an app-style browser window')
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    server.token = secrets.token_urlsafe(32)
    url = f'http://127.0.0.1:{server.server_port}/'
    print(f'Ally is running at {url} — press Ctrl+C to stop.', flush=True)
    if args.open:
        threading.Timer(0.3, open_browser, args=[url]).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == '__main__':
    main()
