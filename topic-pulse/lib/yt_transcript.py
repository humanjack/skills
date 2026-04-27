#!/usr/bin/env python3
"""Fetch a YouTube transcript by video id or URL.

Usage:
    python3 yt_transcript.py <video_id_or_url>

Prints the transcript text (single-line joined) on stdout. On any failure (no captions,
network error, missing dep) prints nothing and exits non-zero.

Auto-installs `youtube-transcript-api` to the user site on first use if missing.
"""
from __future__ import annotations

import re
import subprocess
import sys
from urllib.parse import parse_qs, urlparse


def extract_video_id(arg: str) -> str | None:
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", arg):
        return arg
    try:
        u = urlparse(arg)
    except ValueError:
        return None
    if u.hostname in ("youtu.be",):
        vid = u.path.lstrip("/")[:11]
        return vid if len(vid) == 11 else None
    if u.hostname and "youtube.com" in u.hostname:
        if u.path == "/watch":
            v = parse_qs(u.query).get("v", [None])[0]
            return v if v and len(v) == 11 else None
        m = re.match(r"^/(?:embed|shorts|live)/([A-Za-z0-9_-]{11})", u.path)
        if m:
            return m.group(1)
    return None


def ensure_dep() -> None:
    try:
        import youtube_transcript_api  # noqa: F401
        return
    except ImportError:
        pass
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--quiet", "--user", "youtube-transcript-api"],
        check=True,
    )


def fetch(video_id: str) -> str:
    from youtube_transcript_api import YouTubeTranscriptApi  # type: ignore

    try:
        chunks = YouTubeTranscriptApi.get_transcript(video_id, languages=["en", "en-US", "en-GB"])
    except Exception:
        try:
            chunks = YouTubeTranscriptApi.get_transcript(video_id)
        except Exception:
            return ""
    return " ".join(c.get("text", "").strip() for c in chunks if c.get("text"))


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        return 2
    vid = extract_video_id(argv[1])
    if not vid:
        return 1
    try:
        ensure_dep()
    except Exception:
        return 1
    text = fetch(vid)
    if not text:
        return 1
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
