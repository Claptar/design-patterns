# Exercise 2: Singleton as a Decorator

## Goal

Turn Singleton behavior into a reusable decorator.

In Exercise 1, the singleton logic was written directly inside `AppSettings`. That works, but the same `_instance` and `__new__` logic would be repeated if another class also needed Singleton behavior.

In this exercise, you will move the Singleton behavior into a decorator:

```python
@singleton
class MetricsRegistry:
    ...
```

## What you will practice

- Writing a decorator that receives a class
- Returning a wrapper function that controls instance creation
- Storing the cached instance in a closure
- Adding a small `reset_instance()` helper for exercises and tests
- Seeing the main tradeoff: the class name now points to a function

## Starting point

Open `exercise2.py`.

Fill the TODOs in `singleton(cls)` so that:

1. The first call creates the decorated object.
2. Later calls return the cached object.
3. `reset_instance()` clears the cached instance.
4. The same decorator works for more than one class.

## Expected behavior

```python
metrics1 = MetricsRegistry(namespace="billing")
metrics2 = MetricsRegistry(namespace="email")

assert metrics1 is metrics2
assert metrics2.namespace == "billing"
```

The first call wins because the second call returns the cached object.

## Run the tests

```bash
python -m pytest exercise2.py
```
