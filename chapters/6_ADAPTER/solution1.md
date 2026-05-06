---
layout: default
title: Solution 1 - Basic Object Adapter
---

# Solution 1: Basic Object Adapter

## What changed

The legacy object already had the data we needed:

```python
legacy.device_id()
legacy.recorded_at()
legacy.temp_f()
```

But the client code expected a different interface:

```python
reading.sensor_id
reading.timestamp
reading.celsius
```

The adapter bridges that mismatch.

---

## Key solution

```python
class LegacyReadingAdapter:
    def __init__(self, legacy_reading: LegacyReading):
        self._legacy_reading = legacy_reading

    @property
    def sensor_id(self) -> str:
        return self._legacy_reading.device_id()

    @property
    def timestamp(self) -> int:
        return self._legacy_reading.recorded_at()

    @property
    def celsius(self) -> float:
        fahrenheit = self._legacy_reading.temp_f()
        return round((fahrenheit - 32) * 5 / 9, 2)
```

The adapter does three kinds of translation:

| Target property | Legacy source | Translation |
|---|---|---|
| `sensor_id` | `device_id()` | Rename interface |
| `timestamp` | `recorded_at()` | Rename interface |
| `celsius` | `temp_f()` | Convert Fahrenheit to Celsius |

---

## Why this is Adapter

The alerting function did not change:

```python
alert_if_hot(adapted)
```

That is the point of Adapter.

The client code keeps speaking its own language. The adapter translates the legacy object into that language.

---

## Pitfall

A weak solution would be to modify `alert_if_hot()` like this:

```python
def alert_if_hot(reading):
    if isinstance(reading, LegacyReading):
        return (reading.temp_f() - 32) * 5 / 9 >= 30
    return reading.celsius >= 30
```

That puts legacy knowledge into the client.

The adapter keeps that knowledge at the boundary.

---

## Possible improvement

In a larger codebase, you might define a protocol for the target interface:

```python
class SupportsTemperatureReading(Protocol):
    sensor_id: str
    timestamp: int
    celsius: float
```

Then both real readings and adapted legacy readings can be used by the same client code.
