"""Fetch lyrics từ nhiều source, ưu tiên search-based approach."""

import json
import urllib.request
import urllib.parse
import re
from typing import Optional, Tuple, List

from config import (
    LYRICS_OVH_URL,
    LRCLIB_URL,
    LRCLIB_SEARCH_URL,
)
from logger import log

_cache: dict[str, Optional[str]] = {}


def _fetch(url: str, retries: int = 2) -> Optional[str]:
    """GET URL với retry, trả về response text hoặc None."""
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "LRCGET/0.2.0 (https://github.com/tranxuanthang/lrclib)",
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status == 200:
                    return resp.read().decode("utf-8")
                elif resp.status == 429:
                    import time
                    wait = int(resp.headers.get("Retry-After", 2))
                    log(f"[lyrics] Rate limited, waiting {wait}s...")
                    time.sleep(wait)
                    continue
                else:
                    log(f"[lyrics] HTTP {resp.status} for {url}")
        except urllib.error.HTTPError as e:
            log(f"[lyrics] HTTP {e.code} for {url}")
            if e.code == 429:
                import time
                time.sleep(2)
                continue
            return None
        except Exception as e:
            log(f"[lyrics] Fetch error (attempt {attempt}): {e}")
            if attempt < retries:
                import time
                time.sleep(1)
                continue
            return None
    return None


def _parse_lrclib_search(body: str) -> Optional[dict]:
    """Parse LRCLIB search response → trả về track info tốt nhất."""
    try:
        results = json.loads(body)
        if not isinstance(results, list) or len(results) == 0:
            return None

        # Chọn track phù hợp nhất:
        # 1. Ưu tiên có syncedLyrics
        # 2. Ưu tiên không instrumental
        # 3. Lần đầu (đã được LRCLIB xếp hạng relevance)
        for track in results:
            if track.get("syncedLyrics") and not track.get("instrumental"):
                return track

        # Fallback: track đầu tiên có syncedLyrics
        for track in results:
            if track.get("syncedLyrics"):
                return track

        # Fallback: track đầu tiên
        return results[0] if results else None
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        log(f"[lyrics] LRCLIB search parse error: {e}")
        return None


def _parse_lrclib_get(body: str) -> Optional[dict]:
    """Parse LRCLIB /api/get response."""
    try:
        data = json.loads(body)
        if "error" in data:
            log(f"[lyrics] LRCLIB error: {data.get('message', '')}")
            return None
        return data
    except (json.JSONDecodeError, KeyError) as e:
        log(f"[lyrics] LRCLIB get parse error: {e}")
        return None


def _get_synced_lyrics(track: dict) -> Optional[str]:
    """Trả về syncedLyrics hoặc plainLyrics từ track."""
    synced = track.get("syncedLyrics")
    if synced:
        return synced
    plain = track.get("plainLyrics")
    if plain:
        log("[lyrics] No synced, using plain")
        return plain
    return None


# ==================== PUBLIC API ====================

def search_track(query: str) -> Optional[dict]:
    """Search LRCLIB bằng query string.

    Trả về track info dict hoặc None.
    """
    q = urllib.parse.quote(query.strip())
    url = f"{LRCLIB_SEARCH_URL}/api/search?q={q}"
    log(f"[lyrics] LRCLIB search: query='{query}'")
    body = _fetch(url)
    if body:
        try:
            results = json.loads(body)
            log(f"[lyrics] LRCLIB search: {len(results)} results")
        except json.JSONDecodeError:
            log(f"[lyrics] LRCLIB search: invalid JSON")
            return None
        track = _parse_lrclib_search(body)
        if track:
            name = track.get("trackName") or track.get("name", "?")
            artist = track.get("artistName", "?")
            log(f"[lyrics] Search match: {name} - {artist} (id={track.get('id')})")
            return track
    return None


def get_lyrics_by_id(track_id: int) -> Optional[str]:
    """Fetch synced lyrics bằng track ID."""
    url = f"{LRCLIB_URL}/api/get/{track_id}"
    log(f"[lyrics] LRCLIB get by id: {url}")
    body = _fetch(url)
    if body:
        track = _parse_lrclib_get(body)
        if track:
            return _get_synced_lyrics(track)
    return None


def fetch_lyrics_by_search(query: str) -> Optional[str]:
    """Fetch lyrics bằng cách search LRCLIB.

    Thử theo thứ tự:
    1. Full query
    2. Phần cuối sau " - " (cho format "Category - Song")
    3. Phần đầu trước " - " (cho format "Song - Artist")
    """
    cache_key = f"search:{query.lower().strip()}"
    if cache_key in _cache:
        log(f"[lyrics] Cache hit: {query}")
        return _cache[cache_key]

    # Thử 1: Full query
    track = search_track(query)
    if track:
        lyrics = _get_synced_lyrics(track)
        if lyrics:
            _cache[cache_key] = lyrics
            log(f"[lyrics] Found lyrics via search: {query}")
            return lyrics

    # Thử 2: Fallback — tách theo " - "
    parts = re.split(r"\s*[-–—]\s*", query)
    if len(parts) >= 2:
        # Ưu tiên phần cuối (thường là bài hát trong format "Category - Song")
        for part in [parts[-1], parts[0]]:
            part = part.strip()
            if not part:
                continue
            track = search_track(part)
            if track:
                lyrics = _get_synced_lyrics(track)
                if lyrics:
                    _cache[cache_key] = lyrics
                    log(f"[lyrics] Found lyrics via fallback: {part}")
                    return lyrics

    log(f"[lyrics] No lyrics found for: {query}")
    _cache[cache_key] = None
    return None


def fetch_lyrics(artist: str, song: str, duration: Optional[int] = None) -> Optional[str]:
    """Fetch lyrics cho bài hát.

    Phiên bản cũ: dùng artist + song (ít chính xác).
    Khuyến nghị dùng fetch_lyrics_by_search thay.
    """
    key = (artist.lower().strip(), song.lower().strip())
    if key in _cache:
        log(f"[lyrics] Cache hit: {song} - {artist}")
        return _cache[key]

    # Thử lyrics.ovh
    artist_q = urllib.parse.quote(artist.strip())
    song_q = urllib.parse.quote(song.strip())

    url = LYRICS_OVH_URL.format(artist=artist_q, song=song_q)
    log(f"[lyrics] lyrics.ovh: {url}")
    body = _fetch(url)

    if body:
        try:
            data = json.loads(body)
            lyrics = data.get("lyrics")
            if lyrics:
                _cache[key] = lyrics
                log(f"[lyrics] Found plain lyrics: {song} - {artist}")
                return lyrics
        except (json.JSONDecodeError, KeyError):
            pass

    # Fallback: search LRCLIB
    query = f"{artist} {song}"
    lyrics = fetch_lyrics_by_search(query)
    if lyrics:
        _cache[key] = lyrics
    return lyrics