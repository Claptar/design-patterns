---
layout: default
title: Exercise 2 - Deep Copying Nested State
---

# Exercise 2: Deep Copying Nested State

## Goal

Improve the dashboard prototype so cloned dashboards do not accidentally share nested mutable objects.

This is the most important practical detail in the Prototype pattern.

---

## Story

The first clone worked for top-level fields.

But dashboards contain nested mutable state:

```text
widgets -> list of Widget objects
filters -> dictionary of filter values
```

If two dashboards share the same `filters` dictionary or the same `Widget` objects, changing one dashboard can accidentally change the other.

That is not a safe clone.

---

## Your task

Open `exercise2.py` and implement:

```python
def clone(self, **changes) -> "Dashboard":
    ...
```

This time the clone must be independent from the original, including:

- the `widgets` list,
- each `Widget` inside the list,
- the `filters` dictionary.

---

## Tests to satisfy

The tests check that:

- the clone is a new `Dashboard`,
- changing clone filters does not affect the original,
- changing clone widgets does not affect the original,
- the nested objects are not the same objects in memory.

Run:

```bash
python exercise2.py
```

---

## Hint

Use `copy.deepcopy()`.

The point of this exercise is to feel the difference between:

```python
copy.copy(obj)
```

and:

```python
copy.deepcopy(obj)
```
