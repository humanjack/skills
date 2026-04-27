# Adapter: web

General-purpose web search. The catch-all when a story might appear in blogs, vendor posts,
research mailing lists, etc. — anything not covered by the specialized adapters.

## Tools

- `WebSearch` for queries
- `WebFetch` for top hits when the snippet is insufficient

## Procedure

1. Build 1–2 queries with the topic and a recency filter, e.g.:
   - `<topic> after:<YYYY-MM-DD>` (where date = today − 1 for `24h`, today − 7 for `7d`)
   - `<topic> latest` as a fallback
2. Run `WebSearch`. Take the top ~10 results.
3. Drop results whose domain is `youtube.com`, `youtu.be`, `reddit.com`, `news.ycombinator.com` —
   those belong to other adapters and would double-count.
4. For results where the snippet alone is too thin to summarize, `WebFetch` the URL and extract
   1–2 paragraphs of substantive content. Skip paywalled bodies.
5. Emit items:

```json
{
  "id": "<canonical url>",
  "url": "<canonical url>",
  "title": "<page title>",
  "source": "web",
  "published_at": "<best-effort ISO 8601 or null>",
  "snippet": "<≤ 500 chars>"
}
```

## Limits

- Cap at 8 items per run.
- If fewer than 3 results survive de-domain filtering, return what you have — don't pad.
