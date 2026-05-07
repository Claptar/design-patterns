---
layout: default
title: Composite Design Pattern
---

# Composite Design Pattern

## 1. What problem are we trying to solve?

Imagine you're building a file system explorer. A folder can contain files, but it can also contain other folders — which themselves contain more files and folders.

Now you want to calculate the total size of everything. You might write:

```python
def total_size(folder):
    size = 0
    for item in folder.contents:
        if isinstance(item, File):
            size += item.size
        elif isinstance(item, Folder):
            size += total_size(item)  # recurse
    return size
```

That `isinstance` check is the smell. Every operation — get size, find by name, render a tree — needs the same if/elif branching. Add a new item type (a symlink, a compressed archive) and you hunt down every `isinstance` chain.

The deeper problem is:

> We have a hierarchy of objects where some objects are leaves and some are containers of other objects, but the calling code shouldn't have to know which is which.

---

## 2. Concept introduction

The **Composite pattern** lets you treat individual objects and groups of objects through the same interface.

In plain English:

> Make leaf nodes and container nodes look identical to the outside world, so you can operate on a whole tree without caring whether you're touching one thing or many.

Composite is a **structural pattern** — it's about how objects are composed. It answers:

> How do I let clients treat a single object and a collection of objects uniformly?

The shape is:

```
Component (shared interface)
├── Leaf           → has no children, does the real work
└── Composite      → holds children, delegates to them
```

The magic is that a `Composite` holds `Component` objects — which can themselves be `Composite` objects. The tree can be arbitrarily deep, and the caller never sees the nesting.

---

## 3. The key insight: the interface is the same

The power of Composite comes from one rule:

> `Leaf` and `Composite` must implement exactly the same interface.

That sameness is what lets a `Composite` hold a list of `Component` objects without knowing or caring which are leaves and which are sub-composites.

```python
from abc import ABC, abstractmethod

class Component(ABC):
    @abstractmethod
    def operation(self):
        ...
```

A `Leaf` implements the work directly. A `Composite` implements it by looping over children:

```python
class Leaf(Component):
    def operation(self):
        return "leaf result"

class Composite(Component):
    def __init__(self):
        self._children: list[Component] = []

    def add(self, component: Component):
        self._children.append(component)

    def operation(self):
        return [child.operation() for child in self._children]
```

The client never calls `isinstance`. It just calls `.operation()` on whatever it has.

---

## 4. Minimal file system example

```python
from __future__ import annotations
from abc import ABC, abstractmethod


class FileSystemItem(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def size(self) -> int: ...

    @abstractmethod
    def display(self, indent: int = 0) -> None: ...


class File(FileSystemItem):
    def __init__(self, name: str, size_bytes: int):
        super().__init__(name)
        self._size = size_bytes

    def size(self) -> int:
        return self._size

    def display(self, indent: int = 0) -> None:
        print(" " * indent + f"📄 {self.name} ({self._size} B)")


class Folder(FileSystemItem):
    def __init__(self, name: str):
        super().__init__(name)
        self._children: list[FileSystemItem] = []

    def add(self, item: FileSystemItem) -> Folder:
        self._children.append(item)
        return self

    def size(self) -> int:
        return sum(child.size() for child in self._children)

    def display(self, indent: int = 0) -> None:
        print(" " * indent + f"📁 {self.name}/")
        for child in self._children:
            child.display(indent + 2)
```

Usage:

```python
root = Folder("home")
docs = Folder("documents")
pics = Folder("pictures")

docs.add(File("report.pdf", 204_800))
docs.add(File("notes.txt", 1_024))

pics.add(File("photo.jpg", 3_145_728))

root.add(docs).add(pics).add(File("readme.md", 512))

root.display()
print(f"\nTotal: {root.size():,} B")
```

Output:

```
📁 home/
  📁 documents/
    📄 report.pdf (204800 B)
    📄 notes.txt (1024 B)
  📁 pictures/
    📄 photo.jpg (3145728 B)
  📄 readme.md (512 B)

Total: 3,352,064 B
```

Notice: `root.size()`, `docs.size()`, and `File("readme.md", 512).size()` are all called identically. The client has no `isinstance` checks anywhere.

---

## 5. Natural example: a UI widget tree

A richer natural example is a GUI or document layout system. Every UI framework (HTML DOM, Android Views, SwiftUI) is built on Composite.

A `Widget` can be a button (leaf) or a panel containing other widgets (composite). You call `.render()` on the root and the whole tree draws itself.

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class BoundingBox:
    width: int
    height: int


class Widget(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def render(self, depth: int = 0) -> None: ...

    @abstractmethod
    def bounding_box(self) -> BoundingBox: ...


class Button(Widget):
    def __init__(self, label: str, width: int = 80, height: int = 32):
        super().__init__(f"Button({label!r})")
        self._label = label
        self._width = width
        self._height = height

    def render(self, depth: int = 0) -> None:
        print("  " * depth + f"[{self._label}]")

    def bounding_box(self) -> BoundingBox:
        return BoundingBox(self._width, self._height)


class Label(Widget):
    def __init__(self, text: str):
        super().__init__(f"Label({text!r})")
        self._text = text

    def render(self, depth: int = 0) -> None:
        print("  " * depth + self._text)

    def bounding_box(self) -> BoundingBox:
        return BoundingBox(len(self._text) * 8, 20)


class Panel(Widget):
    def __init__(self, name: str, padding: int = 8):
        super().__init__(name)
        self._children: list[Widget] = []
        self._padding = padding

    def add(self, widget: Widget) -> "Panel":
        self._children.append(widget)
        return self

    def render(self, depth: int = 0) -> None:
        print("  " * depth + f"┌── {self.name}")
        for child in self._children:
            child.render(depth + 1)
        print("  " * depth + f"└──")

    def bounding_box(self) -> BoundingBox:
        if not self._children:
            return BoundingBox(0, 0)
        total_height = sum(c.bounding_box().height for c in self._children)
        max_width = max(c.bounding_box().width for c in self._children)
        return BoundingBox(max_width + 2 * self._padding,
                           total_height + 2 * self._padding)
```

Usage:

```python
toolbar = (Panel("Toolbar")
    .add(Button("New"))
    .add(Button("Open"))
    .add(Button("Save")))

sidebar = (Panel("Sidebar")
    .add(Label("Files"))
    .add(Button("Upload", width=100))
    .add(Button("Download", width=100)))

root = (Panel("AppWindow")
    .add(toolbar)
    .add(sidebar)
    .add(Button("Status Bar", width=600, height=24)))

root.render()
print(f"\nApp window size: {root.bounding_box()}")
```

```
┌── AppWindow
  ┌── Toolbar
    [New]
    [Open]
    [Save]
  └──
  ┌── Sidebar
    Files
    [Upload]
    [Download]
  └──
  [Status Bar]
└──
App window size: BoundingBox(width=116, height=216)
```

`root.bounding_box()` recurses down the whole tree with zero `isinstance` checks. Replacing any leaf with a sub-panel just works.

---

## 6. Connection to earlier concepts and SOLID

**Composite and the Open/Closed Principle** — you can add new `Component` subtypes (a `Symlink`, a `CompressedArchive`, an `Image` widget) without changing any traversal code. The tree-walking logic in `Folder.size()` or `Panel.render()` never needs to be modified.

**Composite and the Single Responsibility Principle** — each class has one job. `File` knows how to represent a file. `Folder` knows how to hold children and delegate. The traversal strategy doesn't live in your business logic — it lives in the tree itself.

**Composite and the Liskov Substitution Principle** — this is where to be careful. If `Composite` exposes `add()` and `remove()` on the base `Component` interface, then `Leaf` must either implement them (throwing `NotImplementedError`) or they shouldn't be on the interface at all. The cleaner design keeps `add()`/`remove()` only on `Composite`, not on the shared interface. The slight inconvenience is that you need to know you have a `Composite` to add children — but that's usually fine because tree *construction* is separate from tree *traversal*.

**Composite and the Adapter pattern** — Composite is about uniform traversal of a tree you control. Adapter is about making a third-party object fit an interface you expect. They can work together: an `ExternalDataSource` that has the wrong interface can be wrapped in an Adapter that implements `Component`, then plugged into a Composite tree.

**Composite and Builder** — complex trees are often best *built* using a Builder (or a fluent API like `.add().add()` above). The Builder manages the assembly process; Composite defines what the result looks like.

---

## 7. Example from a popular Python package: `pathlib` and scikit-learn pipelines

**`pathlib.Path`** exhibits Composite-like behaviour. `Path.iterdir()` gives you `Path` objects regardless of whether they're files or directories. `.stat().st_size` works on both. The API treats files and folders uniformly for navigation operations.

A clearer data-science example is **scikit-learn's `Pipeline` and `FeatureUnion`**. A `Pipeline` chains transformers and an estimator. A `FeatureUnion` runs multiple transformers in parallel and concatenates their outputs. Crucially, a `FeatureUnion` can itself be a step inside a `Pipeline` — and a `Pipeline` can be a step inside another `Pipeline`.

```python
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression

pipeline = Pipeline([
    ("features", FeatureUnion([
        ("scaled", StandardScaler()),
        ("minmax", MinMaxScaler()),
    ])),
    ("reduce", PCA(n_components=5)),
    ("model", LogisticRegression()),
])

pipeline.fit(X_train, y_train)
pipeline.predict(X_test)
```

`pipeline.fit()` calls `.fit_transform()` on the `FeatureUnion`, which calls `.fit_transform()` on each inner transformer — and `pipeline.fit()` itself can be nested inside a `GridSearchCV` that calls `.fit()` on it. The calling code doesn't know or care how deep the nesting goes. Each step exposes the same `fit` / `transform` / `predict` interface.

Reference: [scikit-learn Pipeline documentation](https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html)

---

## 8. When to use, and when not to use

Use Composite when:

| Situation | Why Composite helps |
|---|---|
| You have a part-whole hierarchy | Files in folders, widgets in panels, nodes in a DOM |
| Clients should ignore the difference between leaf and container | Traversal code shouldn't need `isinstance` |
| Operations need to recurse uniformly | `size()`, `render()`, `validate()`, `flatten()` |
| The tree can be arbitrarily deep | You don't know at design time how many levels there will be |
| You want to compose objects into tree structures | Build complex wholes from simple parts |

Good examples:

```text
File systems
UI widget trees
Expression trees (math, queries, rules engines)
Organization charts
Bill-of-materials / product catalogs
Menu systems
Scene graphs in game engines
HTML/XML DOM
```

Do not use Composite when:

- The hierarchy is flat and will never nest — a simple list of items with no nesting doesn't need the pattern.
- Leaves and composites have genuinely different operations that can't be unified — forcing a common interface leads to fake `NotImplementedError` methods (an ISP violation).
- You don't actually need uniform treatment — if the client always knows whether it has a leaf or a container, the abstraction adds complexity with no benefit.
- Performance is critical and virtual dispatch / tree traversal overhead matters — flat data structures (arrays, DataFrames) are faster for bulk operations.

---

## 9. Practical rule of thumb

Ask:

> Do I have a hierarchy where containers hold the same *kind* of thing as their contents?

If yes — folders hold files and folders, panels hold buttons and panels, `FeatureUnion` holds transformers including other `FeatureUnion`s — Composite is likely the right tool.

Ask:

> Am I writing `isinstance(item, LeafType)` or `isinstance(item, ContainerType)` checks in my traversal code?

If yes, that's the signal. Composite eliminates those checks by making the interface identical.

Ask:

> Do I need operations to work on both individual objects and trees of objects without different code paths?

If yes, Composite gives you that for free.

Ask:

> Is my "hierarchy" actually just a flat list with no nesting?

If yes, a plain list is better. Composite earns its keep only when the nesting is real.

---

## 10. Summary and mental model

Composite is a structural pattern for part-whole hierarchies. It lets a tree of objects be traversed uniformly because every node — leaf or container — exposes the same interface.

The mental model for Composite vs the patterns you've already seen:

| Pattern | Main job |
|---|---|
| Adapter | Make an incompatible object fit the interface you expect |
| Bridge | Decouple two independent dimensions so both can grow without M×N explosion |
| Builder | Assemble a complex object step by step with rules and validation |
| Factory | Decide which concrete class to create |
| **Composite** | **Treat individual objects and groups of objects through the same interface** |

In one sentence:

> Composite is useful when you have a part-whole hierarchy and you want clients to treat a single leaf and an entire subtree through exactly the same interface, eliminating `isinstance` checks from your traversal code.
