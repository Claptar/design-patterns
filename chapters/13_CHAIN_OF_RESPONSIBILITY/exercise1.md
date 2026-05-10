---
layout: default
title: "Exercise 1: Method Chain — Logging Pipeline"
---

# Exercise 1: Method Chain — Logging Pipeline

## Goal

Build a logging pipeline using the Chain of Responsibility method chain pattern.

A log message has a **level**:

```text
DEBUG = 1
INFO  = 2
WARNING = 3
ERROR = 4
```

A handler is configured with a **minimum level**. When a message arrives, the handler processes it if the message level is exactly its own level, and passes it along otherwise. At the end of the chain, unhandled messages are silently dropped.

---

## Part A — build the chain

Implement:

- A `LogLevel` enum with `DEBUG`, `INFO`, `WARNING`, `ERROR`.
- A `LogMessage` dataclass with `level: LogLevel` and `text: str`.
- An abstract `LogHandler` base class with:
  - `set_next(handler) -> LogHandler` — wires the chain, returns the handler passed in.
  - `handle(message: LogMessage) -> None` — processes or passes along.
- Three concrete handlers: `DebugHandler`, `InfoHandler`, `WarningHandler`, `ErrorHandler` — each prints a formatted line when it processes a message.

Wire them and verify the output matches the expected section below.

---

## Part B — trace the chain

Add a `name` attribute to the base handler. Before each handler either processes or passes a message, print a trace line:

```text
[DebugHandler] received DEBUG — processing
[DebugHandler] received INFO — passing along
[InfoHandler] received INFO — processing
```

This makes the chain's decision-making visible. Run the same messages from Part A with tracing on.

---

## Expected output (Part A, no tracing)

```text
[DEBUG] hello from debug
[INFO]  user logged in
[WARN]  disk usage at 80%
[ERROR] database connection failed
```

---

## Skeleton

See `exercise1.py`.

---

## Hints

- `set_next` should store the next handler and return it — this enables the fluent wiring style:
  `debug.set_next(info).set_next(warning).set_next(error)`.
- The base `handle` method should call `self._next.handle(message)` if `self._next` is not `None`.
- Each concrete handler should override `handle`, check if the message is "theirs", process or pass.
- In Part B, print the trace line inside `handle` *before* deciding what to do.

---

[Back to notes](chain_of_responsibility_method_chain.md) · [Exercise 2](exercise2.md)
