---
layout: default
title: "Solution 2: Suppress and Flexible Pipelines"
---

# Solution 2: Suppress and Flexible Pipelines

## Part A — SuppressHandler

The implementation is a single level comparison:

```python
class SuppressHandler(LogHandler):
    def __init__(self, suppress_up_to: LogLevel):
        super().__init__("SuppressHandler")
        self._suppress_up_to = suppress_up_to

    def handle(self, message: LogMessage) -> None:
        if message.level.value <= self._suppress_up_to.value:
            return          # silently drop — no _pass_along
        self._pass_along(message)
```

The critical detail is `.value`. `LogLevel.DEBUG <= LogLevel.INFO` doesn't work in Python enums by default — enums don't define ordering by their values unless you use `IntEnum` or implement `__lt__`. Comparing `.value` (the underlying integer) is the safest explicit approach.

Alternatively, using `IntEnum` lets you compare directly:

```python
class LogLevel(IntEnum):
    DEBUG   = 1
    INFO    = 2
    WARNING = 3
    ERROR   = 4
```

Then `message.level <= self._suppress_up_to` works. This is often the cleaner choice for ordered enums.

---

## Part B — FallbackHandler

```python
class FallbackHandler(LogHandler):
    def __init__(self):
        super().__init__("FallbackHandler")

    def handle(self, message: LogMessage) -> None:
        print(f"[FALLBACK] {message.level.name}: {message.text}")
```

Notice it never calls `_pass_along`. A `FallbackHandler` is always placed last and unconditionally handles whatever arrives. It would be incorrect to pass along from here — there is nothing further, and the handler's whole purpose is to catch what would otherwise be silently lost.

---

## Part C — two independent pipelines

The key insight from Part C is that **a chain is just a set of connected handler instances**. Two chains are just two separate sets of instances. There is no shared state between them — each instance has its own `_next` pointer.

This means:

```python
# These two InfoHandlers are completely independent objects
prod = SuppressHandler(LogLevel.DEBUG)
prod.set_next(InfoHandler()).set_next(WarningHandler())

dev = DebugHandler()
dev.set_next(InfoHandler()).set_next(WarningHandler()).set_next(FallbackHandler())
```

Wiring one does not affect the other. The same handler *class* is reused, but different *instances* are created.

---

## Discussion and pitfalls

**`SuppressHandler` before or after other handlers?**

Placing suppress first is the most common approach — you filter early and cheaply. But you could also place it later if you want some handlers to always run regardless of level (e.g. an audit logger). The chain's power is precisely that you can reorder it without changing any handler.

**`FallbackHandler` is the method chain's equivalent of a default branch.**

In an `if/elif` chain, a trailing `else` is a fallback. In a method chain, `FallbackHandler` at the end plays the same role. Both prevent silent drops. The difference is that the method chain version is optional and composable — you add it only to chains where you want it.

**Suppress vs filter — a naming thought.**

`SuppressHandler` drops messages silently. A `FilterHandler` could instead *keep* only certain levels and drop others — the inverse. Both are valid; the distinction matters when documenting behavior for teammates.

**Possible improvement — configurable handler.**

Rather than four concrete handler classes plus `SuppressHandler`, consider a single configurable handler:

```python
class LevelHandler(LogHandler):
    def __init__(self, level: LogLevel, prefix: str):
        super().__init__(f"{level.name}Handler")
        self._level = level
        self._prefix = prefix

    def handle(self, message: LogMessage) -> None:
        if message.level == self._level:
            print(f"[{self._prefix}] {message.text}")
        else:
            self._pass_along(message)
```

This reduces four classes to one. The tradeoff is slightly less explicit class names in stack traces.

---

[Exercise 2](exercise2.md) · [Exercise 3](exercise3.md)
