---
layout: default
title: Monostate Pattern
---

# Monostate Pattern

## 1. What problem are we trying to solve?

With Singleton, we solve this problem:

> There should be only one object.

For example:

```python
settings1 = Settings()
settings2 = Settings()

print(settings1 is settings2)  # True
```

But sometimes the real problem is slightly different.

Maybe we do **not** care whether there is one object or many objects. What we care about is that all objects share the same state.

For example, imagine application-wide settings:

```python
billing_settings = Settings()
email_settings = Settings()
reporting_settings = Settings()
```

These may be three different `Settings` objects.

That is fine.

But they should not disagree about the actual settings.

If one part of the program changes this:

```python
billing_settings.debug = True
```

then another part should see the same value:

```python
print(email_settings.debug)  # True
```

So the problem is:

> We want many normal-looking instances, but all of them should share the same internal state.

That is what **Monostate** solves.

---

## 2. Concept introduction

The **Monostate pattern** means:

> All instances are different objects, but they share the same state.

In plain English:

```text
Singleton:
    one object

Monostate:
    many objects, one shared state
```

With Singleton:

```python
a = Settings()
b = Settings()

print(a is b)  # True
```

With Monostate:

```python
a = Settings()
b = Settings()

print(a is b)  # False
```

But:

```python
a.debug = True

print(b.debug)  # True
```

That is the key idea.

The identity is different:

```python
a is b  # False
```

But the state is shared:

```python
a.__dict__ is b.__dict__  # True
```

So Monostate does not say:

> Prevent new objects from being created.

It says:

> Let new objects be created, but make them all use the same state storage.

---

## 3. Minimal implementation

In Python, the simplest Monostate implementation uses `__dict__`.

Normally, each object has its own instance dictionary:

```python
obj.__dict__
```

That dictionary stores the object's attributes.

Monostate changes that.

```python
class Monostate:
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state
```

Now every instance points its `__dict__` to the same dictionary.

Usage:

```python
class Settings(Monostate):
    pass


settings1 = Settings()
settings2 = Settings()

settings1.environment = "development"
settings2.debug = True

print(settings1.environment)  # development
print(settings2.environment)  # development

print(settings1.debug)        # True
print(settings2.debug)        # True

print(settings1 is settings2)                    # False
print(settings1.__dict__ is settings2.__dict__)  # True
```

The two objects are different objects.

But their attributes live in the same dictionary.

---

## 4. What actually happened?

A normal Python object looks like this:

```text
settings1
    - __dict__ = {"environment": "development"}

settings2
    - __dict__ = {"debug": True}
```

Each object has its own state.

A Monostate object looks like this:

```text
settings1
    \
     shared __dict__ = {
         "environment": "development",
         "debug": True
     }
    /
settings2
```

Both objects point to the same state dictionary.

So this:

```python
settings1.environment = "development"
```

writes into the shared dictionary.

Then this:

```python
settings2.environment
```

reads from that same shared dictionary.

That is the whole trick.

---

## 5. Adding initialization safely

There is one subtle problem.

Suppose we write this:

```python
class Settings(Monostate):
    def __init__(self):
        super().__init__()
        self.environment = "development"
        self.debug = False
```

Now every time we create a new `Settings()` object, `__init__` runs again.

```python
settings1 = Settings()
settings1.debug = True

settings2 = Settings()

print(settings1.debug)
```

This prints:

```text
False
```

Why?

Because the second `Settings()` call ran `__init__` again and reset the shared state.

So we need an initialization guard:

```python
class Settings(Monostate):
    def __init__(self):
        super().__init__()

        if getattr(self, "_initialized", False):
            return

        self.environment = "development"
        self.debug = False
        self._initialized = True
```

Now this works:

```python
settings1 = Settings()
settings1.debug = True

settings2 = Settings()

print(settings1.debug)  # True
print(settings2.debug)  # True
```

The first object initializes the shared state.

Later objects reuse it.

---

## 6. Natural example: application preferences

Imagine a desktop app or CLI tool with preferences:

```text
theme
language
autosave setting
recent project path
```

Different parts of the app may create a preferences object:

```python
editor_preferences = Preferences()
menu_preferences = Preferences()
startup_preferences = Preferences()
```

It is acceptable that these are different objects.

But they should represent the same preferences.

```python
class Monostate:
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class Preferences(Monostate):
    def __init__(self):
        super().__init__()

        if getattr(self, "_initialized", False):
            return

        self.theme = "light"
        self.language = "en"
        self.autosave = True
        self._initialized = True
```

Usage:

```python
editor_preferences = Preferences()
menu_preferences = Preferences()

editor_preferences.theme = "dark"

print(menu_preferences.theme)  # dark
```

This feels natural because `Preferences()` is not really trying to represent a unique physical object.

It is more like a view into shared application preference state.

---

## 7. Safer version: separate shared state per subclass

The simple `Monostate` base class has an important issue.

```python
class Monostate:
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state
```

If several classes inherit from it, they may accidentally share the same state.

```python
class Preferences(Monostate):
    pass


class Metrics(Monostate):
    pass
```

Now this can happen:

```python
preferences = Preferences()
metrics = Metrics()

preferences.theme = "dark"

print(metrics.theme)  # dark
```

That is probably not what we want.

A safer version gives each subclass its own shared dictionary:

```python
class Monostate:
    _shared_states = {}

    def __init__(self):
        cls = type(self)

        if cls not in self._shared_states:
            self._shared_states[cls] = {}

        self.__dict__ = self._shared_states[cls]
```

Now:

```python
class Preferences(Monostate):
    pass


class Metrics(Monostate):
    pass
```

Each class gets its own shared state:

```python
preferences1 = Preferences()
preferences2 = Preferences()

metrics1 = Metrics()
metrics2 = Metrics()

preferences1.theme = "dark"
metrics1.events = 10

print(preferences2.theme)  # dark
print(metrics2.events)     # 10

print(hasattr(metrics2, "theme"))  # False
```

This is usually the better Monostate base class.

---

## 8. Monostate versus Singleton

This is the most important comparison.

| Question | Singleton | Monostate |
|---|---|---|
| Are there many objects? | No | Yes |
| Is object identity shared? | Yes | No |
| Is state shared? | Yes | Yes |
| Does `a is b` return `True`? | Yes | No |
| Does changing `a.x` affect `b.x`? | Yes | Yes |
| Main mechanism | Control instance creation | Share instance state |
| Python implementation | `__new__`, decorator, or metaclass | Shared `__dict__` |

Example:

```python
# Singleton
settings1 = Settings()
settings2 = Settings()

settings1 is settings2  # True
```

```python
# Monostate
settings1 = Settings()
settings2 = Settings()

settings1 is settings2                    # False
settings1.__dict__ is settings2.__dict__  # True
```

So the mental split is:

```text
Singleton controls object identity.
Monostate controls object state.
```

Singleton says:

> Do not create a second object.

Monostate says:

> Create as many objects as you want, but make their state shared.

---

## 9. Connection to SOLID

Monostate can be convenient, but it can also become hidden global state.

This is convenient:

```python
class OrderService:
    def place_order(self, order):
        preferences = Preferences()
        if preferences.autosave:
            ...
```

But now `OrderService` secretly depends on shared preference state.

That can make the code harder to test, because tests may need to reset the shared state between runs.

It can also make the dependency less visible. The constructor of `OrderService` does not tell us that it needs preferences.

A more testable design may still pass the dependency in:

```python
class OrderService:
    def __init__(self, preferences):
        self.preferences = preferences

    def place_order(self, order):
        if self.preferences.autosave:
            ...
```

The production `preferences` object can still use Monostate internally.

But `OrderService` no longer hard-codes how it gets that object.

This connects especially to the Dependency Inversion Principle:

> Important business logic should not be tightly glued to concrete global details.

It also connects to the Single Responsibility Principle:

> A class should not secretly become responsible for finding its own global collaborators.

So Monostate is not automatically bad, but it should be used carefully.

---

## 10. When to use Monostate and when to use Singleton

Use **Monostate** when:

```text
you want normal object construction
you are okay with multiple instances existing
object identity does not matter
shared state is the real requirement
each instance can be thought of as a view over the same state
```

Good examples:

```text
application preferences
feature flags
small shared runtime settings
simple counters
small registries where identity does not matter
```

Use **Singleton** when:

```text
there should truly be one object
object identity matters
multiple instances would be conceptually wrong
external code may compare object identity
there is one shared manager, registry, sentinel, or resource owner
```

Good examples:

```text
one plugin registry
one missing-value sentinel
one process-wide metrics registry
one application container
```

The practical difference is this:

```text
Use Singleton when the design rule is:
    There must be one object.

Use Monostate when the design rule is:
    There may be many objects, but they must share state.
```

For example, if you want this to be true:

```python
settings1 is settings2
```

use Singleton.

If you only need this to be true:

```python
settings1.__dict__ is settings2.__dict__
```

or more generally:

```python
settings1.debug == settings2.debug
```

use Monostate.

---

## 11. When not to use Monostate

Avoid Monostate when shared state would surprise the reader.

For example:

```python
user1 = User()
user2 = User()

user1.name = "Alice"

print(user2.name)  # Alice
```

That would be terrible.

A `User` object should have its own state.

Monostate is also risky when tests need isolation:

```text
one test changes shared state
another test accidentally sees that change
```

It can also be confusing when object identity matters:

```python
a = Settings()
b = Settings()

a is b  # False
```

A reader may think these are independent objects, even though they are not independent in state.

That surprise is the main cost.

---

## 12. Practical rule of thumb

Ask:

> Do I need one shared object?

Use Singleton.

Ask:

> Do I need many objects that share the same state?

Use Monostate.

Ask:

> Would it surprise someone that two different instances share attributes?

Avoid Monostate.

Ask:

> Am I using this just to avoid passing dependencies?

Prefer dependency injection.

Ask:

> Is this Python code and I only need one shared thing?

Consider a module-level object first:

```python
preferences = Preferences()
```

That is often simpler than either Singleton or Monostate.

---

## 13. Summary and mental model

Monostate is the shared-state cousin of Singleton.

The core idea:

```text
Different objects.
Same state.
```

Singleton:

```text
settings1 --\
             one object with one state
settings2 --/
```

Monostate:

```text
settings1 --\
             shared state dictionary
settings2 --/

but settings1 and settings2 are different objects
```

In one sentence:

> Monostate allows many instances to exist, but makes them all share the same internal state.

The practical mental model:

```text
Singleton:
    one identity, one state

Monostate:
    many identities, one state
```

Use it only when shared state is an intentional design rule, not an accidental shortcut.
