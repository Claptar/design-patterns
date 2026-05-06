---
layout: default
title: Solution 2 - One-to-Many Adapter
---

# Solution 2: One-to-Many Adapter

## What changed

Exercise 1 adapted one object into one compatible object.

Exercise 2 adapts one object into many compatible objects.

```text
LegacyBatch
    -> TemperatureReading
    -> TemperatureReading
    -> TemperatureReading
```

The client code only needs an iterable:

```python
for reading in readings:
    ...
```

So the adapter implements `__iter__`.

---

## Key solution

```python
class LegacyBatchToReadingsAdapter:
    def __init__(self, batch: LegacyBatch):
        self._readings = tuple(
            TemperatureReading(
                sensor_id=batch.device_id(),
                timestamp=timestamp,
                celsius=round((fahrenheit - 32) * 5 / 9, 2),
            )
            for timestamp, fahrenheit in batch.raw_rows()
            if fahrenheit is not None
        )

    def __iter__(self):
        return iter(self._readings)

    def __len__(self):
        return len(self._readings)
```

---

## Why store a tuple?

The solution stores normalized readings as a tuple:

```python
self._readings: tuple[TemperatureReading, ...]
```

That gives the adapter a stable internal result. Callers can iterate over it many times without re-reading the legacy batch.

It also prevents accidental mutation of the adapter's internal collection.

---

## Pitfall

A common mistake is to make `__iter__` return a list directly:

```python
def __iter__(self):
    return self._readings
```

That is wrong because `__iter__` should return an iterator.

Use:

```python
return iter(self._readings)
```

---

## Design point

The adapter now owns three kinds of legacy-specific knowledge:

1. where the device id lives,
2. how raw rows are shaped,
3. how to convert Fahrenheit to Celsius.

That keeps the rest of the application clean.
