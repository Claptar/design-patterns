---
layout: default
title: "Exercise 3: Transparent Decorator"
---

# Exercise 3: Transparent Decorator

## The scenario

The notification system has matured. `EmailNotifier` has grown a richer interface beyond
just `send`:

```python
class EmailNotifier(Notifier):
    def send(self, recipient: str, message: str) -> None:
        print(f"EMAIL to {recipient}: {message}")

    def set_from_address(self, address: str) -> None:
        self._from = address
        print(f"From address set to {address}")

    def set_reply_to(self, address: str) -> None:
        self._reply_to = address
        print(f"Reply-to set to {address}")

    def get_sent_count(self) -> int:
        return self._sent_count

    def flush_queue(self) -> None:
        print("Queue flushed")
```

The team uses these methods throughout the codebase:

```python
notifier = EmailNotifier()
notifier.set_from_address("alerts@company.com")
notifier.set_reply_to("noreply@company.com")
notifier.send("alice@example.com", "hello")
print(notifier.get_sent_count())
notifier.flush_queue()
```

Now you wrap `EmailNotifier` with `LoggingDecorator` from Exercise 1:

```python
notifier = LoggingDecorator(EmailNotifier())
notifier.set_from_address("alerts@company.com")  # AttributeError!
```

The decorator only exposes `send`. Everything else is gone.

---

## Your task

### Part A — discover the problem

Run the provided `test_type_erosion` function and observe the `AttributeError`.

Read the error carefully. Make sure you understand *why* it happens before moving on.

### Part B — the wrong fix

A colleague suggests the quick fix: add forwarding methods to `LoggingDecorator`.

```python
class LoggingDecorator(Notifier):
    ...
    def set_from_address(self, address: str) -> None:
        self._wrapped.set_from_address(address)

    def set_reply_to(self, address: str) -> None:
        self._wrapped.set_reply_to(address)

    # ... and so on
```

Implement this version. Then answer:

1. How many methods did you have to add?
2. What happens if `EmailNotifier` gets a new method `set_bcc` next week?
3. What if you have five decorators, not one?

### Part C — the right fix

Rewrite `NotifierDecorator` (the shared base from Exercise 2) to use `__getattr__` forwarding.

After your fix, this should work without any changes to `LoggingDecorator`:

```python
notifier = LoggingDecorator(EmailNotifier())
notifier.set_from_address("alerts@company.com")   # forwards to EmailNotifier
notifier.set_reply_to("noreply@company.com")       # forwards to EmailNotifier
notifier.send("alice@example.com", "hello")        # intercepted by LoggingDecorator
notifier.flush_queue()                             # forwards to EmailNotifier
```

### Part D — stacked decorators

Verify that `__getattr__` forwarding works through a full decorator stack, not just one layer.

```python
notifier = LoggingDecorator(
    RateLimitDecorator(
        PrefixDecorator(EmailNotifier(), prefix="[ALERT] "),
        limit=10,
    )
)

notifier.set_from_address("alerts@company.com")
notifier.send("alice@example.com", "disk at 95%")
notifier.get_sent_count()
```

Make sure all three calls work correctly.

### Part E — the limitation

Add a type hint to a function that only accepts `EmailNotifier`:

```python
def configure_notifier(notifier: EmailNotifier) -> None:
    notifier.set_from_address("alerts@company.com")
    notifier.set_reply_to("noreply@company.com")
```

Now call it with a decorated notifier:

```python
configure_notifier(LoggingDecorator(EmailNotifier()))
```

Does it work at runtime? What does a type checker say? What is the trade-off?

---

## Skeleton

See `exercise3.py`.

---

## What to focus on

- Understanding *why* type erosion happens — what Python is actually looking up.
- The difference between `__getattr__` (fallback) and `__getattribute__` (always fires).
- Why a single `__getattr__` in the base replaces N forwarding methods across all decorators.
- The runtime vs. static type checking trade-off.

---

[Exercise 2](exercise2.md) · [Solution 3](solution3.md)
