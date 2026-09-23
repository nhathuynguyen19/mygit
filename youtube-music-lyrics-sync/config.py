"""Cài đặt chung cho YouTube Music Lyrics Sync Tool."""

# Poll interval (giây) cho việc kiểm tra window title
POLL_INTERVAL = 2

# Thời gian (giây) chờ trước khi hiện "Paused" khi không đổi bài
PAUSE_THRESHOLD = 30

# Overlay window
OVERLAY_WIDTH = 800
OVERLAY_HEIGHT = 400
OVERLAY_POSITION = "center"  # center, top, bottom

# Always-on-top
ALWAYS_ON_TOP = True

# API URLs
LYRICS_OVH_URL = "https://api.lyrics.ovh/v1/{artist}/{song}"
LRCLIB_URL = "https://lrclib.net"
LRCLIB_SEARCH_URL = "https://lrclib.net"

# Regex patterns cho YouTube Music window title
# Phù hợp với: "Song - Artist | YouTube Music" hoặc "Song - Artist · YouTube Music"
YM_TITLE_PATTERNS = [
    r"^(.+?)\s*-\s*(.+?)\s*\| YouTube Music$",
    r"^(.+?)\s*-\s*(.+?)\s*· YouTube Music$",
]

# Color scheme cho overlay
BG_COLOR = "#1a1a2e"
CURRENT_LINE_COLOR = "#ffffff"
CONTEXT_LINE_COLOR = "#888888"
HIGHLIGHT_COLOR = "#e94560"
FONT_FAMILY = "Segoe UI, Helvetica, Arial, sans-serif"
FONT_SIZE_CURRENT = 28
FONT_SIZE_CONTEXT = 20