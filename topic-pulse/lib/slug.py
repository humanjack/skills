#!/usr/bin/env python3
"""Topic → filesystem-safe slug.

Usage: python3 slug.py "<topic>"
"""
import re
import sys
import unicodedata


def slug(topic: str) -> str:
    s = unicodedata.normalize("NFKD", topic)
    s = s.encode("ascii", "ignore").decode("ascii")
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s or "untitled"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: slug.py <topic>")
    print(slug(" ".join(sys.argv[1:])))
