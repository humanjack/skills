# Adapter: youtube

YouTube videos relevant to the topic, summarized from transcript when available.

## Tools

- `WebSearch` to find videos (no YouTube Data API key needed)
- `Bash` to call `lib/yt_transcript.py <video_id>` for transcripts
- `WebFetch` against the watch page as a metadata fallback

## Procedure

1. Search for videos:
   ```text
   WebSearch: <topic> site:youtube.com after:<YYYY-MM-DD>
   ```
   Take the top 8 `youtube.com/watch?v=<id>` results. Extract the `v` parameter as `video_id`.

2. For each video, get metadata. Two strategies:
   - **Cheap path:** trust the WebSearch snippet (channel name often appears in the title or
     description preview).
   - **Full path:** `WebFetch` the watch URL to extract `<title>`, channel, view count, upload
     date, and description. Use this when the snippet is too sparse.

3. Fetch the transcript:
   ```bash
   python3 lib/yt_transcript.py <video_id>
   ```
   - Exit 0 + non-empty stdout → use as transcript (`transcript_available: true`).
   - Non-zero exit or empty stdout → mark `transcript_available: false` and fall back to
     description + title for the summary.

4. Emit:

```json
{
  "id": "yt-<video_id>",
  "url": "https://www.youtube.com/watch?v=<video_id>",
  "title": "<video title>",
  "source": "youtube",
  "published_at": "<upload date if known>",
  "snippet": "<first ~600 chars of transcript, or description if no transcript>",
  "author": "<channel name>",
  "extra": {
    "video_id": "<video_id>",
    "duration": "<HH:MM:SS or MM:SS if known>",
    "transcript_available": <true|false>,
    "transcript": "<full transcript text, only if you'll use it for summary>"
  }
}
```

5. Drop videos that are clearly off-topic, < 60s long, or pure clickbait shorts (channel name
   contains "Shorts" or duration < 60s and topic match is weak).

## Summarization rule

When summarizing a YouTube cluster, base the 2–3 sentence summary on the **transcript**, not the
title. If transcript is unavailable, summarize from description + title and append
`(transcript unavailable)` at the end of the cluster summary.

## Limits

- Cap at 6 videos per run.
- Transcript fetches can be slow — run them sequentially and stop after 6 successes.
