"""Parser cho LRC lyrics format."""

import re
from typing import List, Tuple

# Regex cho [mm:ss.xx] hoặc [mm:ss] timestamp
LRC_TIMESTAMP_RE = re.compile(r"\[(\d{2}):(\d{2})(?:\.(\d{2}))?\]")


def parse_lrc(text: str) -> List[Tuple[float, str]]:
    """Parse LRC lyrics text thành list (timestamp_giây, nội_dung).

    Với dòng không có timestamp, gắn timestamp của dòng trước đó + 5s (default).
    """
    timeline: List[Tuple[float, str]] = []
    last_ts = 0.0

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        matches = LRC_TIMESTAMP_RE.findall(line)
        if matches:
            # Lấy timestamp cuối cùng trong dòng (một số bài có nhiều timestamp)
            mm, ss, xx = matches[-1]
            ts = int(mm) * 60 + int(ss)
            if xx:
                ts += int(xx) / 100.0
            # Nội dung là dòng sau khi bỏ tất cả timestamps
            content = LRC_TIMESTAMP_RE.sub("", line).strip()
            if content:
                timeline.append((ts, content))
                last_ts = ts
        else:
            # Dòng không có timestamp → gắn vào dòng trước + 5s
            content = line.strip()
            if content:
                last_ts += 5
                timeline.append((last_ts, content))

    return timeline


def get_current_line(timeline: List[Tuple[float, str]], elapsed: float) -> int:
    """Trả về index dòng cần hiện tại thời điểm elapsed (giây).

    Nếu elapsed trước dòng đầu → trả -1 (hiện dòng đầu tiên với chờ).
    Nếu elapsed sau dòng cuối → trả len(timeline) - 1.
    """
    if not timeline:
        return -1

    if elapsed < timeline[0][0]:
        return 0

    for i in range(len(timeline) - 1):
        if timeline[i][0] <= elapsed < timeline[i + 1][0]:
            return i

    return len(timeline) - 1