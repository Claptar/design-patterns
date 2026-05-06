---
layout: default
title: Exercise 2 - One-to-Many Adapter
---

# Exercise 2: One-to-Many Adapter

## Goal

Extend Adapter from one object to one object into one object to many objects.

In Exercise 1, one `LegacyReading` became one adapted reading.

Now one `LegacyBatch` contains many raw readings. The client code wants to iterate over clean `TemperatureReading` objects.

---

## Story

The old greenhouse gateway sends readings in batches.

A batch contains:

```python
device_id
[(timestamp, fahrenheit), (timestamp, fahrenheit), ...]
```

But the rest of your application wants this:

```python
for reading in readings:
    process(reading.sensor_id, reading.timestamp, reading.celsius)
```

You do not want every caller to know how to unpack tuples, skip missing values, or convert Fahrenheit to Celsius.

So you will build an iterable adapter.

---

## Your task

Open `exercise2.py` and implement `LegacyBatchToReadingsAdapter`.

The adapter should:

1. accept a `LegacyBatch`,
2. create a collection of `TemperatureReading` objects,
3. skip readings where Fahrenheit is `None`,
4. convert Fahrenheit to Celsius,
5. round Celsius to two decimal places,
6. implement `__iter__`,
7. implement `__len__`.

---

## Expected behavior

```python
batch = LegacyBatch(
    device="greenhouse-1",
    rows=[
        (100, 68.0),
        (101, 86.0),
        (102, None),
    ],
)

adapter = LegacyBatchToReadingsAdapter(batch)

assert len(adapter) == 2
assert list(adapter)[0].celsius == 20.0
assert list(adapter)[1].celsius == 30.0
```

The missing reading is skipped.

---

## Run the tests

```bash
python exercise2.py
```
