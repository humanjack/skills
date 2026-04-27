# topic-pulse — test scenarios

These are manual integration tests against the live skill. Each row is one invocation.
Run them top to bottom on a fresh machine (or after `seen/<slug>.json` is cleared).

| #   | Scenario                       | Command                                                       | Pass criteria |
|-----|--------------------------------|---------------------------------------------------------------|---------------|
| T1  | Default run, fresh topic       | `/topic-pulse "AI agents"`                                    | ≥ 3 source domains, valid markdown matching SKILL.md output spec, header shows `Skipped: 0` |
| T2  | Re-run same topic same day     | repeat T1                                                     | Header shows `Skipped > 0`; no story from T1 reappears in Stories |
| T3  | YouTube-only                   | `/topic-pulse "AI agents" --sources youtube`                  | All Stories are YouTube clusters with `**title** — channel · duration` line |
| T4  | Multi-source filter            | `/topic-pulse "AI agents" --sources youtube,reddit`           | Sources line shows only `youtube, reddit`; no web/news/hn URLs in body |
| T5  | List sources                   | `/topic-pulse --list-sources`                                 | Prints enabled sources from `~/.claude/topic-pulse/sources.json` |
| T6  | Add source                     | `/topic-pulse --add-source hackernews` then T5                | hackernews enabled in config; persisted to disk |
| T7  | Remove source                  | `/topic-pulse --remove-source reddit` then T5                 | reddit disabled; persisted; T8 next run does not collect from reddit |
| T8  | Refuse last-source disable     | disable everything except one, then `--remove-source <last>`  | Skill refuses with a clear message; config unchanged |
| T9  | Reset seen                     | `/topic-pulse "AI agents" --reset`                            | `Skipped: 0` even after T2; `seen/ai-agents.json` deleted |
| T10 | Include-seen                   | `/topic-pulse "AI agents" --include-seen` (after T2)          | Includes prior items; index file unchanged in size after run |
| T11 | Weekly window                  | `/topic-pulse "AI agents" --window 7d`                        | Items span > 24h timestamps; framing in Signal reflects week, not day |
| T12 | Ambiguous topic                | `/topic-pulse Apple`                                          | Asks one clarifying question, does not collect, does not write to seen |
| T13 | Transcript fallback            | force a video without captions (use a known no-caption ID)    | Cluster ends with `(transcript unavailable)`; summary derives from title/description |
| T14 | Empty result                   | `/topic-pulse "<deliberately obscure phrase>"`                | Brief renders with "no new items in window"; no error; seen index untouched |
| T15 | Persistence file shape         | `cat ~/.claude/topic-pulse/seen/ai-agents.json` after T1      | Valid JSON; each entry has `id, url, title, source, first_seen_at` |
| T16 | Slug edge cases                | `/topic-pulse "C++"` then inspect filename                    | Slug file exists at non-empty path (no empty filename); no shell errors |

## How to run a test

1. Note current seen-index state: `python3 lib/seen.py load <slug>`
2. Invoke the command in Claude Code
3. Check pass criteria
4. Record outcome (✓/✗ + notes) in `eval-results.md` (gitignored)

## Pre-flight check

Before any test run:

```bash
python3 topic-pulse/lib/slug.py "test"
python3 topic-pulse/lib/seen.py path "test"
python3 topic-pulse/lib/yt_transcript.py dQw4w9WgXcQ | head -c 200
```

All three should succeed (yt_transcript may take a few seconds on first run while installing the dep).
