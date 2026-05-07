---
layout: default
title: "Exercise 1: Basic Decorator"
---

# Exercise 1: Basic Decorator

## The scenario

You are building a notification system. The core object is a `Notifier` that sends messages to users:

```python
class EmailNotifier(Notifier):
    def send(self, recipient: str, message: str) -> None:
        print(f"EMAIL to {recipient}: {message}")
```

The system works fine. But now two new requirements arrive:

- Every notification should be **logged** (print when it is sent and to whom).
- Some notifications should have their message **uppercased** before sending (for urgent alerts).

You must add these behaviours **without modifying `EmailNotifier`**.

---

## Your task

### Part A — add logging

Implement `LoggingDecorator`. It should:

- Print `"SENDING notification to {recipient}"` before the notification is sent.
- Print `"SENT notification to {recipient}"` after the notification is sent.
- Otherwise delegate to the wrapped notifier.

Expected output:

```
SENDING notification to alice@example.com
EMAIL to alice@example.com: Meeting at 3pm
SENT notification to alice@example.com
```

### Part B — add uppercasing

Implement `UppercaseDecorator`. It should:

- Convert `message` to uppercase before passing it to the wrapped notifier.
- Not change `recipient`.

Expected output when wrapping `EmailNotifier` directly:

```
EMAIL to bob@example.com: SERVER IS DOWN
```

### Part C — compose them

Wrap `EmailNotifier` with both decorators so that the message is uppercased **and** the send is logged.

Expected output:

```
SENDING notification to bob@example.com
EMAIL to bob@example.com: SERVER IS DOWN
SENT notification to bob@example.com
```

---

## Skeleton

See `exercise1.py`.

---

## What to focus on

- The decorator must implement the same interface as the object it wraps.
- The decorator receives the wrapped object in its constructor.
- Each decorator does exactly one thing.

---

[Solution](solution1.md) · [Exercise 2](exercise2.md)
