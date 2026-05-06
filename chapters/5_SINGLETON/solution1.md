# Solution 1: Basic Singleton with `__new__`

## Core idea

The important change is in `__new__`:

```python
if cls._instance is None:
    cls._instance = super().__new__(cls)
return cls._instance
```

`__new__` runs before `__init__`. It is the method that actually creates or returns an object.

So the first call creates the settings object. Later calls return the cached object.

## Why `__init__` needs a guard

Even if `__new__` returns the same object, Python still calls `__init__` after construction syntax:

```python
AppSettings(environment="production", debug=True)
```

Without a guard, this would reset the existing object every time.

That is why the solution uses:

```python
if getattr(self, "_initialized", False):
    return
```

The first call initializes the object. Later calls return immediately.

## What the tests prove

The tests check four ideas:

1. Two calls return the same object.
2. The first initialization wins.
3. State changed through one reference is visible through another.
4. Later calls do not erase already-stored feature flags.

## Pitfall

This implementation makes the class responsible for its own creation rules. That is fine for learning, but in larger applications a module-level object or dependency injection can be clearer.
