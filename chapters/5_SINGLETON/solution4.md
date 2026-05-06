# Solution 4: Monostate

## Core idea

The base class stores one dictionary per subclass:

```python
_shared_states = {}
```

Then each object redirects its instance dictionary:

```python
self.__dict__ = self._shared_states[cls]
```

After that, different objects read and write the same attribute storage.

## Why `type(self)` matters

This line chooses a shared dictionary for the concrete subclass:

```python
cls = type(self)
```

That means all `Preferences` objects share one dictionary, while all `Metrics` objects share another dictionary.

Without this per-subclass design, `Preferences` and `Metrics` could accidentally share unrelated state.

## Why initialization needs a guard

Monostate allows normal object creation. That means `__init__` runs for every new object.

But every object points to the same state dictionary. Without this guard:

```python
if getattr(self, "_initialized", False):
    return
```

later objects would reset the shared state.

So the first `Preferences(...)` call initializes the shared dictionary. Later calls become additional views over the same state.

## Monostate versus Singleton

Singleton:

```python
a = Settings()
b = Settings()
assert a is b
```

Monostate:

```python
a = Preferences()
b = Preferences()
assert a is not b
assert a.__dict__ is b.__dict__
```

Singleton shares identity and state.

Monostate keeps different identities but shares state.

## When to prefer which

Use Singleton when the design rule is:

> There should be exactly one object.

Use Monostate when the design rule is:

> It is okay to create many objects, but they should behave like views over one shared state.

## Pitfall

Monostate can surprise readers because two different objects are not independent. Use it only when shared state is intentional and obvious from the class name or documentation.
