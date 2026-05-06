---
layout: default
title: Exercise 1 - Basic Dashboard Prototype
---

# Exercise 1: Basic Dashboard Prototype

## Goal

Practice the smallest useful version of the Prototype pattern.

In this first part, a dashboard can clone itself and accept small changes.

You should be able to write:

```python
uk_dashboard = template.clone(
    title="UK Sales Dashboard",
    owner="Alice",
)
```

The cloned dashboard should be a new object. The original dashboard should keep its original top-level values.

---

## Story

Your analytics team has a standard dashboard template.

The template already has:

```text
title
owner
layout
widgets
filters
refresh interval
```

For now, focus only on the basic idea:

```text
Take this existing dashboard.
Make a copy.
Change a few fields on the copy.
Return the copy.
```

---

## Your task

Open `exercise1.py` and implement:

```python
def clone(self, **changes) -> "Dashboard":
    ...
```

The method should:

1. copy the current dashboard,
2. apply keyword changes using `setattr`,
3. return the cloned dashboard.

For this first exercise, the tests only check top-level fields.

---

## Tests to satisfy

The tests check that:

- `clone()` returns a different `Dashboard` object,
- changed top-level fields appear on the clone,
- the original dashboard keeps its original top-level fields.

Run:

```bash
python exercise1.py
```

---

## Hint

You may use `copy.copy()` or `copy.deepcopy()` here.

In the next exercise, you will see why shallow copying is not always enough.
