---
layout: default
title: "Cached Adapter Design Pattern"
---

# Cached Adapter: Time-Series Windows

## 1. What problem are we trying to solve?

Imagine you are building a small machine-learning system for temperature forecasting.

The training code expects many small training examples:

```python
TrainingWindow(
    features=(18.0, 18.4, 18.9),
    target=19.2,
)
```

But the data source gives you one long object:

```python
TemperatureSeries(
    sensor_id="boiler-7",
    readings=(18.0, 18.4, 18.9, 19.2, 19.5, 19.8),
)
```

The training code wants this:

```text
many TrainingWindow objects
```

The data source gives this:

```text
one TemperatureSeries object
```

So there is an interface mismatch.

The deeper issue is that adapting one series into windows can produce many objects. If the same series is used repeatedly during training, validation, visualization, or multiple epochs, regenerating those windows again and again is wasteful.

So the problem is:

> We need to adapt one source object into many target objects, and we do not want to repeat the same expensive conversion every time.

---

## 2. Concept introduction

This is still the **Adapter pattern**.

The adapter makes one interface look like another:

```text
TemperatureSeries
    one long sequence of readings

SeriesToWindowAdapter
    exposes an iterable of TrainingWindow objects

Training code
    consumes TrainingWindow objects
```

But this adapter has an extra performance concern:

```text
one adaptee object -> many adapted objects
```

So caching becomes useful.

In plain English:

> A cached adapter translates an incompatible object into the shape the client expects, but remembers the translated result so repeated adaptation is cheap.

This is not a separate GoF pattern. It is an Adapter implementation detail that matters when adaptation is expensive or one-to-many.

---

## 3. The target interface

Let’s say the model training code expects to work with `TrainingWindow` objects:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class TrainingWindow:
    sensor_id: str
    features: tuple[float, ...]
    target: float


def train_on_window(window: TrainingWindow):
    print(f"Training on {window.features} -> {window.target}")
```

The training function does not know anything about raw sensor series.

It only knows:

```text
Give me training windows.
```

That is good design. The training logic should not also know how to slice raw time-series data.

---

## 4. The existing source object

Now suppose the data source gives us this:

```python
@dataclass(frozen=True)
class TemperatureSeries:
    sensor_id: str
    version: int
    readings: tuple[float, ...]
```

Example:

```python
series = TemperatureSeries(
    sensor_id="boiler-7",
    version=12,
    readings=(18.0, 18.4, 18.9, 19.2, 19.5, 19.8),
)
```

This is not directly what the training code wants.

The training code wants:

```text
window 1: (18.0, 18.4, 18.9) -> 19.2
window 2: (18.4, 18.9, 19.2) -> 19.5
window 3: (18.9, 19.2, 19.5) -> 19.8
```

So one `TemperatureSeries` becomes several `TrainingWindow` objects.

---

## 5. Adapter without caching

A first version could look like this:

```python
class SeriesToWindowAdapter:
    def __init__(self, series: TemperatureSeries, window_size: int, horizon: int = 1):
        self._windows = []

        last_start = len(series.readings) - window_size - horizon + 1

        for start in range(max(0, last_start)):
            features = tuple(series.readings[start:start + window_size])
            target_index = start + window_size + horizon - 1
            target = series.readings[target_index]

            self._windows.append(
                TrainingWindow(
                    sensor_id=series.sensor_id,
                    features=features,
                    target=target,
                )
            )

    def __iter__(self):
        return iter(self._windows)
```

Usage:

```python
adapter = SeriesToWindowAdapter(series, window_size=3)

for window in adapter:
    train_on_window(window)
```

This works.

But if we do this repeatedly:

```python
for epoch in range(10):
    adapter = SeriesToWindowAdapter(series, window_size=3)

    for window in adapter:
        train_on_window(window)
```

then the same windows are generated 10 times.

The adapter is correct, but wasteful.

---

## 6. Adapter with caching

Now let’s cache the generated windows.

```python
class CachedSeriesToWindowAdapter:
    _cache: dict[tuple[str, int, int, int], tuple[TrainingWindow, ...]] = {}
    generation_count = 0

    def __init__(self, series: TemperatureSeries, window_size: int, horizon: int = 1):
        if window_size <= 0:
            raise ValueError("window_size must be positive")

        if horizon <= 0:
            raise ValueError("horizon must be positive")

        self._key = (
            series.sensor_id,
            series.version,
            window_size,
            horizon,
        )

        if self._key not in self._cache:
            type(self).generation_count += 1
            print(f"Generating windows for {series.sensor_id}, version {series.version}")

            self._cache[self._key] = self._generate_windows(
                series=series,
                window_size=window_size,
                horizon=horizon,
            )

    @staticmethod
    def _generate_windows(
        series: TemperatureSeries,
        window_size: int,
        horizon: int,
    ) -> tuple[TrainingWindow, ...]:
        windows = []
        last_start = len(series.readings) - window_size - horizon + 1

        for start in range(max(0, last_start)):
            features = tuple(series.readings[start:start + window_size])
            target_index = start + window_size + horizon - 1
            target = series.readings[target_index]

            windows.append(
                TrainingWindow(
                    sensor_id=series.sensor_id,
                    features=features,
                    target=target,
                )
            )

        return tuple(windows)

    def __iter__(self):
        return iter(self._cache[self._key])

    def __len__(self):
        return len(self._cache[self._key])
```

Usage:

```python
series = TemperatureSeries(
    sensor_id="boiler-7",
    version=12,
    readings=(18.0, 18.4, 18.9, 19.2, 19.5, 19.8),
)

for epoch in range(3):
    adapter = CachedSeriesToWindowAdapter(series, window_size=3)

    for window in adapter:
        train_on_window(window)
```

Output starts like this:

```text
Generating windows for boiler-7, version 12
Training on (18.0, 18.4, 18.9) -> 19.2
Training on (18.4, 18.9, 19.2) -> 19.5
Training on (18.9, 19.2, 19.5) -> 19.8
...
```

The important part is that generation happens once.

After that, the adapter reuses the cached windows.

---

## 7. Why the cache key matters

The cache key is the most important design detail.

Here we used:

```python
self._key = (
    series.sensor_id,
    series.version,
    window_size,
    horizon,
)
```

That means:

```text
Same sensor
same data version
same window size
same prediction horizon
    -> reuse the cached windows
```

If the readings change, the `version` should change.

That prevents this bug:

```text
old readings get cached
new readings arrive
adapter accidentally returns old windows
```

A bad cache key would be:

```python
self._key = series.sensor_id
```

That ignores the data version and window size.

Then these two requests would incorrectly share the same cache entry:

```python
CachedSeriesToWindowAdapter(series, window_size=3)
CachedSeriesToWindowAdapter(series, window_size=24)
```

Those are not the same adaptation.

A good cache key must include every input that affects the generated result.

---

## 8. Natural example: forecasting from sensor data

This kind of adapter is common in forecasting and time-series modeling.

Raw data often arrives like this:

```text
one sensor
one long sequence
many readings
```

But machine-learning code often wants this:

```text
many small examples
each example has features and target
```

So the adapter does the translation:

```text
TemperatureSeries
    -> TrainingWindow
    -> TrainingWindow
    -> TrainingWindow
    -> ...
```

The adapter is valuable because it protects the model code from knowing how windows are created.

The cache is valuable because window creation may be repeated:

```text
multiple training epochs
multiple models
grid search
cross-validation
visual inspection
debug runs
```

If the raw series and transformation settings are unchanged, the generated windows are unchanged.

That is when caching makes sense.

---

## 9. Connection to earlier concepts and SOLID

### Adapter

The adapter solves an interface mismatch.

```text
Client expects:
    iterable of TrainingWindow objects

Existing object provides:
    TemperatureSeries with raw readings

Adapter provides:
    __iter__ over generated TrainingWindow objects
```

The client does not need to know the raw data format.

### Factory

A factory would answer:

```text
Which adapter should I create?
```

For example:

```python
def create_training_data_adapter(data_source):
    if data_source.kind == "temperature_series":
        return CachedSeriesToWindowAdapter(data_source.series, window_size=24)

    if data_source.kind == "csv_file":
        return CsvToWindowAdapter(data_source.path)

    raise ValueError("Unsupported data source")
```

The factory chooses.

The adapter translates.

### Builder

A builder assembles one complex object step by step.

This adapter does something different.

It takes one existing object and exposes it as many target objects.

```text
Builder:
    many setup steps -> one final object

Cached Adapter:
    one existing object -> many adapted objects
```

### Single Responsibility Principle

The model training code has one job:

```text
train on windows
```

The adapter has one job:

```text
turn a raw series into windows
```

The cache belongs near the adaptation logic because it optimizes that conversion.

### Dependency Inversion Principle

The training code can depend on an abstraction:

```python
for window in training_windows:
    train_on_window(window)
```

It does not depend directly on:

```text
TemperatureSeries
sensor storage
window slicing rules
cache mechanics
```

That makes the training code easier to test and easier to reuse.

---

## 10. Example from a popular Python package

A related idea appears in scikit-learn pipelines. A scikit-learn `Pipeline` chains transformers and estimators, and intermediate pipeline steps are expected to implement `fit` and `transform`. The pipeline also has a `memory` option that can cache fitted transformers, which helps avoid repeated computation when parameters and input data are identical.

That is not called “Cached Adapter” in the docs, but the design pressure is similar:

```text
expensive transformation
same inputs
same parameters
repeated usage
    -> cache the result
```

The scikit-learn docs also note that caching is especially interesting when fitting a transformer is costly.

So in data science code, caching belongs naturally around transformation boundaries.

References:

- [scikit-learn Pipeline documentation](https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html)
- [scikit-learn example: caching nearest neighbors](https://scikit-learn.org/stable/auto_examples/compose/plot_compare_reduction.html)

---

## 11. When to use a cached adapter

Use this style when:

| Situation | Why caching helps |
|---|---|
| One source object expands into many target objects | Rebuilding the same list repeatedly is wasteful. |
| Adaptation is expensive | CPU, memory, parsing, feature extraction, or I/O cost can be avoided. |
| The same source is adapted repeatedly | Training epochs, repeated rendering, repeated reports, repeated API calls. |
| The adaptation is deterministic | Same input should produce the same output. |
| You have a reliable cache key | You can tell when cached data is still valid. |
| Adapted objects are safe to share | Immutable or treated as read-only. |

Good examples:

```text
time series -> sliding windows
image file -> tiles
document -> tokens
audio file -> frames
API response -> domain objects
map route -> coordinate points
large table -> row objects
```

---

## 12. When not to use it

Do not cache just because you can.

Avoid caching when:

| Situation | Why caching may hurt |
|---|---|
| Adaptation is cheap | The cache adds complexity without benefit. |
| Output is huge | Memory usage may become worse than recomputation. |
| Source changes often | Cache invalidation becomes risky. |
| Cache key is unreliable | Stale or incorrect results become likely. |
| Adapted objects are mutable | One caller may accidentally affect another. |
| Adaptation depends on hidden context | Time, permissions, locale, random seed, or environment may change the result. |

A dangerous version would be:

```python
_cache[series.sensor_id] = windows
```

That looks simple, but it ignores:

```text
data version
window size
prediction horizon
normalization settings
feature options
```

A cache that forgets important inputs is worse than no cache.

---

## 13. Practical rule of thumb

Ask:

> Does this adapter convert one object into many objects?

If yes, caching may be useful.

Ask:

> Will the same adaptation happen more than once?

If yes, caching becomes more attractive.

Ask:

> Is the adapted result deterministic and safely reusable?

If yes, caching is likely safe.

Ask:

> Can I build a correct cache key?

If no, do not cache yet.

The most important rule:

> Cache only when you can clearly name what makes two adaptations the same.

For the time-series adapter, this was:

```text
sensor id
data version
window size
horizon
```

---

## 14. Summary and mental model

A normal adapter says:

```text
This object has the right behavior, but the wrong interface.
I will wrap it and expose the interface the client expects.
```

A cached adapter says:

```text
This object has the right data, but the wrong shape.
I will expand it into the target objects once, then reuse that expansion.
```

Mental model:

```text
A raw time series is like a loaf of bread.
The training code wants slices.
The adapter slices the loaf.
The cache remembers the slices so you do not keep slicing the same loaf again.
```

One-sentence summary:

> Use a cached adapter when adapting one object into many derived objects is expensive, repeated, deterministic, and can be safely identified by a correct cache key.
