---
layout: default
title: "Exercise 2: Multiple Decorators and Ordering"
---

# Exercise 2: Multiple Decorators and Ordering

## The scenario

The notification system from Exercise 1 has grown. There are now three notifier types:

```python
class EmailNotifier(Notifier):
    def send(self, recipient: str, message: str) -> None:
        print(f"EMAIL to {recipient}: {message}")

class SmsNotifier(Notifier):
    def send(self, recipient: str, message: str) -> None:
        print(f"SMS to {recipient}: {message[:160]}")  # SMS has a 160-char limit

class PushNotifier(Notifier):
    def send(self, recipient: str, message: str) -> None:
        print(f"PUSH to {recipient}: {message[:100]}")  # push has a 100-char limit
```

And four cross-cutting behaviours have been requested:

- **Logging** — log before and after each send (from Exercise 1).
- **Retry** — if the inner notifier raises an exception, retry up to N times before giving up.
- **Rate limiting** — track how many notifications have been sent; raise `RateLimitExceeded` if a per-instance limit is exceeded.
- **Prefix** — prepend a fixed string to every message (e.g. `"[URGENT] "` for critical alerts).

---

## Your task

### Part A — implement the four decorators

Implement `LoggingDecorator`, `RetryDecorator`, `RateLimitDecorator`, and `PrefixDecorator`.

`RetryDecorator` constructor:

```python
RetryDecorator(wrapped, max_retries=3)
```

It should print `"Retry {n}/{max_retries}..."` on each retry attempt.

`RateLimitDecorator` constructor:

```python
RateLimitDecorator(wrapped, limit=5)
```

It should raise `RateLimitExceeded` when the limit is reached.

`PrefixDecorator` constructor:

```python
PrefixDecorator(wrapped, prefix="[URGENT] ")
```

### Part B — ordering matters

Consider these two compositions and predict the output for each before running them:

```python
# Composition A
notifier_a = RateLimitDecorator(
    LoggingDecorator(EmailNotifier()),
    limit=5,
)

# Composition B
notifier_b = LoggingDecorator(
    RateLimitDecorator(EmailNotifier(), limit=5)
)
```

Call `notifier_a.send("alice@example.com", "hello")` six times on composition A, then the same on composition B.

Answer these questions:

1. In which composition does logging still happen when the rate limit is exceeded?
2. Why?
3. Which composition would you use if you wanted to audit every *attempted* send, including ones that were blocked?
4. Which would you use if you only wanted to log sends that actually went through?

### Part C — a real-world composition

Build a notifier for a production alert system with these requirements:

- Uses `EmailNotifier`.
- Prepends `"[ALERT] "` to every message.
- Retries up to 2 times on failure.
- Logs all send attempts.
- Enforces a rate limit of 10 alerts per instance.

Write the composition and explain why you chose the order you did.

---

## Skeleton

See `exercise2.py`.

---

## What to focus on

- Each decorator still does exactly one thing.
- Decorator order is not arbitrary — it determines what each layer sees and when.
- The outermost decorator acts first on the way in and last on the way out.

---

[Exercise 1](exercise1.md) · [Solution 2](solution2.md) · [Exercise 3](exercise3.md)
