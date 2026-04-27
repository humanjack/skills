# Adapter: news

Major news outlets. Use when the topic has mainstream coverage (politics, finance, sports,
business). For niche tech topics, this adapter often returns little — that's fine.

## Tools

- `WebSearch` with `site:` filters
- `WebFetch` for headline pages where the snippet is thin

## Procedure

1. Run `WebSearch` with the topic and an OR of `site:` filters across major outlets:
   ```text
   <topic> (site:reuters.com OR site:apnews.com OR site:bbc.com OR site:bloomberg.com
            OR site:wsj.com OR site:nytimes.com OR site:ft.com OR site:axios.com
            OR site:cnbc.com OR site:theguardian.com) after:<YYYY-MM-DD>
   ```
2. Take top 8. Prefer wire services (Reuters, AP, Bloomberg) over commentary when both cover the
   same event — wire usually has the cleanest factual frame.
3. `WebFetch` paywalled-looking pages only if the snippet is empty; respect paywalls (don't fabricate
   body content).
4. Emit:

```json
{
  "id": "<canonical url>",
  "url": "<canonical url>",
  "title": "<headline>",
  "source": "news",
  "published_at": "<ISO 8601 if visible>",
  "snippet": "<lead paragraph, ≤ 500 chars>",
  "extra": { "outlet": "<reuters|apnews|...>" }
}
```

## Limits

- Cap at 6 items per run.
- If two outlets cover the same event, keep both (the cluster step will fold them).
