"""Phát hiện bài hát đang phát từ cửa sổ YouTube Music của Brave."""

import re
import subprocess
from typing import Optional, Tuple

from config import POLL_INTERVAL, YM_TITLE_PATTERNS
from logger import log


def _run_wmctrl() -> Optional[str]:
    """Chạy `wmctrl -l` trả về output hoặc None."""
    try:
        result = subprocess.run(
            ["wmctrl", "-l"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def _get_active_window_id() -> Optional[str]:
    """Lấy ID của active window qua wmctrl."""
    try:
        result = subprocess.run(
            ["wmctrl", "-l"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            for line in result.stdout.strip().splitlines():
                parts = line.split(None, 4)
                if len(parts) >= 5 and "*" in parts[1]:
                    return parts[0]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def _parse_ytm_title(title: str) -> Optional[str]:
    """Parse tiêu đề YouTube Music → trả về search query.

    Bỏ "| YouTube Music" ở cuối, trả về phần còn lại để search.
    LRCLIB search fuzzy nên không cần tách chính xác artist/song.

    Ví dụ: "Music - Unwritten in the Stars | YouTube Music"
    → "Music - Unwritten in the Stars"
    """
    # Bỏ "| YouTube Music" ở cuối
    m = re.match(r"^(.+?)\s*\| YouTube Music$", title)
    if m:
        return m.group(1).strip()

    # Không có "| YouTube Music" — bỏ qua các suffix đã biết
    for suffix in [" · YouTube Music", " - YouTube Music"]:
        if title.endswith(suffix):
            return title[:-len(suffix)].strip()

    return title.strip() if title.strip() else None


def _parse_youtube_title(title: str) -> Optional[str]:
    """Parse tiêu đề YouTube thường → trả về search query.

    YouTube title format: "- Song - Artist | YouTube"
    hoặc "- Song - Artist - YouTube"
    """
    # Bỏ "| YouTube" hoặc "- YouTube" ở cuối
    for suffix in [" | YouTube", " - YouTube"]:
        if title.endswith(suffix):
            title = title[:-len(suffix)].strip()
            break

    # YouTube thường dùng format: "- Song - Artist"
    # Tách theo " - "
    parts = re.split(r"\s*-\s*", title)
    if len(parts) >= 2:
        # Phần đầu tiên sau "-" đầu tiên là song name
        # Ví dụ: "- Dutch guy REACTS: NỖI ĐAU - HÒA MINZY"
        # → parts = ["", "Dutch guy REACTS: NỖI ĐAU", "HÒA MINZY"]
        # Song = parts[1], Artist = parts[2]
        song = parts[1].strip() if len(parts) > 1 else title
        return song

    return title.strip() if title.strip() else None


def detect_current_song() -> Optional[Tuple[str, str]]:
    """Trả về (song_name, window_title) của bài đang phát, hoặc None.

    song_name: tên bài để search lyrics
    window_title: tiêu đề gốc để hiện thị
    """
    output = _run_wmctrl()
    if not output:
        log("[detector] wmctrl không chạy được")
        return None

    active_id = _get_active_window_id()

    best_match = None
    best_query = None
    is_active = False

    for line in output.strip().splitlines():
        parts = line.split(None, 4)
        if len(parts) < 5:
            continue

        window_id = parts[0]
        window_title = parts[4]

        log(f"[detector] Window: {window_title}")

        # Xét window YouTube Music hoặc YouTube thường
        is_ytm = "YouTube Music" in window_title
        is_yt = "youtube.com" in window_title.lower() or "youtu.be" in window_title.lower() or window_title.endswith("- YouTube")
        if not is_ytm and not is_yt:
            continue

        # Dùng parser phù hợp theo loại YouTube
        if is_ytm:
            query = _parse_ytm_title(window_title)
        else:
            query = _parse_youtube_title(window_title)
        if not query:
            continue

        # Ưu tiên active window
        if active_id and window_id == active_id:
            log(f"[detector] Active match: query='{query}'")
            return (query, window_title)

        if not is_active:
            best_match = window_title
            best_query = query
            is_active = True

    if best_match:
        log(f"[detector] Best match: query='{best_query}'")
        return (best_query, best_match)

    log(f"[detector] No YouTube window found")
    return None


def poll_song_change(last_song: Optional[str]) -> Tuple[Optional[str], bool]:
    """Poll window title, trả về (current_query, has_changed)."""
    result = detect_current_song()
    if result:
        current_query = result[0]
    else:
        current_query = None

    has_changed = current_query is not None and current_query != last_song
    return current_query, has_changed