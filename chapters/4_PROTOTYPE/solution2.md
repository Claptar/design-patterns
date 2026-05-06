---
layout: default
title: Solution 2 - Deep Copying Nested State
---

# Solution 2: Deep Copying Nested State

## Completed idea

Replace `copy.copy()` with `copy.deepcopy()`.

This makes the clone's nested objects — the `widgets` list, each `Widget`, and the `filters` dictionary — fully independent from the original.

---

## Solution

```python
def clone(self, **changes) -> "Dashboard":
    cloned = deepcopy(self)

    for field_name, value in changes.items():
        setattr(cloned, field_name, value)

    return cloned
```

---

## Why shallow copy breaks here

With `copy.copy()`, the clone and the original share the same `filters` dictionary and the same `Widget` objects in memory.

Mutating one affects the other:

```python
cloned.filters["region"] = "UK"
print(template.filters["region"])  # "UK" — unexpected
```

With `deepcopy()`, the entire object graph is copied recursively.

`cloned.filters` becomes a new dictionary, and `cloned.widgets[0]` becomes a new `Widget` object.

Changing either no longer affects the original.

---

## Key distinction

```text
copy.copy()    -> new outer object, shared nested objects
copy.deepcopy() -> new outer object, new nested objects (recursively)
```

For Prototype, the question to ask is:

> Should the clone share nested objects with the original, or own independent copies?

If independence is required — as it almost always is for mutable nested state — use `deepcopy()`.

---

[Back to exercise](exercise2.md) · [Solution script](exercise_solution2.py)
