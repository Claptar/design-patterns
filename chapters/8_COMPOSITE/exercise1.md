---
layout: default
title: "Composite Exercise 1: Metric Tree"
---

# Exercise 1: Metric Tree

## Goal

Practice the core Composite mechanic: make a leaf and a container implement the
same interface so a caller can treat them identically.

---

## Context

You are building a monitoring dashboard for a web service.

Metrics come in two shapes:

- A **single reading** — one number with a name and a unit, such as
  `cpu_usage = 73.2 %`.
- A **metric group** — a named collection of metrics that may itself contain
  other groups.

The dashboard only needs two operations right now:

| Operation | Description |
|---|---|
| `value() -> float` | Returns the metric's value. For a group, returns the **average** of all children's values. |
| `display(indent: int = 0) -> None` | Prints a human-readable representation of the metric, indented to show hierarchy. |

The key constraint: the dashboard code must call `.value()` and `.display()` in
**exactly the same way** regardless of whether it is holding a single reading or
an entire group.

---

## What you need to build

### `Metric` (abstract base)

```python
from abc import ABC, abstractmethod

class Metric(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def value(self) -> float: ...

    @abstractmethod
    def display(self, indent: int = 0) -> None: ...
```

### `MetricValue` (leaf)

Stores a single float reading and its unit.

- `value()` returns the stored reading.
- `display(indent)` prints something like:

```
    cpu_usage: 73.2 %
```

### `MetricGroup` (composite)

Holds a list of `Metric` children (which may be `MetricValue` or `MetricGroup`).

- `add(metric: Metric) -> MetricGroup` — adds a child and returns `self` so
  calls can be chained.
- `value()` returns the **mean** of all children's `value()` results.
  Raise `ValueError` if the group is empty.
- `display(indent)` prints the group name, then calls `display(indent + 2)` on
  every child:

```
system/
  cpu/
    cpu_usage: 73.2 %
    cpu_iowait: 4.1 %
  memory/
    mem_used: 61.0 %
```

---

## Skeleton

Work in `exercise1.py`.  Do not change the test functions.

```python
from abc import ABC, abstractmethod


class Metric(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def value(self) -> float: ...

    @abstractmethod
    def display(self, indent: int = 0) -> None: ...


class MetricValue(Metric):
    def __init__(self, name: str, reading: float, unit: str = ""):
        # TODO
        ...

    def value(self) -> float:
        # TODO
        ...

    def display(self, indent: int = 0) -> None:
        # TODO
        ...


class MetricGroup(Metric):
    def __init__(self, name: str):
        # TODO
        ...

    def add(self, metric: Metric) -> "MetricGroup":
        # TODO
        ...

    def value(self) -> float:
        # TODO
        ...

    def display(self, indent: int = 0) -> None:
        # TODO
        ...


# ---------------------------------------------------------------------------
# Tests — do not modify
# ---------------------------------------------------------------------------

def test_leaf_value():
    m = MetricValue("cpu_usage", 73.2, "%")
    assert m.value() == 73.2, f"Expected 73.2, got {m.value()}"
    print("PASS test_leaf_value")


def test_group_average():
    g = MetricGroup("cpu")
    g.add(MetricValue("cpu_usage", 80.0, "%"))
    g.add(MetricValue("cpu_iowait", 20.0, "%"))
    assert g.value() == 50.0, f"Expected 50.0, got {g.value()}"
    print("PASS test_group_average")


def test_nested_group_average():
    cpu = MetricGroup("cpu")
    cpu.add(MetricValue("cpu_usage", 60.0, "%"))
    cpu.add(MetricValue("cpu_iowait", 40.0, "%"))   # avg = 50.0

    mem = MetricGroup("memory")
    mem.add(MetricValue("mem_used", 70.0, "%"))     # avg = 70.0

    system = MetricGroup("system")
    system.add(cpu)
    system.add(mem)                                  # avg of (50, 70) = 60.0

    assert system.value() == 60.0, f"Expected 60.0, got {system.value()}"
    print("PASS test_nested_group_average")


def test_empty_group_raises():
    g = MetricGroup("empty")
    try:
        g.value()
        print("FAIL test_empty_group_raises — no exception raised")
    except ValueError:
        print("PASS test_empty_group_raises")


def test_uniform_interface():
    items: list[Metric] = [
        MetricValue("cpu_usage", 73.2, "%"),
        MetricGroup("memory"),
    ]
    # add a child so the group is not empty
    items[1].add(MetricValue("mem_used", 61.0, "%"))

    # calling code must not use isinstance — just call .value()
    for item in items:
        _ = item.value()
    print("PASS test_uniform_interface")


def test_display_runs():
    system = MetricGroup("system")
    cpu = MetricGroup("cpu")
    cpu.add(MetricValue("cpu_usage", 73.2, "%"))
    cpu.add(MetricValue("cpu_iowait", 4.1, "%"))
    system.add(cpu)
    system.add(MetricValue("requests_per_sec", 412.0, "req/s"))
    print("--- display output ---")
    system.display()
    print("--- end ---")
    print("PASS test_display_runs")


if __name__ == "__main__":
    test_leaf_value()
    test_group_average()
    test_nested_group_average()
    test_empty_group_raises()
    test_uniform_interface()
    test_display_runs()
```

---

## Expected display output for `test_display_runs`

```
--- display output ---
system/
  cpu/
    cpu_usage: 73.2 %
    cpu_iowait: 4.1 %
  requests_per_sec: 412.0 req/s
--- end ---
```

---

## Hints

- `MetricGroup.value()` should call `child.value()` on each child — not check
  whether the child is a `MetricValue` or a `MetricGroup`.
- The indentation in `display` is driven purely by the `indent` parameter.
  Each level adds 2 spaces.
- A group name is displayed with a trailing `/` to distinguish it from a leaf.

---

[Solution 1](solution1.md) · [Exercise 2](exercise2.md)
