# topic-pulse — quality rubric

Run the rubric against this fixed sample of 5 topics, all in the default 24h window:

- `AI agents`
- `Federal Reserve`
- `climate tech`
- `NBA playoffs`
- `semiconductor industry`

For each topic, score 1–5 on the dimensions below. Notes column should explain any score < 4.

| Dimension          | What "5" looks like                                                            | What "1" looks like                                  |
|--------------------|--------------------------------------------------------------------------------|------------------------------------------------------|
| Novelty            | Surfaces an angle a casual reader of the topic wouldn't already know           | Restates obvious headlines anyone with Google has    |
| Dedupe accuracy    | Each cluster is a genuinely distinct event/story                               | The same event appears as 2+ clusters                |
| Source diversity   | ≥ 5 unique domains across the brief                                            | All from one outlet                                  |
| Signal quality     | Makes a falsifiable claim and names a specific "watch next"                    | Vague hedging, restates TL;DR                        |
| Conciseness        | ≤ 500 words, every sentence earns its place                                    | Padding, repetition, > 700 words                     |
| Latency (s)        | ≤ 60s wall clock                                                               | > 180s                                               |

## Aggregate pass bar (v1 ship)

- Mean rubric score ≥ **3.5 / 5** across the 5 topics, averaged across the 5 quality dimensions
  (latency tracked separately).
- **100%** of runs hit source-diversity ≥ 3 unique domains.
- **100%** of re-runs (T2 in scenarios.md) correctly skip prior items.
- Latency p50 ≤ **90s**, p95 ≤ **180s**.

## Eval log template

Copy into `eval-results.md` (gitignored — it's a running log, not a spec):

```
## <YYYY-MM-DD> · v0.1

| topic               | novelty | dedupe | div | signal | concise | latency_s | notes |
|---------------------|--------:|-------:|----:|-------:|--------:|----------:|-------|
| AI agents           |       4 |      5 |   5 |      4 |       5 |        58 |       |
| Federal Reserve     |       3 |      4 |   5 |      3 |       5 |        72 | Signal hedged |
| climate tech        |       … |      … |   … |      … |       … |         … |       |
| NBA playoffs        |       … |      … |   … |      … |       … |         … |       |
| semiconductor industry |    … |      … |   … |      … |       … |         … |       |

mean (excl latency): 4.0   →  PASS / FAIL
p50 latency:        65s    →  PASS
p95 latency:       175s    →  PASS
```

## When the rubric fails

- **Novelty consistently low** → the Signal-section prompt in `SKILL.md` is too generic. Make it
  demand a falsifiable claim and a specific "watch next" entity.
- **Dedupe failing** → tighten clustering rule: same event = same cluster even across sources.
  Possibly add a pre-cluster step that hashes (entity, action, date) tuples.
- **Source diversity low** → check whether one adapter is dominating; cap per-source items more aggressively.
- **Latency high** → likely YouTube transcript fetches. Consider parallelizing or capping youtube to 3 videos.
