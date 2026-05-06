# Exercise 3: Singleton as a Metaclass

## Goal

Implement Singleton behavior with a metaclass.

In Exercise 2, the decorator worked, but it replaced the class name with a wrapper function. In this exercise, the class should remain a real class.

That is the advantage of the metaclass approach.

## What you will practice

- Understanding that normal classes use `type` as their metaclass
- Overriding `__call__` on a custom metaclass
- Caching one instance per class
- Keeping `isinstance(obj, Class)` working
- Giving each singleton class its own cached instance

## The normal behavior

A regular class behaves roughly like this:

```python
type.__call__(RegularSettings, "development")
```

That creates a new object every time.

Your job is to change that call path by defining:

```python
class SingletonMeta(type):
    def __call__(cls, *args, **kwargs):
        ...
```

Then classes can opt in:

```python
class Settings(metaclass=SingletonMeta):
    ...
```

## Starting point

Open `exercise3.py`.

Fill the TODOs so that:

1. Regular classes still create new objects every call.
2. Classes using `SingletonMeta` return one cached object.
3. `__init__` runs only on the first creation.
4. Each singleton class has its own cached instance.
5. The class remains a real class, so `isinstance(obj, Settings)` works.

## Run the tests

```bash
python -m pytest exercise3.py
```
