#!/usr/bin/env python3
"""Per-topic seen-index for topic-pulse.

Index lives at ~/.claude/topic-pulse/seen/<slug>.json and stores:
    [{"id": str, "url": str, "title": str, "source": str, "first_seen_at": ISO8601 UTC}, ...]

Subcommands:
    load    <slug>                  Print the full index as JSON.
    filter  <slug> < items.json     Read items JSON from stdin, write to stdout
                                     only those whose id is NOT in the seen index.
    append  <slug> < items.json     Read items JSON from stdin, append any new
                                     ids to the seen index with first_seen_at=now.
                                     Auto-prunes entries older than 90d while saving.
    prune   <slug>                  Remove entries older than 90 days.
    reset   <slug>                  Delete the index file for this topic.
    path    <slug>                  Print the index file path (no I/O).

Items JSON shape (input for filter/append):
    [{"id": "...", "url": "...", "title": "...", "source": "...", ...}, ...]
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import sys
from datetime import datetime, timedelta, timezone

ROOT = pathlib.Path(os.path.expanduser("~/.claude/topic-pulse/seen"))
PRUNE_DAYS = 90
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def validate_slug(slug: str) -> None:
    if not SLUG_RE.fullmatch(slug):
        raise ValueError(f"invalid slug: {slug!r}")


def index_path(slug: str) -> pathlib.Path:
    validate_slug(slug)
    return ROOT / f"{slug}.json"


def load(slug: str) -> list[dict]:
    p = index_path(slug)
    if not p.exists():
        return []
    try:
        with p.open() as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save(slug: str, entries: list[dict]) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    p = index_path(slug)
    tmp = p.with_suffix(".json.tmp")
    with tmp.open("w") as f:
        json.dump(entries, f, indent=2)
    tmp.replace(p)


def prune(entries: list[dict]) -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=PRUNE_DAYS)
    out = []
    for e in entries:
        ts = e.get("first_seen_at")
        if not ts:
            continue
        try:
            seen_at = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            if seen_at.tzinfo is None:
                continue
        except (ValueError, TypeError):
            continue
        if seen_at >= cutoff:
            out.append(e)
    return out


def cmd_load(slug: str) -> None:
    print(json.dumps(load(slug), indent=2))


def cmd_filter(slug: str) -> None:
    items = json.load(sys.stdin)
    entries = prune(load(slug))
    save(slug, entries)
    seen_ids = {e["id"] for e in entries if "id" in e}
    fresh = [it for it in items if it.get("id") not in seen_ids]
    print(json.dumps(fresh, indent=2))


def cmd_append(slug: str) -> None:
    items = json.load(sys.stdin)
    entries = prune(load(slug))
    seen_ids = {e["id"] for e in entries if "id" in e}
    now = datetime.now(timezone.utc).isoformat()
    added = 0
    for it in items:
        iid = it.get("id")
        if not iid or iid in seen_ids:
            continue
        entries.append({
            "id": iid,
            "url": it.get("url", ""),
            "title": it.get("title", ""),
            "source": it.get("source", ""),
            "first_seen_at": now,
        })
        seen_ids.add(iid)
        added += 1
    save(slug, entries)
    print(json.dumps({"added": added, "total": len(entries)}))


def cmd_prune(slug: str) -> None:
    entries = prune(load(slug))
    save(slug, entries)
    print(json.dumps({"total": len(entries)}))


def cmd_reset(slug: str) -> None:
    p = index_path(slug)
    if p.exists():
        p.unlink()
    print(json.dumps({"reset": str(p)}))


def cmd_path(slug: str) -> None:
    print(str(index_path(slug)))


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2
    cmd, slug = argv[1], argv[2]
    try:
        validate_slug(slug)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    handlers = {
        "load": cmd_load,
        "filter": cmd_filter,
        "append": cmd_append,
        "prune": cmd_prune,
        "reset": cmd_reset,
        "path": cmd_path,
    }
    if cmd not in handlers:
        print(f"unknown command: {cmd}", file=sys.stderr)
        return 2
    handlers[cmd](slug)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
