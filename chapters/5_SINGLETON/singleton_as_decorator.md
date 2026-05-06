---
layout: default
title: "Singleton as Decorator"
---

# Singleton as Decorator

## 1. What problem are we trying to solve?

In a basic Singleton implementation, we may put the instance-control logic directly inside the class:

```python
class Settings:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance
```

This works, but it creates a new problem:

> Every class that wants Singleton behavior has to reimplement the same logic.

For example:

```python
class Settings:
    ...


class MetricsRegistry:
    ...


class PluginRegistry:
    ...
```

If all three should be singletons, we do not want to copy and paste `_instance` and `__new__` into every class.

So the problem is:

> How do we make Singleton behavior reusable without putting the Singleton machinery inside every class?

A decorator gives us one Pythonic answer.

---

## 2. Concept introduction

A **singleton decorator** is a function that takes a class and returns a controlled creation function.

In plain English:

> When someone tries to create this class, first check whether we already created one. If yes, return the old one. If no, create it.

The class can be written normally:

```python
@singleton
class Settings:
    ...
```

The Singleton logic lives outside the class, inside the decorator.

That means the decorator gives us reusable Singleton behavior.

---

## 3. Minimal decorator implementation

```python
def singleton(cls):
    instance = None

    def get_instance(*args, **kwargs):
        nonlocal instance

        if instance is None:
            instance = cls(*args, **kwargs)

        return instance

    return get_instance
```

Now we can use it like this:

```python
@singleton
class Settings:
    def __init__(self, environment: str):
        self.environment = environment
```

Usage:

```python
settings1 = Settings("development")
settings2 = Settings("production")

print(settings1 is settings2)
print(settings1.environment)
print(settings2.environment)
```

Output:

```text
True
development
development
```

The first call creates the object:

```python
Settings("development")
```

The second call does not create a new object:

```python
Settings("production")
```

It returns the original object.

So in this simple implementation:

> The first call wins.

---

## 4. What actually happened?

Before decoration, this name:

```python
Settings
```

refers to the class.

After decoration, this name:

```python
Settings
```

refers to the function returned by this call:

```python
singleton(Settings)
```

So this:

```python
Settings("development")
```

is not directly calling the class anymore.

It is calling the wrapper function:

```python
get_instance("development")
```

That wrapper function decides whether to create the object or return the cached one.

The movement looks like this:

```text
@singleton
class Settings
        |
        v
singleton(Settings)
        |
        v
returns get_instance
        |
        v
Settings now points to get_instance
        |
        v
Settings(...) returns cached instance
```

That is the core decorator mechanism.

---

## 5. Natural example: metrics registry

Suppose your application records metrics:

```text
orders_created
emails_sent
payments_failed
```

You want all parts of the app to update the same registry.

```python
@singleton
class MetricsRegistry:
    def __init__(self):
        self._counters = {}

    def increment(self, name: str):
        self._counters[name] = self._counters.get(name, 0) + 1

    def get(self, name: str):
        return self._counters.get(name, 0)
```

Usage:

```python
billing_metrics = MetricsRegistry()
email_metrics = MetricsRegistry()

billing_metrics.increment("payments_failed")
email_metrics.increment("emails_sent")

print(billing_metrics is email_metrics)
print(billing_metrics.get("emails_sent"))
```

Output:

```text
True
1
```

Even though different parts of the app call `MetricsRegistry()`, they all get the same registry.

That is a natural Singleton use case:

> The object represents one shared application-wide registry.

---

## 6. Why a decorator feels nice here

The decorator version has a very readable signal:

```python
@singleton
class MetricsRegistry:
    ...
```

The reader sees the intent immediately:

```text
This class is special.
This class should have one shared instance.
```

The class itself does not need to know about `_instance`, `__new__`, or caching.

That separation can feel clean in small examples.

The decorator owns the Singleton behavior.

The decorated class owns the domain behavior.

```text
singleton decorator -> controls instance creation
MetricsRegistry     -> stores and updates counters
```

---

## 7. The main downside

The simple decorator version has an important downside:

```python
@singleton
class Settings:
    ...
```

After decoration, `Settings` is no longer really the class.

It is the wrapper function returned by the decorator.

That means this can become awkward:

```python
isinstance(settings1, Settings)
```

Why?

Because `Settings` now points to a function, not the original class.

So the simple decorator version is easy to understand, but it changes what the class name means.

That is the biggest practical warning.

---

## 8. A slightly improved decorator

We can at least preserve some metadata with `functools.wraps`.

```python
from functools import wraps


def singleton(cls):
    instance = None

    @wraps(cls)
    def get_instance(*args, **kwargs):
        nonlocal instance

        if instance is None:
            instance = cls(*args, **kwargs)

        return instance

    return get_instance
```

This helps with things like the wrapper's name and documentation.

But it does not fully solve the deeper issue:

```text
The class name still points to a function.
```

So if preserving class behavior matters, a metaclass is usually a better fit.

---

## 9. Connection to earlier concepts

### Connection to creational patterns

Singleton is a creational pattern because it controls object creation.

The concern is not how objects communicate or how objects are composed.

The concern is:

```text
How many instances should be created?
```

The decorator version answers:

```text
Create the first instance, then reuse it.
```

### Connection to Factory

A factory decides which object to create.

A singleton decorator decides whether to create a new object at all.

| Pattern | Main question |
|---|---|
| Factory | Which object should I create? |
| Singleton decorator | Should I create the object or return the cached one? |

The decorator behaves a little like a small factory function because it controls object creation.

But the purpose is different.

Factory is about selection.

Singleton is about identity.

### Connection to Builder

Builder is about constructing a complex object step by step.

Singleton decorator is not about step-by-step construction.

It is about reusing one shared instance.

```text
Builder: construct this object correctly.
Singleton: make sure there is only one of this object.
```

### Connection to SOLID

Singleton can easily become hidden global state.

This is convenient but risky:

```python
class OrderService:
    def place_order(self, order):
        registry = MetricsRegistry()
        registry.increment("orders_created")
```

The service now secretly depends on a global registry.

A more testable design may pass the registry in:

```python
class OrderService:
    def __init__(self, metrics_registry):
        self.metrics_registry = metrics_registry

    def place_order(self, order):
        self.metrics_registry.increment("orders_created")
```

The registry may still be a singleton in production, but the service does not hard-code how to get it.

---

## 10. When to use singleton as decorator

Use the decorator version when:

```text
you want a small, simple implementation
you have one or two singleton classes
you do not need subclassing
you do not care much about isinstance checks
you want the Singleton behavior to be visually obvious with @singleton
```

A good teaching example:

```python
@singleton
class MetricsRegistry:
    ...
```

This is easy to read and easy to explain.

---

## 11. When not to use singleton as decorator

Avoid the simple decorator version when:

```text
the class must remain a normal class
other code needs isinstance(obj, Class)
you need subclassing
you are writing a library API
you care deeply about type checkers and IDE support
```

Also avoid it when a module-level object would be simpler:

```python
# metrics.py
metrics_registry = MetricsRegistry()
```

In Python, this is often the cleanest way to share one object.

---

## 12. Practical rule of thumb

Ask:

> Do I want a quick reusable Singleton for one class?

A decorator may be fine.

Ask:

> Does this class need to remain a proper class for `isinstance`, subclassing, or type checking?

Use a metaclass or another approach instead.

Ask:

> Am I using Singleton just to avoid passing dependencies around?

Prefer dependency injection.

Ask:

> Is a module-level object enough?

Prefer the module-level object.

---

## 13. Summary and mental model

Singleton as a decorator means:

> Replace the class name with a wrapper that returns one cached instance.

The mental model:

```text
Decorator replaces the doorway.
Calling Settings() actually calls a wrapper function.
The wrapper returns the cached instance.
```

In one sentence:

> Singleton as a decorator is the simple wrapper approach: easy to teach and easy to write, but it changes what the class name means.

---

[Singleton as Metaclass](singleton_as_metaclass.md)
