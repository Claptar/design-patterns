# Singleton Design Pattern

## 1. What problem are we trying to solve?

Imagine an application has one shared configuration:

```python
config = AppConfig()
```

This configuration stores things like:

```text
database URL
API keys
feature flags
environment name
timeout settings
```

Now imagine different parts of the application accidentally create their own config objects:

```python
billing_config = AppConfig()
email_config = AppConfig()
reporting_config = AppConfig()
```

At first this may look harmless.

But now you may have three separate objects that are supposed to represent one global application configuration. If one part updates a setting, the others may not see it. If loading the config is expensive, you may repeat that work. If the object owns a resource, such as a connection pool or registry, you may accidentally create duplicates.

So the problem is:

> Some objects represent one shared thing in the running program, and having multiple instances would be confusing, wasteful, or incorrect.

That is the kind of problem Singleton tries to solve.

---

## 2. Concept introduction

The **Singleton pattern** ensures that a class has only one instance and gives the program a controlled way to access that instance.

In plain English:

> Singleton means: “There should be exactly one object of this kind, and everyone should use that same object.”

Singleton is a **creational pattern**. Creational patterns are about object creation. Singleton's specific creation rule is:

> Ensure only one instance exists.

The shape is usually:

```text
Class controls its own creation.
First request creates the object.
Later requests return the same object.
```

So instead of this:

```python
a = AppConfig()
b = AppConfig()

print(a is b)  # False
```

we want this:

```python
a = AppConfig()
b = AppConfig()

print(a is b)  # True
```

The important part is identity:

```python
a is b
```

not just equality:

```python
a == b
```

Singleton says both variables point to the same object.

---

## 3. A simple Python implementation

One common Python implementation uses `__new__`.

`__new__` is responsible for creating the object before `__init__` initializes it.

```python
class AppConfig:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        self.environment = "development"
        self.debug = True
```

Usage:

```python
config1 = AppConfig()
config2 = AppConfig()

print(config1 is config2)  # True
```

This works because the first call creates the object, and later calls return the same object.

But there is a subtle problem.

```python
config1 = AppConfig()
config1.environment = "production"

config2 = AppConfig()

print(config2.environment)
```

You might expect:

```text
production
```

But `__init__` runs every time `AppConfig()` is called, so it can reset state.

A safer version guards initialization:

```python
class AppConfig:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return

        self.environment = "development"
        self.debug = True
        self._initialized = True
```

Now initialization happens only once.

---

## 4. Natural example: application settings

Suppose you are building a backend service.

You have one `.env` file or one deployment environment. Your app should not have many independent configuration objects. It should have one shared configuration object.

```python
class Settings:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return

        self.database_url = "postgresql://localhost/app"
        self.cache_url = "redis://localhost:6379"
        self.debug = False
        self._initialized = True


settings_a = Settings()
settings_b = Settings()

print(settings_a is settings_b)  # True
```

This is natural because the application really has one runtime settings object.

The point is not just to save memory. The point is to avoid disagreement:

```text
billing code should not use one config
email code should not use another config
reporting code should not use a third config
```

They should all read from the same source.

---

## 5. The Pythonic alternative: module-level singleton

In Python, you often do not need a special Singleton class.

A module itself can act like a singleton.

For example:

```python
# settings.py

class Settings:
    def __init__(self):
        self.database_url = "postgresql://localhost/app"
        self.debug = False


settings = Settings()
```

Then other files import the same object:

```python
# billing.py
from settings import settings

print(settings.database_url)
```

```python
# email_service.py
from settings import settings

print(settings.debug)
```

This is often clearer than forcing Singleton behavior into the class.

The reason this works is that Python caches imported modules. Once a module has been imported, later imports reuse the same module object rather than creating a fresh one.

So in Python, this is usually enough:

```python
# one object created at module import time
settings = Settings()
```

This is often the most practical Singleton style in Python.

---

## 6. Connection to earlier learned concepts

### Singleton versus Factory

A **Factory** decides which object to create.

```python
processor = PaymentProcessorFactory.create_for_provider("stripe")
```

A **Singleton** controls how many instances may exist.

```python
settings1 = Settings()
settings2 = Settings()

settings1 is settings2  # True
```

So the questions are different:

| Pattern | Main question |
|---|---|
| Factory | Which class or object should I create? |
| Singleton | Should there be only one instance? |

Factory is about choosing between alternatives.

Singleton is about limiting identity.

### Singleton versus Builder

A **Builder** helps assemble a complex object step by step.

```python
request = (
    HttpRequestBuilder()
    .post("/orders")
    .with_json_body({"id": 123})
    .build()
)
```

A **Singleton** does not assemble a complex object. It controls access to one shared object.

Builder is useful when construction has rules, defaults, validation, or assembly steps.

Singleton is useful when the object represents one shared thing.

### Singleton and SOLID

Singleton can conflict with good design if it becomes hidden global state.

A careless Singleton can make high-level code depend directly on concrete global details:

```python
class OrderService:
    def place_order(self, order):
        database_url = Settings().database_url
        # save order using database_url
```

A more testable design is often dependency injection:

```python
class OrderService:
    def __init__(self, settings):
        self.settings = settings
```

Then production can pass the real settings object, and tests can pass a fake one.

---

## 7. Example from a popular Python package

A good data-science example is **pandas `pd.NA`**.

`pd.NA` is used as a shared missing-value indicator.

Example:

```python
import pandas as pd

s = pd.Series([1, 2, None], dtype="Int64")

print(s[2])           # <NA>
print(s[2] is pd.NA)  # True
```

This is a good Singleton-like use case because `<NA>` is not meant to be many different objects with different state.

It represents one special concept:

```text
missing value
unknown value
not available
```

So pandas gives users one shared sentinel object: `pd.NA`.

---

## 8. When to use Singleton

Use Singleton when these are true:

| Situation | Why Singleton may fit |
|---|---|
| There should logically be one instance | Example: process-wide settings |
| Multiple instances would cause inconsistency | Example: two separate registries disagree |
| The object represents a shared sentinel value | Example: `pd.NA` |
| The object is expensive and should be reused | Example: shared metadata cache |
| You need controlled access to a global resource | Example: one metrics registry |

Good examples:

```text
application settings
plugin registry
metrics registry
missing-value sentinel
feature flag registry
shared schema registry
```

But be careful with resources like database connections.

A single database connection is often not what you want in real backend systems. Usually you want a connection pool, and that pool may be passed around as a dependency.

---

## 9. When not to use Singleton

Avoid Singleton when you are just trying to avoid passing arguments.

This is a warning sign:

```python
class OrderService:
    def place_order(self, order):
        db = DatabaseConnection()
        db.save(order)
```

If `DatabaseConnection()` is a Singleton, the code hides its dependency. The method looks simple, but it secretly depends on global database state.

This makes tests harder:

```text
How do I replace the database with a fake one?
How do I reset Singleton state between tests?
What if one test changes the Singleton and another test sees the change?
```

Also avoid Singleton when the “only one” rule is not truly part of the domain.

Bad justification:

```text
I only need one right now.
```

Better justification:

```text
The application must have exactly one registry because all plugins must register in the same place.
```

There is a big difference between:

```text
I happen to create one.
```

and:

```text
There must be only one.
```

---

## 10. Practical rule of thumb

Ask:

> Would the program become incorrect or confusing if two instances existed?

If yes, Singleton might be useful.

Ask:

> Am I using Singleton just so I do not have to pass dependencies around?

If yes, prefer dependency injection.

Ask:

> Is this Python code?

If yes, consider a module-level object first:

```python
# settings.py
settings = Settings()
```

That is often simpler than writing a Singleton class.

Ask:

> Is this a shared sentinel value, like “missing” or “not configured”?

A Singleton object can be a good fit.

---

## 11. Summary and mental model

Singleton is a creational pattern that controls object identity.

It says:

> This class should have one shared instance, not many independent instances.

The mental model:

```text
Factory:   choose the right object
Builder:   assemble a complex object
Singleton: reuse the one shared object
```

The most important caution:

> Singleton is useful when “only one” is a real rule, but dangerous when it becomes hidden global state.

In one sentence:

> Use Singleton when one shared object is part of the design, not merely because passing dependencies feels inconvenient.
