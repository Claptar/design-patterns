---
layout: default
title: Solution 4 - Cached Time-Series Adapter
---

# Solution 4: Cached Time-Series Adapter

## What changed

Exercise 3 generated windows every time the adapter was created.

Exercise 4 remembers generated windows:

```text
same series
same version
same window size
same horizon
    -> reuse existing windows
```

This matters because the adapter creates many derived objects from one source object.

---

## Key solution

```python
self._key = (series.sensor_id, series.version, window_size, horizon)

if self._key not in type(self)._cache:
    type(self).generation_count += 1
    type(self)._cache[self._key] = self._generate_windows(
        series=series,
        window_size=window_size,
        horizon=horizon,
    )
```

Then iteration reads from the cache:

```python
def __iter__(self):
    return iter(type(self)._cache[self._key])
```

---

## Why the cache key matters

The cache key is not a small implementation detail. It defines when two adaptations are considered the same.

This key is good for this exercise:

```python
(series.sensor_id, series.version, window_size, horizon)
```

It includes:

| Key part | Why it matters |
|---|---|
| `sensor_id` | Different sensors have different data. |
| `version` | Same sensor may receive updated data. |
| `window_size` | Different feature lengths produce different windows. |
| `horizon` | Different prediction distances produce different targets. |

---

## Pitfall: incomplete cache key

This key is dangerous:

```python
series.sensor_id
```

It ignores `version`, `window_size`, and `horizon`.

That means these two adapters might incorrectly share cached data:

```python
CachedSeriesToWindowAdapter(series, window_size=3)
CachedSeriesToWindowAdapter(series, window_size=24)
```

A wrong cache is worse than no cache because it can silently return stale or incorrect results.

---

## Pitfall: mutable cached data

The solution stores windows as a tuple:

```python
return tuple(windows)
```

This reduces the chance that one caller mutates the cached result and affects another caller.

The `TrainingWindow` dataclass is also frozen, so individual windows are immutable.

---

## Possible improvements

For a production system, you might add:

- a maximum cache size,
- an LRU eviction policy,
- a time-to-live,
- explicit invalidation by sensor id,
- thread-safety if adapters are used from multiple threads,
- metrics for cache hits and misses.

But do not add those too early.

The first requirement is correctness: the cache key must represent the full adaptation input.

---

## Final rule

Use adapter caching when all of these are true:

```text
adaptation is repeated
adaptation is expensive enough to matter
adaptation is deterministic
cache keys are reliable
cached results are safe to share
```
