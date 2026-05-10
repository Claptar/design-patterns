---
layout: default
title: "Solution 1: Method Chain — Logging Pipeline"
---

# Solution 1: Method Chain — Logging Pipeline

## Part A solution

The key decisions:

**`set_next` returns its argument**, not `self`. This is what enables fluent wiring:

```python
def set_next(self, handler: LogHandler) -> LogHandler:
    self._next = handler
    return handler
```

So `debug.set_next(info).set_next(warning)` works because each call returns the handler just stored, and the *next* `set_next` is called on that. If `set_next` returned `self` instead, the whole chain would stay wired to `debug`.

**Each concrete handler checks its own level first**, then passes along:

```python
class InfoHandler(LogHandler):
    def handle(self, message: LogMessage) -> None:
        if message.level == LogLevel.INFO:
            print(f"[INFO]  {message.text}")
        else:
            self._pass_along(message)
```

**`_pass_along` guards against `None`**:

```python
def _pass_along(self, message: LogMessage) -> None:
    if self._next is not None:
        self._next.handle(message)
```

This is what makes the end of the chain safe — the last handler calls `_pass_along`, which does nothing because `_next` is `None`.

---

## Part B solution

The simplest approach is to print the trace line inside each handler before the if/else decision. A cleaner reuse is to put the "passing along" trace inside `_pass_along` in a shared base, since passing along always goes through that method:

```python
def _pass_along(self, message: LogMessage) -> None:
    if self._next is not None:
        print(f"  [{self.name}] received {message.level.name} — passing along")
        self._next.handle(message)
```

And each handler prints the "processing" trace before doing its work.

For a `WARNING` message the trace would look like:

```text
  [DebugHandler] received WARNING — passing along
  [InfoHandler] received WARNING — passing along
  [WarningHandler] received WARNING — processing
[WARN]  disk usage at 80%
```

This makes the chain's traversal completely visible, which is very useful for debugging.

---

## Discussion and pitfalls

**The `None` guard is essential.** If you forget it, the last handler in the chain will raise `AttributeError: 'NoneType' object has no attribute 'handle'` on any message it doesn't process. This is one of the most common method chain bugs.

**Handler order matters.** The chain is traversed in the order it was wired. If you put `ErrorHandler` before `DebugHandler`, debug messages will travel all the way to the end unnecessarily. For a logging pipeline, the natural order (debug → info → warning → error) is also the most efficient.

**One handler, one message.** Each message is processed by exactly one handler. This is the core invariant of the method chain variant. The next exercise breaks this invariant deliberately to show why sometimes you want it and sometimes you don't.

**Possible improvement — threshold-based handler.** Instead of four separate handler classes you could write one:

```python
class ThresholdHandler(LogHandler):
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

This is cleaner when all handlers share the same structure and differ only in their level. The four concrete classes are easier to understand as a first implementation, but `ThresholdHandler` is what you'd likely write in production.

---

[Exercise 1](exercise1.md) · [Exercise 2](exercise2.md)
