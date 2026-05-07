---
layout: default
title: "Solution 1: Basic Decorator"
---

# Solution 1: Basic Decorator

## Implementation

```python
class LoggingDecorator(Notifier):
    def __init__(self, wrapped: Notifier):
        self._wrapped = wrapped

    def send(self, recipient: str, message: str) -> None:
        print(f"SENDING notification to {recipient}")
        self._wrapped.send(recipient, message)
        print(f"SENT notification to {recipient}")


class UppercaseDecorator(Notifier):
    def __init__(self, wrapped: Notifier):
        self._wrapped = wrapped

    def send(self, recipient: str, message: str) -> None:
        self._wrapped.send(recipient, message.upper())
```

Composition:

```python
notifier = LoggingDecorator(UppercaseDecorator(EmailNotifier()))
notifier.send("bob@example.com", "server is down")
```

Output:

```
SENDING notification to bob@example.com
EMAIL to bob@example.com: SERVER IS DOWN
SENT notification to bob@example.com
```

---

## What makes this work

Every decorator:

1. Implements `Notifier` — so the caller never knows it is wrapped.
2. Receives the wrapped object in its constructor — so the chain can be any depth.
3. Calls `self._wrapped.send(...)` — so the real work still happens.
4. Only does one thing — `LoggingDecorator` only logs, `UppercaseDecorator` only transforms.

---

## The key structural insight

Notice that `UppercaseDecorator` wraps the *inner* object and `LoggingDecorator` wraps *that*:

```
LoggingDecorator
    └── UppercaseDecorator
            └── EmailNotifier
```

The call flows inward:

```
LoggingDecorator.send
    prints "SENDING..."
    calls UppercaseDecorator.send
        uppercases message
        calls EmailNotifier.send
            prints "EMAIL to..."
    prints "SENT..."
```

This is why the logged message is already uppercase in the output — uppercasing happens before the email is sent, and logging wraps the entire operation.

---

## Possible pitfall: forgetting to call `self._wrapped.send`

```python
class BrokenDecorator(Notifier):
    def __init__(self, wrapped: Notifier):
        self._wrapped = wrapped

    def send(self, recipient: str, message: str) -> None:
        print(f"SENDING to {recipient}")
        # forgot to call self._wrapped.send !
```

This decorator silently swallows the notification. The log appears but nothing is actually sent. Always call through to the wrapped object unless you have a deliberate reason not to (like a stub or a null object).

---

## Possible improvement: a shared decorator base

If you have many decorators, you can put the forwarding in a base class so each decorator only overrides what it changes:

```python
class NotifierDecorator(Notifier):
    def __init__(self, wrapped: Notifier):
        self._wrapped = wrapped

    def send(self, recipient: str, message: str) -> None:
        self._wrapped.send(recipient, message)


class LoggingDecorator(NotifierDecorator):
    def send(self, recipient: str, message: str) -> None:
        print(f"SENDING notification to {recipient}")
        super().send(recipient, message)
        print(f"SENT notification to {recipient}")
```

This is not required for this exercise, but becomes useful in exercise 2 when you have several decorators.

---

[Exercise 1](exercise1.md) · [Exercise 2](exercise2.md)
