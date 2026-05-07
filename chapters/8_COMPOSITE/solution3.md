---
layout: default
title: "Composite Exercise 3: Solution"
---

# Exercise 3: Solution

## Full solution additions

```python
# MetricValue

def find(self, name: str) -> "Metric | None":
    return self if self.name == name else None

def all_breaching(self) -> "list[Metric]":
    return [self] if self.is_breaching() else []

def leaves(self) -> "list[MetricValue]":
    return [self]


# MetricGroup

def find(self, name: str) -> "Metric | None":
    if self.name == name:
        return self
    for child in self._children:
        result = child.find(name)
        if result is not None:
            return result
    return None

def all_breaching(self) -> "list[Metric]":
    result = []
    for child in self._children:
        result.extend(child.all_breaching())
    return result

def leaves(self) -> "list[MetricValue]":
    result = []
    for child in self._children:
        result.extend(child.leaves())
    return result
```

---

## Discussion

### All three operations follow the same structural pattern

Look at the three `MetricGroup` implementations side by side:

```python
# find — returns first match or None
def find(self, name):
    if self.name == name:
        return self
    for child in self._children:
        result = child.find(name)
        if result is not None:
            return result
    return None

# all_breaching — accumulates into a list
def all_breaching(self):
    result = []
    for child in self._children:
        result.extend(child.all_breaching())
    return result

# leaves — accumulates into a list
def leaves(self):
    result = []
    for child in self._children:
        result.extend(child.leaves())
    return result
```

They are all variations of the same shape:

```
do something with self (optionally)
for each child, call the same method
combine results
```

Once you have the Composite structure in place, adding new tree operations
is mechanical. You implement the leaf case (usually trivial) and the group
case (usually a loop). You never touch the calling code.

### `find` is depth-first and short-circuits

The `for child in self._children` loop returns immediately after finding the
first match. It does not search the rest of the tree.

This is depth-first: it goes all the way into the first subtree before
trying the second. The test tree looks like:

```
system
  cpu
    cpu_usage    <- found here first
    cpu_iowait
  memory
    mem_used
```

Searching for `"cpu_usage"` finds it before ever looking at `memory`.

### `leaves()` uses `isinstance` — and that is fine

`MetricValue.leaves()` returns `[self]`.
`MetricGroup.leaves()` concatenates children's results.

Because `MetricValue.leaves()` always returns a list containing itself (a
`MetricValue`), the `isinstance` check is implicit in the delegation: only
leaves return themselves, groups collect their children's leaves. The caller
never needs to write `isinstance`.

If you were writing a standalone traversal function instead, you would need
explicit `isinstance` checks — that is the tradeoff.

### The design question: methods on the interface vs standalone functions

The exercise asked you to think about where these operations should live.

**Methods on the interface** (what we built):

Pros:
- Clean call site: `system.find("cpu_usage")`
- No knowledge of internal structure needed outside the tree
- Adding a new node type forces you to implement the operation (compiler/type
  checker catches omissions)

Cons:
- The `Metric` interface grows with every new operation
- Operations that don't make sense on leaves still appear there
  (e.g., `MetricValue.leaves()` returning `[self]` feels slightly awkward)

**Standalone functions** (the alternative):

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

Pros:
- Interface stays minimal
- Operations can be added without modifying any class

Cons:
- Exposes internal structure (`_children`) or requires a public accessor
- The `isinstance` check re-appears in every function
- A new node type silently breaks the function unless you remember to handle it

### The Visitor pattern resolves this tension

The **Visitor pattern** (a future topic) is the formal solution for adding
operations to a class hierarchy without modifying the classes.

The idea is:

```python
class MetricVisitor(ABC):
    @abstractmethod
    def visit_value(self, metric: MetricValue): ...

    @abstractmethod
    def visit_group(self, metric: MetricGroup): ...
```

Each `Metric` subclass implements `accept(visitor)`:

```python
class MetricValue(Metric):
    def accept(self, visitor: MetricVisitor):
        visitor.visit_value(self)

class MetricGroup(Metric):
    def accept(self, visitor: MetricVisitor):
        visitor.visit_group(self)
        for child in self._children:
            child.accept(visitor)
```

Now `find`, `all_breaching`, and `leaves` become `Visitor` implementations.
The tree stays stable; operations are added externally.

This is worth knowing, but for most small trees, methods on the interface
are simpler and easier to read. Use Visitor when the tree is large, stable,
and the number of external operations is expected to grow.

---

[Exercise 3](exercise3.md) · [Back to Composite](composite.md)
