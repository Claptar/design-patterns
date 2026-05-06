---
layout: default
title: "Singleton as Metaclass"
---

# Singleton as Metaclass

## 1. What problem are we trying to solve?

A singleton decorator gives us reusable Singleton behavior:

```python
@singleton
class Settings:
    ...
```

But the simple decorator version has a downside:

> It replaces the class name with a wrapper function.

That can make this awkward:

```python
isinstance(settings, Settings)
```

It can also be less natural when we care about subclassing, type checkers, or library-style APIs.

So the problem is:

> How do we control instance creation while keeping the class as a real class?

A metaclass gives us a more advanced Python answer.

The key idea is:

> Do not replace the class. Change the class's creation behavior.

---

## 2. Concept introduction

A **metaclass** controls how classes behave.

Most Python classes are instances of `type`.

For example:

```python
class Settings:
    pass
```

Conceptually:

```text
Settings is an object too.
The object called Settings is an instance of type.
```

So this is true:

```python
print(type(Settings))  # <class 'type'>
```

A metaclass lets us customize what happens when the class object itself is called:

```python
Settings()
```

So Singleton as a metaclass means:

> Instead of replacing the class with a wrapper function, customize what happens when the class is called.

The class remains a real class.

---

## 3. Regular classes use `metaclass=type`

When you write this:

```python
class Settings:
    pass
```

Python behaves roughly as if you wrote this:

```python
class Settings(metaclass=type):
    pass
```

The second version is rarely written because `type` is the default metaclass.

So a normal class has this relationship:

```text
settings instance  --is instance of-->  Settings
Settings class     --is instance of-->  type
```

In code:

```python
class Settings:
    pass

settings = Settings()

print(type(settings))  # <class '__main__.Settings'>
print(type(Settings))  # <class 'type'>
```

This is the important mental shift:

> Instances are created from classes, but classes themselves are also objects created from metaclasses.

So there are two levels:

```text
metaclass -> class -> instance
```

For a normal class:

```text
type -> Settings -> settings
```

---

## 4. What happens with regular `type`?

Suppose we have this normal class:

```python
class Settings:
    def __new__(cls, environment: str):
        print("Settings.__new__")
        return super().__new__(cls)

    def __init__(self, environment: str):
        print("Settings.__init__")
        self.environment = environment
```

When we call it:

```python
settings1 = Settings("development")
settings2 = Settings("production")
```

Python calls the metaclass's `__call__` method.

Because the metaclass is `type`, the call goes through:

```python
type.__call__(Settings, "development")
```

`type.__call__` roughly does this:

```text
1. call Settings.__new__(Settings, ...)
2. call Settings.__init__(new_object, ...)
3. return the new object
```

So the normal flow is:

```text
Settings("development")
    |
    v
type.__call__(Settings, "development")
    |
    v
Settings.__new__(Settings, "development")
    |
    v
Settings.__init__(new_object, "development")
    |
    v
return new_object
```

When we call the class a second time:

```python
settings2 = Settings("production")
```

`type.__call__` repeats the same process.

That means:

```text
new call -> new object -> __init__ runs again
```

So this is false for a regular class:

```python
settings1 is settings2  # False
```

A regular class call means:

> Create a fresh instance.

---

## 5. The idea: change the class-call doorway

From the previous section, a regular class call goes through this doorway:

```python
type.__call__(Settings, "development")
```

That default doorway means:

```text
Always create a fresh Settings object.
```

For Singleton behavior, we want to change that doorway so it means:

```text
If Settings has no instance yet, create one normally.
If Settings already has an instance, return the existing one.
```

In other words, we want this idea:

```text
Settings("development")
    -> singleton-aware class-call behavior
    -> one shared Settings object
```

But we should not try to modify Python's built-in `type.__call__` directly.

Instead, we create our own metaclass that inherits from `type` and overrides `__call__`.

```python
class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)

        return cls._instances[cls]
```

Now we tell `Settings` to use this metaclass:

```python
class Settings(metaclass=SingletonMeta):
    def __init__(self, environment: str):
        self.environment = environment
```

That one line changes the class-call doorway.

With a regular class:

```text
Settings(...) -> type.__call__(Settings, ...)
```

With a singleton metaclass:

```text
Settings(...) -> SingletonMeta.__call__(Settings, ...)
```

That is the core mechanism.

Singleton as a metaclass is not mainly changing the class body.
It is changing the method that controls what happens when the class is called.

---

## 6. What changed in the relationship?

With a regular class, the relationship is:

```text
type -> Settings -> settings instance
```

In code:

```python
class Settings:
    pass

settings = Settings()

print(type(settings))  # <class '__main__.Settings'>
print(type(Settings))  # <class 'type'>
```

With a singleton metaclass, the relationship is:

```text
SingletonMeta -> Settings -> settings instance
```

In code:

```python
class Settings(metaclass=SingletonMeta):
    pass

settings = Settings()

print(type(settings))  # <class '__main__.Settings'>
print(type(Settings))  # <class '__main__.SingletonMeta'>
```

The instance is still a `Settings` instance.

So this still works:

```python
isinstance(settings, Settings)  # True
```

The difference is one level above the class:

```text
Settings class --is instance of--> SingletonMeta
```

instead of:

```text
Settings class --is instance of--> type
```

And because `SingletonMeta` is a subclass of `type`, `Settings` is still a normal class-like object.
It just has customized call behavior.

---

## 7. What does `SingletonMeta.__call__` do?

Here is the implementation again:

```python
class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)

        return cls._instances[cls]
```

The important method is:

```python
def __call__(cls, *args, **kwargs):
    ...
```

Here, `cls` is the class being called.

So when we write:

```python
Settings("development")
```

Python routes the call to:

```python
SingletonMeta.__call__(Settings, "development")
```

Inside `__call__`, `cls` is:

```python
Settings
```

So this line:

```python
if cls not in cls._instances:
```

means:

```text
Have we already created the singleton instance for Settings?
```

The cache is a dictionary:

```python
_instances = {}
```

The key is the class:

```python
Settings
```

The value is the one shared instance of that class:

```python
settings1
```

After the first call, the cache is conceptually:

```python
{
    Settings: settings1
}
```

That is why the same `SingletonMeta` can support many singleton classes.
Each class gets its own entry in the dictionary.

---

## 8. How does it still create the object normally the first time?

This line matters:

```python
cls._instances[cls] = super().__call__(*args, **kwargs)
```

Since `SingletonMeta` inherits from `type`, this:

```python
super().__call__(*args, **kwargs)
```

means:

```text
Use the normal type.__call__ behavior.
```

So the singleton metaclass is not manually building the object from scratch.
It says:

> If this class has no cached instance yet, use normal Python object creation, then store the result.

The first call looks like this:

```text
Settings("development")
    |
    v
SingletonMeta.__call__(Settings, "development")
    |
    v
No cached Settings instance exists
    |
    v
super().__call__("development")
    |
    v
type.__call__(Settings, "development")
    |
    v
Settings.__new__(Settings, "development")
    |
    v
Settings.__init__(new_object, "development")
    |
    v
cache and return new_object
```

The second call looks like this:

```text
Settings("production")
    |
    v
SingletonMeta.__call__(Settings, "production")
    |
    v
Cached Settings instance already exists
    |
    v
return cached Settings object
```

On the second call, this does not happen again:

```text
Settings.__new__
Settings.__init__
```

That is why this prints `development`, not `production`:

```python
settings1 = Settings("development")
settings2 = Settings("production")

print(settings2.environment)  # development
```

The first call creates and initializes the object.
Later calls only retrieve it.

---

## 9. Side-by-side: `type` versus `SingletonMeta`

### Regular class

```python
class Settings(metaclass=type):
    def __init__(self, environment: str):
        self.environment = environment
```

Call flow:

```text
Settings("development")
    -> type.__call__
    -> Settings.__new__
    -> Settings.__init__
    -> new Settings object

Settings("production")
    -> type.__call__
    -> Settings.__new__
    -> Settings.__init__
    -> another new Settings object
```

Result:

```python
settings1 is settings2  # False
```

### Singleton class

```python
class Settings(metaclass=SingletonMeta):
    def __init__(self, environment: str):
        self.environment = environment
```

Call flow:

```text
Settings("development")
    -> SingletonMeta.__call__
    -> no cached Settings instance
    -> type.__call__
    -> Settings.__new__
    -> Settings.__init__
    -> cache and return new Settings object

Settings("production")
    -> SingletonMeta.__call__
    -> cached Settings instance exists
    -> return cached Settings object
```

Result:

```python
settings1 is settings2  # True
```

The difference is not inside `Settings.__init__`.

The difference is one level above it:

```text
the metaclass controls what calling Settings means
```

---

## 10. Trace example with print statements

This example makes the difference visible.

### Regular class

```python
class RegularSettings:
    def __new__(cls, environment: str):
        print("RegularSettings.__new__")
        return super().__new__(cls)

    def __init__(self, environment: str):
        print("RegularSettings.__init__")
        self.environment = environment


regular1 = RegularSettings("development")
regular2 = RegularSettings("production")

print(regular1 is regular2)
```

Output:

```text
RegularSettings.__new__
RegularSettings.__init__
RegularSettings.__new__
RegularSettings.__init__
False
```

Each call creates and initializes a new object.

### Singleton metaclass

```python
class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        print(f"SingletonMeta.__call__ for {cls.__name__}")

        if cls not in cls._instances:
            print("creating new instance")
            cls._instances[cls] = super().__call__(*args, **kwargs)
        else:
            print("returning cached instance")

        return cls._instances[cls]


class SingletonSettings(metaclass=SingletonMeta):
    def __new__(cls, environment: str):
        print("SingletonSettings.__new__")
        return super().__new__(cls)

    def __init__(self, environment: str):
        print("SingletonSettings.__init__")
        self.environment = environment


singleton1 = SingletonSettings("development")
singleton2 = SingletonSettings("production")

print(singleton1 is singleton2)
print(singleton2.environment)
```

Output:

```text
SingletonMeta.__call__ for SingletonSettings
creating new instance
SingletonSettings.__new__
SingletonSettings.__init__
SingletonMeta.__call__ for SingletonSettings
returning cached instance
True
development
```

Notice the second call:

```text
SingletonSettings.__new__
SingletonSettings.__init__
```

are not printed again.

That is the concrete effect of overriding the metaclass `__call__` method.

---

## 11. What changes, exactly?

Here is the most important comparison.

| Part | Regular `metaclass=type` | `metaclass=SingletonMeta` |
|---|---|---|
| Class object | Created as an instance of `type` | Created as an instance of `SingletonMeta` |
| Class body | Normal | Normal |
| Instance type | `Settings` | `Settings` |
| `isinstance(obj, Settings)` | Works | Works |
| Call target | `type.__call__` | `SingletonMeta.__call__` |
| First call | Creates a new object | Creates, caches, and returns a new object |
| Later calls | Create new objects | Return cached object |
| Does `__init__` run every call? | Yes | No, only when a new instance is created |
| Where is the cache? | No cache | On the metaclass, usually `_instances` |

The class itself stays ordinary from the user's perspective:

```python
settings = Settings("development")
settings.environment
isinstance(settings, Settings)
```

The special behavior lives above the class:

```text
SingletonMeta.__call__
```

---

## 12. Why not just put Singleton logic in `Settings.__new__`?

You can implement Singleton directly in the class:

```python
class Settings:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance
```

This works for one class.

But if many classes need the same behavior, you may duplicate the logic:

```text
Settings
PluginRegistry
CommandRegistry
MetricsRegistry
```

The metaclass moves that creation rule into one reusable place:

```python
class SingletonMeta(type):
    ...
```

Then each class opts in:

```python
class Settings(metaclass=SingletonMeta):
    ...

class PluginRegistry(metaclass=SingletonMeta):
    ...
```

So the metaclass version is useful when Singleton behavior is a reusable class-level policy.

---

## 13. Natural example: plugin registry

Suppose an application has a plugin registry.

Different parts of the app need to register and retrieve plugins:

```text
auth plugins
payment plugins
export plugins
notification plugins
```

You want one shared registry.

```python
class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)

        return cls._instances[cls]
```

Now the registry can use the metaclass:

```python
class PluginRegistry(metaclass=SingletonMeta):
    def __init__(self):
        self._plugins = {}

    def register(self, name: str, plugin):
        self._plugins[name] = plugin

    def get(self, name: str):
        return self._plugins[name]
```

Usage:

```python
plugins1 = PluginRegistry()
plugins2 = PluginRegistry()

plugins1.register("csv_export", object())

print(plugins1 is plugins2)
print(plugins2.get("csv_export"))
```

Output:

```text
True
<object object at ...>
```

Both variables point to the same registry.

This is natural because the registry represents one shared application-wide collection.

---

## 14. Multiple singleton classes

The metaclass approach becomes more useful when several classes need the same Singleton behavior.

```python
class PluginRegistry(metaclass=SingletonMeta):
    def __init__(self):
        self._plugins = {}


class CommandRegistry(metaclass=SingletonMeta):
    def __init__(self):
        self._commands = {}
```

Usage:

```python
plugins1 = PluginRegistry()
plugins2 = PluginRegistry()

commands1 = CommandRegistry()
commands2 = CommandRegistry()

print(plugins1 is plugins2)    # True
print(commands1 is commands2)  # True
print(plugins1 is commands1)   # False
```

Important detail:

```text
Each class gets its own singleton instance.
```

Why?

Because the cache uses the class as the key:

```python
_instances[PluginRegistry]
_instances[CommandRegistry]
```

So `PluginRegistry` has one instance.

`CommandRegistry` has one instance.

They do not share the same object.

---

## 15. A subtle constructor issue: first arguments win

With a singleton metaclass, the first call creates the object.

Later calls ignore their arguments because they do not create a new object.

```python
settings1 = Settings("development")
settings2 = Settings("production")

print(settings2.environment)  # development
```

That can be surprising.

So singleton classes should usually avoid meaningful repeated constructor arguments.

Prefer one of these designs:

### Option 1: no constructor arguments

```python
class Settings(metaclass=SingletonMeta):
    def __init__(self):
        self.environment = load_environment()
```

### Option 2: explicit configuration method

```python
class Settings(metaclass=SingletonMeta):
    def configure(self, environment: str):
        self.environment = environment
```

### Option 3: fail if later calls pass different arguments

For stricter systems, the metaclass can remember the first arguments and reject conflicting later calls.

But that adds complexity, so use it only if the problem needs it.

---

## 16. Thread-safe metaclass version

In real backend code, two threads might try to create the singleton at the same time.

A safer version uses a lock:

```python
from threading import Lock


class SingletonMeta(type):
    _instances = {}
    _lock = Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)

        return cls._instances[cls]
```

This protects the first creation step.

The double check matters:

```text
First check: avoid locking after the instance already exists.
Second check: avoid creating twice if two threads waited for the same lock.
```

For teaching, the minimal version is easier.

For production, think about concurrency.

---

## 17. Metaclass versus decorator

| Question | Singleton as decorator | Singleton as metaclass |
|---|---|---|
| Where is the logic? | In a function that wraps the class | In a metaclass controlling class calls |
| Is it easy to understand? | Easier | Harder |
| Does the class remain a real class? | Not in the simple version | Yes |
| Does `isinstance(obj, Class)` work? | Usually not with the simple version | Yes |
| Good for one-off use? | Yes | Maybe too much |
| Good for many singleton classes? | Okay | Better |
| Supports inheritance more naturally? | No | Yes |
| Main risk | Replaces class with function | Adds metaclass complexity |

The decorator is simpler.

The metaclass is more powerful.

The key distinction:

```text
Decorator changes what the class name points to.
Metaclass changes how the class object behaves.
```

---

## 18. Connection to earlier concepts

### Connection to creational patterns

Singleton is a creational pattern because it controls object creation.

The metaclass version controls creation at the class-call level:

```python
Settings()
```

Instead of allowing every call to create a fresh object, it returns the cached object after the first call.

### Connection to Factory

A factory centralizes object creation decisions.

A singleton metaclass also centralizes object creation behavior, but the question is different:

| Pattern | Main question |
|---|---|
| Factory | Which object should I create? |
| Singleton metaclass | Should this class create a new object or reuse its existing one? |

Factory is about choosing between alternatives.

Singleton is about preserving one identity.

### Connection to Builder

Builder handles construction steps, validation, defaults, and assembly.

Singleton metaclass does not organize construction steps.

It controls repeated construction attempts.

```text
Builder: make object construction readable and safe.
Singleton metaclass: prevent repeated construction from creating multiple instances.
```

### Connection to SOLID

Singleton can make dependencies hidden.

This is convenient:

```python
class OrderService:
    def place_order(self, order):
        registry = PluginRegistry()
```

But the service now reaches directly into a global object.

A more testable design is often:

```python
class OrderService:
    def __init__(self, plugin_registry):
        self.plugin_registry = plugin_registry
```

The application can still pass the singleton registry in production.

The difference is that `OrderService` no longer controls how the registry is obtained.

---

## 19. When to use singleton as metaclass

Use the metaclass version when:

```text
you want reusable Singleton behavior across several classes
the class should remain a real class
isinstance checks should keep working
subclasses should inherit the behavior
you are comfortable with metaclasses
```

Good example:

```python
class Registry(metaclass=SingletonMeta):
    ...
```

This is useful when Singleton behavior is part of a reusable class pattern.

---

## 20. When not to use singleton as metaclass

Avoid the metaclass version when:

```text
the team is not comfortable with metaclasses
a module-level object would be clearer
dependency injection would solve the problem
you only need one simple singleton
the extra abstraction makes the code harder to read
```

Metaclasses are powerful, but they are not casual tools.

If the reader has to stop and ask, "Why is there a metaclass here?", the design should be worth that extra complexity.

---

## 21. Practical rule of thumb

Ask:

> Do I need the class to remain a proper class?

Use a metaclass instead of the simple decorator.

Ask:

> Do many classes need the same Singleton creation rule?

A metaclass is a good fit.

Ask:

> Is this just one shared object in one module?

Prefer a module-level object.

Ask:

> Am I using Singleton just to avoid passing dependencies around?

Prefer dependency injection.

Ask:

> Do constructor arguments matter after the first call?

Be careful. With the simple singleton metaclass, only the first constructor call actually initializes the object.

---

## 22. Summary and mental model

Singleton as a metaclass means:

> Keep the class as a class, but control what happens when the class is called.

The normal model is:

```text
type -> Settings -> settings instance
```

The singleton metaclass model is:

```text
SingletonMeta -> Settings -> one shared settings instance
```

The mental model:

```text
Regular metaclass=type:
    Settings(...) means create a new Settings object.

metaclass=SingletonMeta:
    Settings(...) means ask SingletonMeta for the Settings object.
    If it does not exist, create it normally and cache it.
    If it already exists, return the cached one.
```

In one sentence:

> Singleton as a metaclass is the more powerful class-creation approach: harder to teach, but better when the class must remain a real class and several classes need the same Singleton behavior.

---

[Singleton as Decorator](singleton_as_decorator.md)
