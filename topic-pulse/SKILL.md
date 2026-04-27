---
name: topic-pulse
description: |
  Daily briefing on a topic the user cares about. Collects from web / YouTube / Reddit / HN / news,
  dedupes against prior runs, summarizes story clusters, and produces an opinionated Signal section.
  Trigger when the user asks "what's going on with <topic> today?", "give me a brief on <topic>",
  or invokes /topic-pulse. Skip for one-off factual questions that don't need a multi-source roundup.
---

# topic-pulse

Produce one short, dated, opinionated brief on a user-chosen topic. Collect from multiple sources,
dedupe across runs (persistent seen-index), cluster, summarize, analyze.

## Invocation

```
/topic-pulse <topic>                          # default: all enabled sources, last 24h
/topic-pulse "<topic>" --window 7d            # weekly rollup
/topic-pulse <topic> --sources youtube        # one source only
/topic-pulse <topic> --sources youtube,reddit # subset
/topic-pulse <topic> --reset                  # clear seen-index for this topic
/topic-pulse <topic> --include-seen           # bypass seen-filter for this run
/topic-pulse --list-sources                   # show enabled sources
/topic-pulse --add-source <name>              # enable a source
/topic-pulse --remove-source <name>           # disable a source
```

## Argument parsing

Parse the user's invocation into:
- `topic` (string, required unless a `--list-sources`/`--add-source`/`--remove-source` command)
- `sources` (list, optional — empty means "all enabled")
- `window` (string, default `24h`; accepts `24h`, `7d`)
- `reset` (bool, default false)
- `include_seen` (bool, default false)
- management command: `list_sources` | `add_source <name>` | `remove_source <name>`

If the topic is **ambiguous** (e.g. "Apple" — company or fruit? "Mercury" — planet, element, or god?),
ask exactly one short clarifying question and stop. Do not collect.

## Paths

- Skill root: the directory containing this `SKILL.md`
- User config dir: `~/.claude/topic-pulse/` (create if missing)
- Sources config: `~/.claude/topic-pulse/sources.json`
  (on first run, copy `<skill-root>/sources.default.json` here)
- Seen index: `~/.claude/topic-pulse/seen/<topic-slug>.json`
- Topic slug: lowercase, non-alphanumeric → `-`, collapsed, trimmed (use `lib/slug.py`)

## Source-management commands (handle first, exit early)

- `--list-sources`: read `sources.json`, print the enabled list and the available adapter names.
- `--add-source <name>`: validate `<name>` is a known adapter (see Adapters below), set `enabled: true` in `sources.json`, save, confirm.
- `--remove-source <name>`: set `enabled: false`, save, confirm. Refuse if it would leave zero enabled sources.

## Pipeline

When invoked with a topic:

1. **Resolve sources.** If `--sources` given, intersect with known adapters. Else use enabled set from config.
2. **Compute slug** for the topic and load the seen index from `seen/<slug>.json` (empty list if missing).
3. **If `--reset`,** clear the seen index file for this topic before continuing.
4. **Collect** from each resolved source in parallel. Each adapter returns a list of items:
   ```
   {id, url, title, source, published_at, snippet, author?, extra?}
   ```
   See `sources/*.md` for adapter-specific instructions.
5. **Filter seen.** Drop items whose `id` is in the seen index, unless `--include-seen` is set.
   Track count of skipped items.
6. **Cluster.** Group remaining items into 3–6 clusters by event/topic similarity. Same story
   from two outlets → one cluster. A YouTube video that covers the same story as a news article
   may be its own cluster if its angle is distinct (commentary, analysis), else fold into the
   news cluster as a secondary source.
7. **Summarize each cluster** in 2–3 sentences. For YouTube clusters with transcripts, base the
   summary on the transcript, not the title. Note "(transcript unavailable)" when falling back.
8. **Analyze across clusters** to produce the `Signal` section: trend shift vs. last run if any,
   who/what moved, contrarian angle, one "watch next" item. Make a real claim, not a restatement.
9. **Render output** in the format below.
10. **Persist:** append every item that appeared in any cluster to the seen index with
    `first_seen_at = now (UTC, ISO 8601)`. Save the file. Prune entries older than 90 days
    while you're there.

If after filtering there are 0 items, still render the brief. The Stories section says
"no new items in window". The Signal section briefly describes the lull (e.g. "quiet day; last
notable activity was N days ago").

## Output format

```
# Today · <topic> · <YYYY-MM-DD>
Sources: <a, b, c> · Window: <24h|7d> · New: <N> · Skipped (already seen): <M>

**TL;DR**
- <punchy bullet>
- <punchy bullet>
- <punchy bullet>

## Stories

### <cluster headline>
<2–3 sentences> · [<domain>](<url>)<, [<domain2>](<url2>) if multiple>

### <youtube cluster headline>
**<video title>** — <channel> · <duration>
<2–3 sentences from transcript> · [watch](<url>)

## Signal
<2–4 sentence analytical take. Trend shift, who's winning/losing, contrarian read,
one "watch next" item. Make a claim.>

## Sources
- web: <url>, <url>
- youtube: <url>, <url>
- reddit: <url>
- hackernews: <url>
- news: <url>
```

Keep total length ≤ 500 words. Trim filler before going over.

## Adapters

The available source adapters are defined in `sources/`:

- `sources/web.md`
- `sources/news.md`
- `sources/hackernews.md`
- `sources/reddit.md`
- `sources/youtube.md`

Read the relevant adapter file before collecting from that source.

## Helpers

- `lib/slug.py` — `python3 lib/slug.py "<topic>"` → slug on stdout
- `lib/seen.py` — `python3 lib/seen.py load|filter|append|prune|reset <slug> [args]`
- `lib/yt_transcript.py` — `python3 lib/yt_transcript.py <video_id_or_url>` → transcript text on stdout, empty + non-zero exit on failure

Use these via the `Bash` tool. They are intentionally tiny and stdlib-only where possible
(`yt_transcript.py` will `pip install --user youtube-transcript-api` on first use if missing).

## Rules

- Default to `--window 24h`. Only widen to `7d` when explicitly requested.
- Always respect `sources.json`. Never collect from a disabled source.
- Never invent URLs. If a source returns nothing, say so — do not fabricate items to fill space.
- The Signal section must take a position. "Many things happened" is not a take.
- Cite sources inline as `[domain](url)`. Never write a claim without a link to back it.
- One clarifying question max for ambiguous topics — then proceed with the user's answer.
- Do not block on optional helpers. If `yt_transcript.py` fails, fall back to title + description and mark the cluster `(transcript unavailable)`.
