---
layout: default
title: Exercise 3 - Time-Series Window Adapter
---

# Exercise 3: Time-Series Window Adapter

## Goal

Build an adapter that creates derived objects.

The source object is a long temperature series:

```python
TemperatureSeries(
    sensor_id="greenhouse-1",
    version=1,
    values=(20.0, 21.0, 22.0, 23.0, 24.0),
)
```

The client code wants training windows:

```python
TrainingWindow(
    sensor_id="greenhouse-1",
    features=(20.0, 21.0, 22.0),
    target=23.0,
)
```

One series should become many windows.

---

## Story

The forecasting team wants to train a model that predicts the next temperature reading.

The raw data is stored as one long series. The model code, however, wants many small examples:

```text
previous readings -> next reading
```

So you will create an adapter that exposes a time series as an iterable of `TrainingWindow` objects.

---

## Your task

Open `exercise3.py` and implement `SeriesToWindowAdapter`.

The adapter should:

1. accept a `TemperatureSeries`,
2. accept `window_size`,
3. accept `horizon` with default value `1`,
4. validate that `window_size > 0`,
5. validate that `horizon > 0`,
6. generate `TrainingWindow` objects,
7. implement `__iter__`,
8. implement `__len__`.

---

## Window rule

For this series:

```python
values = (20.0, 21.0, 22.0, 23.0, 24.0)
```

With `window_size=3` and `horizon=1`, generate:

```text
features=(20.0, 21.0, 22.0), target=23.0
features=(21.0, 22.0, 23.0), target=24.0
```

With `window_size=2` and `horizon=2`, generate:

```text
features=(20.0, 21.0), target=23.0
features=(21.0, 22.0), target=24.0
```

The target index is:

```python
start + window_size + horizon - 1
```

---

## Run the tests

```bash
python exercise3.py
```
