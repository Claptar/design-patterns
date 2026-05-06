---
layout: default
title: Exercise 1 - Basic Object Adapter
---

# Exercise 1: Basic Object Adapter

## Goal

Practice the core Adapter idea on the smallest useful example.

You are given client code that expects an object with this interface:

```python
reading.sensor_id
reading.timestamp
reading.celsius
```

But the legacy system gives you a `LegacyReading` object with a different interface:

```python
legacy.device_id()
legacy.recorded_at()
legacy.temp_f()
```

Your task is to write an adapter that lets the existing client code use the legacy object without changing the client code.

---

## Story

A greenhouse monitoring service already has alerting logic written against Celsius readings.

Later, the team connects an older gateway. The gateway works, but it reports temperatures in Fahrenheit and uses method names that do not match the new application.

You do not want alerting code to know about Fahrenheit, old method names, or gateway details.

So you will put a small adapter between the old object and the new client code.

---

## Your task

Open `exercise1.py` and implement `LegacyReadingAdapter`.

The adapter should:

1. store the wrapped `LegacyReading`,
2. expose `sensor_id` as a property,
3. expose `timestamp` as a property,
4. expose `celsius` as a property,
5. convert Fahrenheit to Celsius using:

```python
(fahrenheit - 32) * 5 / 9
```

For this exercise, round Celsius to two decimal places.

---

## Expected behavior

This should work:

```python
legacy = LegacyReading(device="greenhouse-1", when=100, fahrenheit=86.0)
adapted = LegacyReadingAdapter(legacy)

assert adapted.sensor_id == "greenhouse-1"
assert adapted.timestamp == 100
assert adapted.celsius == 30.0
assert alert_if_hot(adapted) is True
```

The important detail is this:

```python
alert_if_hot(adapted)
```

The alerting function does not know it received an adapter. It only sees the interface it expects.

---

## Run the tests

```bash
python exercise1.py
```

The file contains basic tests at the bottom.
