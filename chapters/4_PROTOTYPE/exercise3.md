---
layout: default
title: Exercise 3 - Custom Clone Rules
---

# Exercise 3: Custom Clone Rules

## Goal

Practice a more realistic Prototype implementation.

In real code, `deepcopy()` is not always the whole answer.

Sometimes a clone should:

- copy some fields,
- share some fields,
- reset some fields.

---

## Story

The dashboard now has a `DataSource` and a `cache`.

```text
DataSource -> shared configuration for where data comes from
cache      -> temporary computed results
```

When cloning a dashboard:

- `widgets` should be independent,
- `filters` should be independent,
- `data_source` should be shared,
- `cache` should start empty.

Why?

The data source is shared configuration. The clone should point to the same source.

The cache is temporary runtime data. The clone should not inherit old cached results.

---

## Your task

Open `exercise3.py` and implement:

```python
def clone(self, **changes) -> "Dashboard":
    ...
```

The method should create a new `Dashboard` manually or carefully copy the fields.

The clone must satisfy these rules:

1. new `Dashboard` object,
2. independent `widgets`,
3. independent `filters`,
4. same shared `data_source`,
5. empty `cache`,
6. keyword changes are applied,
7. unknown fields raise `AttributeError`.

---

## Tests to satisfy

Run:

```bash
python exercise3.py
```

The tests check all clone rules above.

---

## Hint

Do not blindly use `deepcopy(self)` as the whole implementation.

A good implementation can use `deepcopy()` only for selected fields:

```python
widgets=deepcopy(self.widgets)
filters=deepcopy(self.filters)
```

Then intentionally reuse:

```python
data_source=self.data_source
```

And intentionally reset:

```python
cache={}
```
