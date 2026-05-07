---
layout: default
title: "Composite Exercise 2: Export and Thresholds"
---

# Exercise 2: Export and Thresholds

## Goal

Add a second operation to the tree and introduce per-node metadata.
Notice how Composite makes adding new tree-wide operations mechanical:
you implement the operation once on `Metric`, once on `MetricValue`, once on
`MetricGroup` — and the whole tree gains the ability.

---

## Starting point

Start from your solution to Exercise 1, or copy `exercise_solution1.py` and
rename it `exercise2.py`.

---

## What to add

### 1. `threshold` on `MetricValue`

`MetricValue` gains an optional `threshold: float | None = None` constructor
parameter.

When a threshold is set, the metric is considered **breaching** if its value
exceeds the threshold.

### 2. `is_breaching() -> bool` on `Metric`

| Class | Behaviour |
|---|---|
| `MetricValue` | Returns `True` if `threshold` is set and `value() > threshold`. |
| `MetricGroup` | Returns `True` if **any** child `is_breaching()`. |

### 3. `to_dict() -> dict` on `Metric`

Serialises the entire subtree to a nested dictionary suitable for JSON export.

Expected shapes:

**Leaf:**

```python
{
    "name": "cpu_usage",
    "value": 73.2,
    "unit": "%",
    "threshold": 80.0,
    "breaching": False,
}
```

**Group:**

```python
{
    "name": "system",
    "value": 60.0,
    "breaching": True,
    "children": [
        { ... },   # each child's to_dict()
        { ... },
    ]
}
```

### 4. Updated `display`

When `is_breaching()` is `True`, prefix the line with `[!]`:

```
system/
  cpu/
    [!] cpu_usage: 92.0 %  (threshold: 80.0)
        cpu_iowait: 4.1 %
  memory/
    mem_used: 61.0 %
```

---

## Skeleton additions

Add these to your existing classes:

```python
class MetricValue(Metric):
    def __init__(self, name: str, reading: float, unit: str = "",
                 threshold: float | None = None):
        # store threshold in addition to existing fields
        ...

    def is_breaching(self) -> bool:
        # TODO
        ...

    def to_dict(self) -> dict:
        # TODO
        ...

    def display(self, indent: int = 0) -> None:
        # TODO: show [!] prefix and threshold when breaching
        ...


class MetricGroup(Metric):
    def is_breaching(self) -> bool:
        # TODO
        ...

    def to_dict(self) -> dict:
        # TODO
        ...
```

Also add `is_breaching` as an abstract method on `Metric`.

---

## Tests

```python
def test_breaching_leaf():
    m = MetricValue("cpu_usage", 92.0, "%", threshold=80.0)
    assert m.is_breaching() is True
    print("PASS test_breaching_leaf")


def test_not_breaching_leaf():
    m = MetricValue("cpu_usage", 73.2, "%", threshold=80.0)
    assert m.is_breaching() is False
    print("PASS test_not_breaching_leaf")


def test_no_threshold_never_breaching():
    m = MetricValue("cpu_usage", 99.9, "%")
    assert m.is_breaching() is False
    print("PASS test_no_threshold_never_breaching")


def test_group_breaching_if_any_child_breaches():
    g = MetricGroup("cpu")
    g.add(MetricValue("cpu_usage", 92.0, "%", threshold=80.0))
    g.add(MetricValue("cpu_iowait", 4.1, "%"))
    assert g.is_breaching() is True
    print("PASS test_group_breaching_if_any_child_breaches")


def test_group_not_breaching_when_all_fine():
    g = MetricGroup("cpu")
    g.add(MetricValue("cpu_usage", 50.0, "%", threshold=80.0))
    g.add(MetricValue("cpu_iowait", 4.1, "%"))
    assert g.is_breaching() is False
    print("PASS test_group_not_breaching_when_all_fine")


def test_to_dict_leaf():
    m = MetricValue("cpu_usage", 73.2, "%", threshold=80.0)
    d = m.to_dict()
    assert d["name"] == "cpu_usage"
    assert d["value"] == 73.2
    assert d["unit"] == "%"
    assert d["threshold"] == 80.0
    assert d["breaching"] is False
    print("PASS test_to_dict_leaf")


def test_to_dict_group():
    g = MetricGroup("cpu")
    g.add(MetricValue("cpu_usage", 92.0, "%", threshold=80.0))
    d = g.to_dict()
    assert d["name"] == "cpu"
    assert "children" in d
    assert len(d["children"]) == 1
    assert d["breaching"] is True
    print("PASS test_to_dict_group")


def test_to_dict_nested():
    system = MetricGroup("system")
    cpu = MetricGroup("cpu")
    cpu.add(MetricValue("cpu_usage", 92.0, "%", threshold=80.0))
    system.add(cpu)
    d = system.to_dict()
    assert d["children"][0]["name"] == "cpu"
    assert d["children"][0]["children"][0]["name"] == "cpu_usage"
    print("PASS test_to_dict_nested")


def test_display_shows_breach():
    system = MetricGroup("system")
    cpu = MetricGroup("cpu")
    cpu.add(MetricValue("cpu_usage", 92.0, "%", threshold=80.0))
    cpu.add(MetricValue("cpu_iowait", 4.1, "%"))
    system.add(cpu)
    print("--- display output ---")
    system.display()
    print("--- end ---")
    print("PASS test_display_shows_breach")


if __name__ == "__main__":
    test_breaching_leaf()
    test_not_breaching_leaf()
    test_no_threshold_never_breaching()
    test_group_breaching_if_any_child_breaches()
    test_group_not_breaching_when_all_fine()
    test_to_dict_leaf()
    test_to_dict_group()
    test_to_dict_nested()
    test_display_shows_breach()
```

---

## Key question to reflect on

When you implement `is_breaching()` and `to_dict()` on `MetricGroup`, notice
that you call `child.is_breaching()` and `child.to_dict()` without any
`isinstance` check.

Now imagine you later add a third node type — say, `MetricAlias` that points
to another metric. What do you need to change in `MetricGroup`?

Nothing. You only need to implement the interface on `MetricAlias`.

That is the Open/Closed Principle payoff from Composite.

---

[Exercise 1](exercise1.md) · [Solution 2](solution2.md) · [Exercise 3](exercise3.md)
