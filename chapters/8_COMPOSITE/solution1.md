---
layout: default
title: "Composite Exercise 1: Solution"
---

# Exercise 1: Solution

## Full solution

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
        super().__init__(name)
        self._reading = reading
        self._unit = unit

    def value(self) -> float:
        return self._reading

    def display(self, indent: int = 0) -> None:
        unit_str = f" {self._unit}" if self._unit else ""
        print(" " * indent + f"{self.name}: {self._reading}{unit_str}")


class MetricGroup(Metric):
    def __init__(self, name: str):
        super().__init__(name)
        self._children: list[Metric] = []

    def add(self, metric: Metric) -> "MetricGroup":
        self._children.append(metric)
        return self

    def value(self) -> float:
        if not self._children:
            raise ValueError(f"MetricGroup '{self.name}' has no children")
        return sum(child.value() for child in self._children) / len(self._children)

    def display(self, indent: int = 0) -> None:
        print(" " * indent + f"{self.name}/")
        for child in self._children:
            child.display(indent + 2)
```

---

## Discussion

### The two implementations of `value()` are fundamentally different

`MetricValue.value()` is trivial — it just returns a stored number.

`MetricGroup.value()` is recursive — it calls `child.value()` on every child,
which may itself trigger further recursion.

The important point is that `MetricGroup.value()` does not ask:

```python
if isinstance(child, MetricValue):
    total += child._reading
elif isinstance(child, MetricGroup):
    total += child.value()
```

It just calls:

```python
sum(child.value() for child in self._children)
```

The recursion is implicit in the fact that `MetricGroup.value()` calls the
same interface method that the caller used in the first place. This is the
Composite pattern working as intended.

### The `display` method follows the same logic

`MetricValue.display()` prints one line.

`MetricGroup.display()` prints the group header and then delegates to each
child's `display()` method, passing `indent + 2`. A deeply nested tree
self-describes correctly without any special-casing.

### Why the trailing `/` on group names matters

It lets the reader distinguish a group from a leaf at a glance:

```
system/          <- group
  cpu/           <- group
    cpu_usage: 73.2 %    <- leaf
```

This is a convention borrowed from file system displays.

### The `add()` method returns `self`

Returning `self` enables chaining:

```python
system = (
    MetricGroup("system")
    .add(MetricGroup("cpu").add(MetricValue("cpu_usage", 73.2, "%")))
    .add(MetricValue("requests_per_sec", 412.0, "req/s"))
)
```

This is a common Python fluent-API convention when building tree structures.

### Possible improvements

**Weighted average instead of simple mean.** The current implementation weighs
each direct child equally, so a group with many children counts the same as
one with few. Depending on the domain, a flat aggregation over all leaf values
might make more sense:

```python
def _all_leaf_values(self) -> list[float]:
    result = []
    for child in self._children:
        if isinstance(child, MetricGroup):
            result.extend(child._all_leaf_values())
        else:
            result.append(child.value())
    return result
```

Notice this version does use `isinstance` — but only inside the group's own
implementation, not in external calling code. That is acceptable.

**`__len__` and `__iter__`.** Adding these to `MetricGroup` lets callers treat
groups like sequences, which can be useful for testing or reporting.

---

[Exercise 1](exercise1.md) · [Exercise 2](exercise2.md)
