"""Entry point cho YouTube Music Lyrics Sync Tool."""

import sys
import time
import json
import os
from typing import Optional, Tuple, List

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction
from PyQt5.QtGui import QKeySequence

from config import POLL_INTERVAL, PAUSE_THRESHOLD
from detector import poll_song_change, detect_current_song
from lyrics import fetch_lyrics_by_search
from lrc import parse_lrc, get_current_line
from overlay import LyricsOverlay
from logger import log


class LyricsApp:
    """Ứng dụng chính: detect → fetch → sync → display."""

    def __init__(self, overlay: LyricsOverlay):
        self._overlay = overlay
        self._current_query: Optional[str] = None
        self._current_title: Optional[str] = None
        self._timeline: List[Tuple[float, str]] = []
        self._song_start: float = 0.0
        self._last_update_index: int = -1
        self._poll_count = 0

        # Timer 1: Poll window title mỗi POLL_INTERVAL giây
        self._poll_timer = QTimer()
        self._poll_timer.timeout.connect(self._on_poll)
        self._poll_timer.start(POLL_INTERVAL * 1000)

        # Timer 2: Update highlight lyrics mỗi 500ms
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._on_update_overlay)
        self._update_timer.start(500)

        # Timer 3: Update sync time display mỗi 1s
        self._sync_time_timer = QTimer()
        self._sync_time_timer.timeout.connect(self._on_update_sync_time)
        self._sync_time_timer.start(1000)

        # Connect overlay sync signal
        self._overlay.syncRequested.connect(self._on_sync_requested)

    def _on_poll(self):
        """Kiểm tra window title có đổi bài không."""
        self._poll_count += 1
        result = poll_song_change(self._current_query)
        current_query = result[0]
        has_changed = result[1]

        if current_query:
            log(f"[main] Poll #{self._poll_count}: query='{current_query}'")

        if has_changed and current_query:
            song_info = detect_current_song()
            if song_info:
                self._current_title = song_info[1]
            log(f"[main] Song changed!")
            self._on_song_change(current_query)

    def _on_song_change(self, query: str):
        """Bài hát thay đổi → fetch lyrics, reset timeline."""
        self._current_query = query
        self._song_start = time.monotonic()
        self._last_update_index = -1

        if self._current_title:
            self._overlay.set_song_info(self._current_title, "")

        self._fetch_lyrics(query)

    def _fetch_lyrics(self, query: str):
        """Fetch lyrics bằng search-based approach."""
        log(f"[main] Search query: {query}")
        lyrics_text = fetch_lyrics_by_search(query)
        if lyrics_text:
            log(f"[main] Lyrics fetched, length: {len(lyrics_text)} chars")
            self._timeline = parse_lrc(lyrics_text)
            log(f"[main] Parsed {len(self._timeline)} lines")
            lines = [text for _, text in self._timeline]
            self._overlay._webview.page().runJavaScript(
                f"window.setLines({json.dumps(lines, ensure_ascii=False)});"
            )
        else:
            log(f"[main] No lyrics found")
            self._timeline = []
            self._overlay.show_not_found(query, "")

    def _on_update_overlay(self):
        """Cập nhật highlight dòng lyrics theo thời gian."""
        if not self._timeline:
            if self._current_query and (time.monotonic() - self._song_start) > PAUSE_THRESHOLD:
                self._overlay.show_paused()
            return

        elapsed = time.monotonic() - self._song_start
        idx = get_current_line(self._timeline, elapsed)

        if idx != self._last_update_index:
            self._last_update_index = idx
            total = len(self._timeline)
            _, text = self._timeline[idx]
            self._overlay.update_line(idx, total, text)

    def _on_update_sync_time(self):
        """Cập nhật sync time hiển thị."""
        if self._timeline:
            elapsed = time.monotonic() - self._song_start
            self._overlay.set_sync_time(elapsed)

    def _on_sync_requested(self):
        """User request sync → reset song_start."""
        log("[main] Sync requested by user")
        self._song_start = time.monotonic()
        self._last_update_index = -1
        self._overlay.set_sync_time(0)

    def start(self):
        """Khởi chạy ứng dụng."""
        self._overlay.start_sync_polling()
        self._overlay.show()

    def stop(self):
        """Dừng ứng dụng."""
        self._overlay.stop_sync_polling()


class MainWindow(QMainWindow):
    """MainWindow chính — handle keyboard shortcuts."""

    def __init__(self, app: LyricsApp):
        super().__init__()
        self._app = app
        self.setWindowTitle("YouTube Music Lyrics Sync")
        self.setMinimumSize(1, 1)  # Hidden window

        # Keyboard shortcut: Ctrl+Shift+S to sync
        self._sync_action = QAction("Sync Lyrics", self)
        self._sync_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self._sync_action.triggered.connect(self._on_sync)
        self.addAction(self._sync_action)

        # Keyboard shortcut: Escape to quit
        self._quit_action = QAction("Quit", self)
        self._quit_action.setShortcut(QKeySequence("Escape"))
        self._quit_action.triggered.connect(self._on_quit)
        self.addAction(self._quit_action)

    def _on_sync(self):
        self._app._on_sync_requested()

    def _on_quit(self):
        self._app.stop()
        self.close()
        QApplication.quit()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("YouTube Music Lyrics Sync")

    display_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "display", "index.html")
    overlay = LyricsOverlay(display_path)
    lyrics_app = LyricsApp(overlay)

    # Create hidden main window for keyboard shortcuts
    main_window = MainWindow(lyrics_app)
    main_window.show()

    lyrics_app.start()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()