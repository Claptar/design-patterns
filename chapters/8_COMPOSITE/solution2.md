---
layout: default
title: "Composite Exercise 2: Solution"
---

# Exercise 2: Solution

## Full solution

```python
class MetricValue(Metric):
    def __init__(self, name: str, reading: float, unit: str = "",
                 threshold: float | None = None):
        super().__init__(name)
        self._reading = reading
        self._unit = unit
        self._threshold = threshold

    def value(self) -> float:
        return self._reading

    def is_breaching(self) -> bool:
        return self._threshold is not None and self._reading > self._threshold

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "value": self._reading,
            "unit": self._unit,
            "threshold": self._threshold,
            "breaching": self.is_breaching(),
        }

    def display(self, indent: int = 0) -> None:
        prefix = "[!] " if self.is_breaching() else ""
        unit_str = f" {self._unit}" if self._unit else ""
        threshold_str = (
            f"  (threshold: {self._threshold})" if self.is_breaching() else ""
        )
        print(" " * indent + f"{prefix}{self.name}: {self._reading}{unit_str}{threshold_str}")


class MetricGroup(Metric):
    def is_breaching(self) -> bool:
        return any(child.is_breaching() for child in self._children)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "value": self.value(),
            "breaching": self.is_breaching(),
            "children": [child.to_dict() for child in self._children],
        }

    def display(self, indent: int = 0) -> None:
        prefix = "[!] " if self.is_breaching() else ""
        print(" " * indent + f"{prefix}{self.name}/")
        for child in self._children:
            child.display(indent + 2)
```

---

## Discussion

### Adding a new operation is mechanical

Compare the effort for `is_breaching()` versus what it would have taken without
Composite:

**Without Composite**, the calling code would need something like:

```python
def any_breaching(items):
    for item in items:
        if isinstance(item, MetricValue):
            if item.is_breaching():
                return True
        elif isinstance(item, MetricGroup):
            if any_breaching(item._children):
                return True
    return False
```

**With Composite**, `MetricGroup.is_breaching()` is one line:

```python
return any(child.is_breaching() for child in self._children)
```

The recursion is completely hidden inside the tree. The calling code does not
know the tree exists — it just calls `.is_breaching()` on whatever it holds.

### `to_dict()` demonstrates the Open/Closed payoff

Adding `to_dict()` to the tree required no changes to any existing traversal
code. Each class implements its own serialisation. Calling code that builds a
JSON export does not need updating.

If a new node type is added later — say, `MetricAlias` that forwards to another
metric — only `MetricAlias` needs `to_dict()`. Everything else continues
working unchanged.

### `is_breaching()` bubbles upward automatically

A group is breaching if any descendant is breaching. This propagates naturally:

```
system/          is_breaching() -> True
  cpu/           is_breaching() -> True
    [!] cpu_usage: 92.0 %   is_breaching() -> True
        cpu_iowait: 4.1 %   is_breaching() -> False
  memory/        is_breaching() -> False
    mem_used: 61.0 %         is_breaching() -> False
```

No external code needs to walk the tree. The tree reports its own health.

### Possible improvement: lazy evaluation

`is_breaching()` currently evaluates every child even after finding one that
breaches. Using `any()` already short-circuits in Python (it stops at the first
`True`), so the current solution is fine. But if `value()` were expensive,
caching the result would be worth considering.

### Pitfall: calling `value()` inside `to_dict()` on an empty group

`MetricGroup.to_dict()` calls `self.value()`, which raises `ValueError` for
an empty group. One option is to catch that and include `None` in the dict.
Another is to make `value()` return `0.0` for empty groups. Which is right
depends on the domain — the current approach (raising) makes the problem
visible rather than hiding it.

---

[Exercise 2](exercise2.md) · [Exercise 3](exercise3.md)
