---
layout: default
title: "Exercise 2: Method Chain — Suppress and Flexible Pipelines"
---

# Exercise 2: Method Chain — Suppress and Flexible Pipelines

## Context

We continue with the logging pipeline from Exercise 1. The base code — `LogLevel`, `LogMessage`, `LogHandler`, and the four concrete handlers — is already in place.

This exercise adds two important real-world requirements.

---

## Part A — SuppressHandler

Add a `SuppressHandler` that **silently drops** any message at or below a configurable level, without passing it along.

```python
suppress = SuppressHandler(suppress_up_to=LogLevel.INFO)
```

This handler swallows `DEBUG` and `INFO` messages completely. `WARNING` and `ERROR` pass through to the next handler.

Wire the chain so that suppression happens first:

```python
chain = suppress.set_next(warning).set_next(error)
```

Then verify:

```python
chain.handle(LogMessage(LogLevel.DEBUG,   "ignored"))    # no output
chain.handle(LogMessage(LogLevel.INFO,    "ignored"))    # no output
chain.handle(LogMessage(LogLevel.WARNING, "printed"))    # printed
chain.handle(LogMessage(LogLevel.ERROR,   "printed"))    # printed
```

---

## Part B — FallbackHandler

Add a `FallbackHandler` that catches **any message that no earlier handler processed**. It should print a generic line so that nothing is silently dropped by accident.

```python
fallback = FallbackHandler()
```

Place it at the end of any chain. If a message reaches it, it prints:

```text
[FALLBACK] WARNING: disk usage at 80%
```

Wire a chain that has no `WarningHandler` and verify that a `WARNING` message reaches the fallback.

---

## Part C — building different pipelines from the same handlers

Using only the handlers from Exercise 1 and this exercise, build two different pipelines from the same set of handler objects and verify they behave independently:

**Production pipeline** — suppress debug, pass everything else through:

```python
production = SuppressHandler(LogLevel.DEBUG)
production.set_next(InfoHandler()).set_next(WarningHandler()).set_next(ErrorHandler())
```

**Development pipeline** — everything goes through, with a fallback at the end:

```python
dev = DebugHandler()
dev.set_next(InfoHandler()).set_next(WarningHandler()).set_next(ErrorHandler()).set_next(FallbackHandler())
```

Send the same set of messages to both and observe the difference in output.

---

## Skeleton

See `exercise2.py`.

---

## Hints

- `SuppressHandler` should check `message.level.value <= self._suppress_up_to.value`. If true, return without calling `_pass_along`. If false, call `_pass_along`.
- `FallbackHandler` processes every message that reaches it — there's no level check. It is always the last handler so it has no next.
- Nothing in `LogHandler` needs to change. `SuppressHandler` and `FallbackHandler` are just two more concrete subclasses.
- Two pipelines are just two separate chains wired from separate handler instances. Handler instances are not shared between chains.

---

[Exercise 1](exercise1.md) · [Solution 2](solution2.md) · [Exercise 3](exercise3.md)
