---
layout: default
title: Solution 1 - Basic Dashboard Prototype
---

# Solution 1: Basic Dashboard Prototype

## Completed idea

A `Dashboard` can clone itself by making a shallow copy and applying keyword overrides.

The copy returns a different object with the same top-level field values, except for the ones explicitly changed.

---

## Solution

```python
def clone(self, **changes) -> "Dashboard":
    cloned = copy(self)

    for field_name, value in changes.items():
        setattr(cloned, field_name, value)

    return cloned
```

---

## Why `copy.copy()` works here

This exercise only checks top-level fields like `title` and `owner`.

`copy.copy()` creates a new `Dashboard` object whose top-level fields point to the same values.

Reassigning `cloned.title = "UK Sales Dashboard"` replaces the string reference on the clone, so the original is unaffected.

That is enough to pass exercise 1.

The next exercise shows where shallow copying breaks down.

---

[Back to exercise](exercise1.md) · [Solution script](exercise_solution1.py)
