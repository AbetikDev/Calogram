"""
Calogram — unified launcher.
Starts both the Flask backend (port 5001) and a static HTTP frontend (port 5500)
from the project root.

Usage:
    python run.py

Stop with Ctrl+C — both processes are terminated automatically.
"""

import os
import sys
import signal
import subprocess
import threading
import time

from server.app import create_app


app = create_app()

# ── Colorama (optional, install with: pip install colorama) ───────────────────
try:
    from colorama import init as _colorama_init, Fore, Style
    _colorama_init(autoreset=True)
    _HAS_COLOR = True
except ImportError:
    _HAS_COLOR = False

    class Fore:   # noqa: F811
        GREEN = CYAN = YELLOW = RED = MAGENTA = WHITE = RESET = ''

    class Style:  # noqa: F811
        BRIGHT = DIM = RESET_ALL = ''


def _c(text, *codes):
    if not _HAS_COLOR:
        return text
    return ''.join(codes) + text + Style.RESET_ALL


# ── Config ────────────────────────────────────────────────────────────────────
try:
    from dotenv import dotenv_values
    _env = dotenv_values(os.path.join(os.path.dirname(__file__), 'server', '.env'))
except ImportError:
    _env = {}

FLASK_PORT    = _env.get('FLASK_PORT',    os.getenv('PORT', os.getenv('FLASK_PORT', '10000')))
FRONTEND_PORT = _env.get('FRONTEND_PORT', os.getenv('FRONTEND_PORT', '5500'))

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON   = sys.executable

# Colour scheme per process
_STYLES = {
    'API':  (Fore.GREEN,  Style.BRIGHT),
    'WEB':  (Fore.CYAN,   Style.BRIGHT),
    'SYS':  (Fore.YELLOW, Style.BRIGHT),
    'ERR':  (Fore.RED,    Style.BRIGHT),
}


def _tag(label):
    """Returns a coloured [LABEL] prefix."""
    colors = _STYLES.get(label, (Fore.WHITE,))
    return _c(f'[{label}]', *colors)


def _stream(proc, label):
    """Forward subprocess stdout/stderr to our stdout with a coloured label."""
    for line in iter(proc.stdout.readline, b''):
        text = line.decode('utf-8', errors='replace').rstrip()
        # Highlight error lines in red
        if any(kw in text.lower() for kw in ('error', 'traceback', 'exception', 'critical')):
            text = _c(text, Fore.RED)
        elif any(kw in text.lower() for kw in ('warning', 'warn')):
            text = _c(text, Fore.YELLOW)
        print(f'{_tag(label)} {text}', flush=True)


def main():
    LINE = _c('━' * 60, Fore.MAGENTA, Style.BRIGHT)
    print(LINE)
    print(_c('  Calogram  —  starting all services', Fore.WHITE, Style.BRIGHT))
    print(LINE)
    print(f'  {_c("Backend  ", Fore.GREEN, Style.BRIGHT)}  →  '
          f'{_c(f"http://127.0.0.1:{FLASK_PORT}/api/ping", Fore.CYAN)}')
    print(f'  {_c("Frontend ", Fore.CYAN,  Style.BRIGHT)}  →  '
          f'{_c(f"http://0.0.0.0:{FRONTEND_PORT}/index.html", Fore.CYAN)}  (публічно: http://<ваш_IP>:{FRONTEND_PORT}/index.html)')
    print(f'  {_c("Tip", Fore.YELLOW)}  Press Ctrl+C to stop both servers.')
    print(LINE)

    # ── Backend ───────────────────────────────────────────────────
    backend = subprocess.Popen(
        [PYTHON, os.path.join(ROOT_DIR, 'server', 'run.py')],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=ROOT_DIR,
    )

    # ── Frontend (bind to 0.0.0.0 — accessible from public IP) ────────────────
    frontend = subprocess.Popen(
        [PYTHON, '-m', 'http.server', FRONTEND_PORT, '--bind', '0.0.0.0'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=ROOT_DIR,
    )

    # Stream logs from both processes
    for proc, label in [(backend, 'API'), (frontend, 'WEB')]:
        t = threading.Thread(target=_stream, args=(proc, label), daemon=True)
        t.start()

    processes = {'backend': backend, 'frontend': frontend}

    def _stop(sig=None, frame=None):
        print(f'\n{_tag("SYS")} {_c("Shutting down…", Fore.YELLOW)}', flush=True)
        for proc in processes.values():
            try:
                proc.terminate()
            except Exception:
                pass
        sys.exit(0)

    signal.signal(signal.SIGINT,  _stop)
    signal.signal(signal.SIGTERM, _stop)

    # Watch for unexpected exits
    while True:
        if backend.poll() is not None:
            print(f'{_tag("ERR")} {_c("Backend exited unexpectedly. Stopping…", Fore.RED)}', flush=True)
            _stop()
        if frontend.poll() is not None:
            print(f'{_tag("ERR")} {_c("Frontend server exited unexpectedly. Stopping…", Fore.RED)}', flush=True)
            _stop()
        time.sleep(1)


if __name__ == '__main__':
    main()
