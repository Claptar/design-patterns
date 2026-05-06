# Solution 2: Singleton as a Decorator

## Core idea

The decorator receives a class:

```python
def singleton(cls):
    ...
```

Then it returns a wrapper function:

```python
def get_instance(*args, **kwargs):
    ...
```

The wrapper owns a closure variable:

```python
instance = None
```

The first call creates the object. Later calls return the cached object.

## Why this works

After decoration, this:

```python
@singleton
class MetricsRegistry:
    ...
```

roughly becomes this:

```python
MetricsRegistry = singleton(MetricsRegistry)
```

So calling `MetricsRegistry(...)` now calls `get_instance(...)`, not the original class directly.

## Why `reset_instance()` is included

The cached object lives in a closure, so it is not directly visible as `MetricsRegistry._instance`.

That is why the decorator exposes:

```python
MetricsRegistry.reset_instance()
```

This is useful in exercises and tests because it lets you create a fresh singleton object for the next scenario.

## Pitfall

The simple decorator version changes what the class name means.

Before decoration, `MetricsRegistry` is a class. After decoration, `MetricsRegistry` is a function that returns the singleton instance.

That can make `isinstance(obj, MetricsRegistry)` awkward because `MetricsRegistry` no longer points to the class. The solution stores the original class on `__wrapped__`, but the public name is still the wrapper function.

This is the main reason to learn the metaclass version next.
