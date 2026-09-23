"""PyQt5 overlay window hiển thị lyrics."""

import json
import os
import time

from PyQt5.QtCore import Qt, QUrl, QTimer, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView

from config import (
    OVERLAY_WIDTH,
    OVERLAY_HEIGHT,
    ALWAYS_ON_TOP,
    BG_COLOR,
)


class LyricsOverlay(QMainWindow):
    """Floating overlay window hiển thị lyrics đồng bộ."""

    # Signal khi user request sync
    syncRequested = pyqtSignal()

    def __init__(self, display_path: str):
        super().__init__()
        self._display_path = display_path
        self._sync_polling = False
        self._setup_window()
        self._setup_webview()
        self._setup_shortcuts()

    def _setup_window(self):
        self.setWindowTitle("YouTube Music Lyrics")
        self.setFixedSize(OVERLAY_WIDTH, OVERLAY_HEIGHT)

        flags = Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        if not ALWAYS_ON_TOP:
            flags &= ~Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet(f"background: {BG_COLOR}; border-radius: 12px;")

        self._center_on_screen()

    def _setup_webview(self):
        self._webview = QWebEngineView(self)
        self.setCentralWidget(self._webview)

        url = QUrl.fromLocalFile(os.path.abspath(self._display_path))
        self._webview.load(url)

        # Poll sync flag mỗi 500ms, nhưng chỉ sau khi page load xong
        self._sync_timer = QTimer(self)
        self._sync_timer.timeout.connect(self._check_sync)

        # Chờ page load xong mới start polling
        self._webview.loadFinished.connect(self._on_load_finished)

    def _on_load_finished(self, ok):
        if ok:
            print("[overlay] Page loaded, starting sync polling")
            self._sync_timer.start(500)
        else:
            print("[overlay] Page load failed")

    def _setup_shortcuts(self):
        # Keyboard shortcut sẽ được setup trong main.py
        pass

    def _center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - OVERLAY_WIDTH) // 2
        y = (screen.height() - OVERLAY_HEIGHT) // 2
        self.move(x, y)

    def _check_sync(self):
        """Poll JS sync flag."""
        if not self._sync_polling:
            return
        self._webview.page().runJavaScript(
            "isSyncRequested()",
            lambda result: self._on_sync_requested(result)
        )

    def _on_sync_requested(self, result):
        """Callback khi JS flag là True."""
        if result:
            self.syncRequested.emit()

    def start_sync_polling(self):
        """Bắt đầu poll sync flag."""
        self._sync_polling = True

    def stop_sync_polling(self):
        """Dừng poll sync flag."""
        self._sync_polling = False

    def update_line(self, index: int, total: int, text: str):
        """Cập nhật dòng lyrics đang phát."""
        self._webview.page().runJavaScript(
            f"window.setLine({index}, {total}, {self._js_str(text)});"
        )

    def set_song_info(self, song: str, artist: str):
        """Hiện thông tin bài hát khi đổi bài."""
        info = f"{song} — {artist}"
        self._webview.page().runJavaScript(
            f"window.setSongInfo({self._js_str(info)});"
        )

    def show_not_found(self, song: str, artist: str):
        """Hiện thông báo không tìm thấy lyrics."""
        msg = f"Lyrics not found: {song} - {artist}"
        self._webview.page().runJavaScript(
            f"window.setNotFound({self._js_str(msg)});"
        )

    def show_paused(self):
        """Hiện trạng thái Pause."""
        self._webview.page().runJavaScript("window.setPaused();")

    def set_sync_time(self, elapsed: float):
        """Hiện sync time."""
        mins = int(elapsed) // 60
        secs = int(elapsed) % 60
        ts = f"{mins:02d}:{secs:02d}"
        self._webview.page().runJavaScript(
            f"setSyncTime('{ts}');"
        )

    @staticmethod
    def _js_str(s: str) -> str:
        """Escape string cho JavaScript."""
        return json.dumps(s, ensure_ascii=False)