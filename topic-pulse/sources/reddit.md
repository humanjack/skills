# Adapter: reddit

Topic-relevant subreddits. Reddit's public JSON endpoint works without auth (rate-limited but
fine for a once-a-day brief).

## Tools

- `Bash` with `curl` (preferred — clean JSON)
- `WebFetch` as fallback

## Procedure

1. Pick 2–4 subreddits relevant to the topic. Defaults:
   - tech / AI: `r/MachineLearning`, `r/LocalLLaMA`, `r/singularity`, `r/programming`
   - finance: `r/investing`, `r/economics`, `r/stocks`
   - politics: `r/politics`, `r/neutralpolitics`
   - science: `r/science`
   - generic: `r/all` site-wide search
   If none clearly fit, fall back to a sitewide search at `https://www.reddit.com/search.json`.

2. For each subreddit, fetch:
   ```
   https://www.reddit.com/r/<sub>/search.json?q=<urlencoded topic>&restrict_sr=1&sort=top&t=<day|week>
   ```
   (`t=day` for 24h window, `t=week` for 7d.) Pass a non-empty `User-Agent` header
   (`-A "topic-pulse/0.1"`) — Reddit blocks empty UAs.

3. Parse `data.children`. For each post, emit:

```json
{
  "id": "reddit-<id>",
  "url": "https://reddit.com<permalink>",
  "title": "<title>",
  "source": "reddit",
  "published_at": "<ISO 8601 from created_utc>",
  "snippet": "<first ~400 chars of selftext, or empty if link post>",
  "author": "<author>",
  "extra": {
    "subreddit": "<subreddit>",
    "score": <score>,
    "num_comments": <num_comments>,
    "external_url": "<url if link post>"
  }
}
```

4. Sort by score desc, take top 6 across all subreddits combined. Drop posts with `score < 20`
   on a 24h window or `< 50` on 7d — Reddit at low scores is mostly noise.

## Limits

- Cap at 6.
- If a post links externally to a YouTube video or news article, keep the Reddit item but the
  cluster step may merge it with the corresponding YouTube/news cluster.
