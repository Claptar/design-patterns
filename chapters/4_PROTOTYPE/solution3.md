---
layout: default
title: Solution 3 - Custom Clone Rules
---

# Solution 3: Custom Clone Rules

## Completed idea

`deepcopy(self)` clones everything uniformly. But sometimes clone rules are not uniform.

The solution is to build the clone manually, applying different copy strategies per field.

---

## Solution

```python
def clone(self, **changes) -> "Dashboard":
    cloned = Dashboard(
        title=self.title,
        owner=self.owner,
        layout=self.layout,
        data_source=self.data_source,
        widgets=deepcopy(self.widgets),
        filters=deepcopy(self.filters),
        refresh_minutes=self.refresh_minutes,
        cache={},
    )

    for field_name, value in changes.items():
        if not hasattr(cloned, field_name):
            raise AttributeError(f"Dashboard has no field: {field_name}")
        setattr(cloned, field_name, value)

    return cloned
```

---

## The three clone strategies

```text
Independent copy   -> widgets, filters
    deepcopy(self.widgets), deepcopy(self.filters)
    Each clone owns its own widgets and filter state.

Shared reference   -> data_source
    data_source=self.data_source
    All clones point to the same DataSource.
    This is intentional: the source is shared configuration.

Reset              -> cache
    cache={}
    Each clone starts with an empty cache.
    Inheriting old cached results would be wrong.
```

---

## Why not `deepcopy(self)` here

`deepcopy(self)` would also deep-copy `data_source`.

That would give each clone its own separate `DataSource`, breaking the sharing invariant.

It would also copy the original's `cache` contents into the clone, which should start fresh.

When different fields have different copy semantics, a manual clone is the right tool.

---

[Back to exercise](exercise3.md) · [Solution script](exercise_solution3.py)
