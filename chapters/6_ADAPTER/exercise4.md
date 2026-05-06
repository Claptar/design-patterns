---
layout: default
title: Exercise 4 - Cached Time-Series Adapter
---

# Exercise 4: Cached Time-Series Adapter

## Goal

Add caching to an adapter that generates many derived objects.

Exercise 3 created windows every time the adapter was instantiated.

That is correct, but wasteful when the same series and settings are adapted repeatedly.

---

## Story

The forecasting team now trains for many epochs.

Each epoch needs the same training windows:

```python
for epoch in range(10):
    windows = SeriesToWindowAdapter(series, window_size=24)
    train(windows)
```

If the raw series did not change, generating the same windows again is unnecessary.

So you will create a cached adapter.

---

## Your task

Open `exercise4.py` and implement `CachedSeriesToWindowAdapter`.

The adapter should:

1. validate `window_size` and `horizon`,
2. build a cache key,
3. generate windows only on a cache miss,
4. store generated windows in a class-level cache,
5. implement `__iter__`,
6. implement `__len__`,
7. implement `clear_cache()` for tests.

---

## Cache key

Use this key:

```python
(series.sensor_id, series.version, window_size, horizon)
```

The key should include everything that affects the generated windows.

For this exercise, assume `version` changes whenever the raw series changes.

---

## Expected behavior

```python
CachedSeriesToWindowAdapter.clear_cache()

adapter1 = CachedSeriesToWindowAdapter(series, window_size=3)
adapter2 = CachedSeriesToWindowAdapter(series, window_size=3)

assert CachedSeriesToWindowAdapter.generation_count == 1
assert list(adapter1) == list(adapter2)
```

The second adapter should reuse the cached windows.

---

## Run the tests

```bash
python exercise4.py
```
