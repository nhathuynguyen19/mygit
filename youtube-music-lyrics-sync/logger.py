"""File logger cho YouTube Music Lyrics Sync Tool."""

import os
import sys
from datetime import datetime

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.log")

_max_size = 5 * 1024 * 1024  # 5MB


def _rotate():
    """Rotate log nếu quá lớn."""
    try:
        if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > _max_size:
            old = LOG_FILE + ".old"
            if os.path.exists(old):
                os.remove(old)
            os.rename(LOG_FILE, old)
    except OSError:
        pass


def log(msg: str):
    """Ghi log ra file và stdout."""
    _rotate()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"

    # Ghi ra file
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass

    # Ghi ra stdout
    print(line)