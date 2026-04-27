# topic-pulse

Daily briefing on a topic you care about. Collects from web, YouTube, Reddit, Hacker News, and
news outlets; dedupes against prior runs; produces an opinionated brief in ~500 words or less.

## Usage

```text
/topic-pulse <topic>
/topic-pulse "AI agents"
/topic-pulse "Federal Reserve" --window 7d
/topic-pulse "AI agents" --sources youtube
/topic-pulse "AI agents" --sources youtube,reddit
/topic-pulse "AI agents" --reset            # clear this topic's seen-index
/topic-pulse "AI agents" --include-seen     # bypass dedupe for one run
/topic-pulse --list-sources
/topic-pulse --add-source hackernews
/topic-pulse --remove-source reddit
```

## Default sources

`web`, `news`, `hackernews`, `reddit`, `youtube` — all enabled out of the box. Toggle with
`--add-source` / `--remove-source`. The skill refuses to disable the last enabled source.

## Persistence

Per-topic seen-index lives at `~/.claude/topic-pulse/seen/<slug>.json`. Re-running a topic
skips items already present in the persisted seen index (regardless of calendar day) and
reports `Skipped: N` in the header. Entries older than 90 days are pruned automatically.

## Sample output

```markdown
# Today · AI agents · 2026-04-27
Sources: web, news, hackernews, reddit, youtube · Window: 24h · New: 7 · Skipped: 3

**TL;DR**
- Anthropic ships agent SDK v2 with native tool-search; OpenAI counters with Operator GA
- Frontier labs converge on "skill" abstractions — naming may differ but the shape is identical
- Reddit's r/LocalLLaMA is openly skeptical that any of this works outside demos

## Stories
### Anthropic Agent SDK v2 lands
Adds tool-search and managed memory primitives. ...

## Signal
The interesting move isn't the SDK release — it's the convergence on "skills" as the unit of
agent capability. Watch which lab ships a marketplace first; that's the platform fight.

## Sources
- web: ...
- youtube: ...
```

See `tests/scenarios.md` and `tests/rubric.md` for how this is evaluated.
