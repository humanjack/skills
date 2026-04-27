# Adapter: hackernews

Hacker News via the Algolia search API — fast, no key required.

## Tools

- `WebFetch` (or `Bash` curl) against the Algolia HN endpoint

## Procedure

1. Compute the lower-bound unix timestamp:
   - `24h` → `now - 86400`
   - `7d`  → `now - 604800`
2. Hit:
   ```
   https://hn.algolia.com/api/v1/search_by_date?query=<urlencoded topic>&tags=story&numericFilters=created_at_i>=<lower>
   ```
   Use `Bash` with `curl -s` for clean JSON, or `WebFetch` if curl is unavailable.
3. Parse the `hits` array. For each hit, build:

```json
{
  "id": "hn-<objectID>",
  "url": "<hit.url || https://news.ycombinator.com/item?id=<objectID>>",
  "title": "<hit.title>",
  "source": "hackernews",
  "published_at": "<hit.created_at>",
  "snippet": "<first ~300 chars of story_text if present, else empty>",
  "extra": {
    "hn_url": "https://news.ycombinator.com/item?id=<objectID>",
    "points": <hit.points>,
    "num_comments": <hit.num_comments>
  }
}
```

4. Sort by `points` desc and keep the top 8. Discard items with `points < 5` and no comments —
   they're noise.

## Limits

- Cap at 8.
- Skip items whose `url` is a YouTube/Reddit link (those go to other adapters).
