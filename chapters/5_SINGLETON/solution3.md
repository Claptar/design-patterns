# Solution 3: Singleton as a Metaclass

## Normal class behavior

A regular class uses `type` as its metaclass.

So this:

```python
RegularSettings("development")
```

roughly goes through:

```python
type.__call__(RegularSettings, "development")
```

That normal call path creates a new object every time.

## What changes with `SingletonMeta`

When we write:

```python
class Settings(metaclass=SingletonMeta):
    ...
```

then this:

```python
Settings("development")
```

runs through:

```python
SingletonMeta.__call__(Settings, "development")
```

That is the one doorway we changed.

## The implementation

```python
class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
```

`super().__call__(*args, **kwargs)` means:

> Use the normal class-call behavior to create and initialize the object.

But we only do that once per class.

## Where the instances live

The cache is here:

```python
SingletonMeta._instances
```

The keys are classes:

```python
Settings
PluginRegistry
```

The values are the one cached instance for each class.

So `Settings` and `PluginRegistry` do not share the same object. Each class gets one object of its own.

## Why `__init__` runs only once

`__init__` runs inside `super().__call__`.

Since the metaclass calls `super().__call__` only when the class is missing from the cache, initialization also happens only once.

That is different from the basic `__new__` version, where you often need an explicit `_initialized` guard.

## Why this is different from the decorator version

The decorator version replaces the class name with a function.

The metaclass version keeps `Settings` as a real class.

That is why this still works:

```python
isinstance(settings, Settings)
```

## Pitfall

Metaclasses are powerful but less familiar. Use this approach when preserving class identity matters or when several classes should share the same creation rule.

For a small one-off singleton, a module-level object or a simpler implementation may be easier to read.
