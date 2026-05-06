---
layout: default
title: Solution 3 - Time-Series Window Adapter
---

# Solution 3: Time-Series Window Adapter

## What changed

This adapter does not merely rename methods or convert units.

It derives new objects from an existing object:

```text
TemperatureSeries
    -> TrainingWindow
    -> TrainingWindow
    -> TrainingWindow
```

The source object is one long sequence. The target interface is an iterable of model-ready examples.

---

## Key solution

```python
last_start = len(series.values) - window_size - horizon + 1

for start in range(max(0, last_start)):
    features = tuple(series.values[start:start + window_size])
    target_index = start + window_size + horizon - 1
    target = series.values[target_index]
    windows.append(TrainingWindow(series.sensor_id, features, target))
```

The formula:

```python
target_index = start + window_size + horizon - 1
```

means:

```text
skip the feature window
then move horizon steps forward
```

For `horizon=1`, the target is the next value.

For `horizon=2`, the target is two steps after the end of the window.

---

## Why this is Adapter

The client code wants this:

```python
for window in windows:
    model.train(window.features, window.target)
```

The raw object gives this:

```python
series.values
```

The adapter hides the slicing rules.

The model code does not need to know how `TemperatureSeries` is stored or how windows are generated.

---

## Pitfall

The most common bug is an off-by-one error.

For example, this is wrong:

```python
last_start = len(series.values) - window_size
```

It ignores `horizon` and may produce a target index beyond the end of the series.

The safe version is:

```python
last_start = len(series.values) - window_size - horizon + 1
```

---

## Possible improvement

If window generation becomes expensive and the same series is adapted repeatedly, this adapter can be extended with caching.

That is the topic of Exercise 4.
