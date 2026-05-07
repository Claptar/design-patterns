---
layout: default
title: "Composite Exercise 3: Search and Flattening"
---

# Exercise 3: Search and Flattening

## Goal

Implement tree-traversal operations — searching by name, filtering by condition,
and flattening the tree to a list — and notice that all of them follow the same
Composite delegation pattern you have already used twice.

This exercise also introduces a deliberate design question: should these
operations live on the `Metric` interface or outside the tree altogether?

---

## Starting point

Start from your solution to Exercise 2, or copy `exercise_solution2.py` and
rename it `exercise3.py`.

---

## What to add

### 1. `find(name: str) -> Metric | None`

Searches the tree for a node whose `.name` matches exactly.
Returns the first match found (depth-first), or `None` if no match.

| Class | Behaviour |
|---|---|
| `MetricValue` | Returns `self` if `self.name == name`, else `None`. |
| `MetricGroup` | Returns `self` if `self.name == name`. Otherwise searches children depth-first and returns the first non-`None` result, or `None`. |

### 2. `all_breaching() -> list[Metric]`

Returns a flat list of every node in the subtree that is currently breaching.
The order should be depth-first.

| Class | Behaviour |
|---|---|
| `MetricValue` | Returns `[self]` if `is_breaching()`, else `[]`. |
| `MetricGroup` | Collects results from all children recursively. Optionally includes `self` in the list (your choice — document whichever you pick). |

### 3. `leaves() -> list[MetricValue]`

Returns all `MetricValue` leaf nodes in the subtree, in depth-first order.
This is the one place in this exercise where `isinstance` is acceptable —
inside the tree's own implementation.

| Class | Behaviour |
|---|---|
| `MetricValue` | Returns `[self]`. |
| `MetricGroup` | Concatenates `child.leaves()` for each child. |

---

## Skeleton additions

Add these as abstract methods on `Metric` and implement them on both classes:

```python
from __future__ import annotations

class Metric(ABC):
    # ... existing methods ...

    @abstractmethod
    def find(self, name: str) -> "Metric | None": ...

    @abstractmethod
    def all_breaching(self) -> "list[Metric]": ...

    @abstractmethod
    def leaves(self) -> "list[MetricValue]": ...
```

---

## Tests

```python
def test_find_leaf_by_name():
    system = _build_tree()
    result = system.find("cpu_usage")
    assert result is not None
    assert result.name == "cpu_usage"
    print("PASS test_find_leaf_by_name")


def test_find_group_by_name():
    system = _build_tree()
    result = system.find("cpu")
    assert result is not None
    assert result.name == "cpu"
    print("PASS test_find_group_by_name")


def test_find_returns_none_for_missing():
    system = _build_tree()
    result = system.find("does_not_exist")
    assert result is None
    print("PASS test_find_returns_none_for_missing")


def test_find_on_leaf_self_match():
    m = MetricValue("cpu_usage", 73.2, "%")
    assert m.find("cpu_usage") is m
    print("PASS test_find_on_leaf_self_match")


def test_find_on_leaf_no_match():
    m = MetricValue("cpu_usage", 73.2, "%")
    assert m.find("other") is None
    print("PASS test_find_on_leaf_no_match")


def test_all_breaching_finds_leaves():
    system = _build_tree()
    breaching = system.all_breaching()
    names = [m.name for m in breaching]
    assert "cpu_usage" in names
    print("PASS test_all_breaching_finds_leaves")


def test_all_breaching_empty_when_none_breach():
    g = MetricGroup("cpu")
    g.add(MetricValue("cpu_usage", 50.0, "%", threshold=80.0))
    result = g.all_breaching()
    leaf_names = [m.name for m in result if isinstance(m, MetricValue)]
    assert "cpu_usage" not in leaf_names
    print("PASS test_all_breaching_empty_when_none_breach")


def test_leaves_returns_all_leaf_nodes():
    system = _build_tree()
    leaf_names = {m.name for m in system.leaves()}
    assert "cpu_usage" in leaf_names
    assert "cpu_iowait" in leaf_names
    assert "mem_used" in leaf_names
    assert "system" not in leaf_names
    assert "cpu" not in leaf_names
    print("PASS test_leaves_returns_all_leaf_nodes")


def test_leaves_on_leaf_returns_self():
    m = MetricValue("cpu_usage", 73.2, "%")
    assert m.leaves() == [m]
    print("PASS test_leaves_on_leaf_returns_self")


def _build_tree() -> MetricGroup:
    cpu = MetricGroup("cpu")
    cpu.add(MetricValue("cpu_usage", 92.0, "%", threshold=80.0))
    cpu.add(MetricValue("cpu_iowait", 4.1, "%"))

    mem = MetricGroup("memory")
    mem.add(MetricValue("mem_used", 61.0, "%", threshold=90.0))

    system = MetricGroup("system")
    system.add(cpu)
    system.add(mem)
    return system


if __name__ == "__main__":
    test_find_leaf_by_name()
    test_find_group_by_name()
    test_find_returns_none_for_missing()
    test_find_on_leaf_self_match()
    test_find_on_leaf_no_match()
    test_all_breaching_finds_leaves()
    test_all_breaching_empty_when_none_breach()
    test_leaves_returns_all_leaf_nodes()
    test_leaves_on_leaf_returns_self()
```

---

## Design question to think about

The three operations in this exercise (`find`, `all_breaching`, `leaves`) live
on the `Metric` interface. That means every node type must implement them.

An alternative is to write them as **standalone functions** that accept a
`Metric` and traverse it:

```python
def find(root: Metric, name: str) -> Metric | None:
    if root.name == name:
        return root
    if isinstance(root, MetricGroup):
        for child in root._children:
            result = find(child, name)
            if result is not None:
                return result
    return None
```

Which design is better? Consider:

- The interface approach keeps all operations on the node itself. The tree is
  self-contained. But the interface grows with every new operation.
- The standalone function approach keeps the interface minimal, but exposes
  internal structure (`_children`) or requires a separate visitor protocol.

There is no single right answer. The Visitor pattern (a future topic) exists
specifically to resolve this tension for large, stable trees.

---

[Exercise 2](exercise2.md) · [Solution 3](solution3.md)
