# Exercise 1: Basic Singleton with `__new__`

## Goal

Implement a basic Singleton for application settings.

The object represents runtime configuration for one running application process. Different parts of the application may call `AppSettings()`, but they should all receive the same object.

## What you will practice

- Using `__new__` to control object creation
- Returning the already-created instance on later calls
- Guarding `__init__` so it does not reset state every time
- Checking object identity with `is`

## Starting point

Open `exercise1.py`.

You are given an `AppSettings` class and tests. Fill the TODOs so that:

1. `AppSettings()` always returns the same object.
2. The first initialization wins.
3. Later calls do not reset `environment`, `debug`, or `features`.
4. Feature flags changed through one reference are visible through another reference.

## Expected behavior

```python
settings1 = AppSettings(environment="development", debug=False)
settings2 = AppSettings(environment="production", debug=True)

assert settings1 is settings2
assert settings2.environment == "development"
assert settings2.debug is False
```

The second call should not create or reinitialize a new settings object.

## Run the tests

```bash
python -m pytest exercise1.py
```
