# Exercise 4: Monostate

## Goal

Implement Monostate: many objects, one shared state.

Singleton says:

```text
one object
```

Monostate says:

```text
many objects, one shared state
```

In this exercise, `Preferences()` should create different objects, but all `Preferences` objects should share the same attributes.

## What you will practice

- Redirecting each object's `__dict__` to shared storage
- Keeping object identity separate from object state
- Guarding initialization so later objects do not reset shared state
- Giving each subclass its own shared state dictionary
- Comparing Monostate with Singleton

## Starting point

Open `exercise4.py`.

Fill the TODOs so that:

1. `Preferences()` creates different objects.
2. Different `Preferences` objects share the same `__dict__`.
3. Changing one object's attribute is visible through another object.
4. Later `Preferences(...)` calls do not reset the first initialization.
5. Different subclasses do not accidentally share state.

## Expected behavior

```python
first = Preferences(theme="light")
second = Preferences(theme="dark")

assert first is not second
assert first.__dict__ is second.__dict__
assert second.theme == "light"

first.theme = "dark"
assert second.theme == "dark"
```

## Run the tests

```bash
python -m pytest exercise4.py
```
