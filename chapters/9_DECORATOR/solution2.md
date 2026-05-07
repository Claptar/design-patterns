---
layout: default
title: "Solution 2: Multiple Decorators and Ordering"
---

# Solution 2: Multiple Decorators and Ordering

## Implementation

```python
class LoggingDecorator(NotifierDecorator):
    def send(self, recipient: str, message: str) -> None:
        print(f"SENDING notification to {recipient}")
        self._wrapped.send(recipient, message)
        print(f"SENT notification to {recipient}")


class RetryDecorator(NotifierDecorator):
    def __init__(self, wrapped: Notifier, max_retries: int = 3):
        super().__init__(wrapped)
        self._max_retries = max_retries

    def send(self, recipient: str, message: str) -> None:
        last_error = None

        for attempt in range(1, self._max_retries + 1):
            try:
                self._wrapped.send(recipient, message)
                return
            except Exception as e:
                last_error = e
                if attempt < self._max_retries:
                    print(f"Retry {attempt}/{self._max_retries}...")

        raise last_error


class RateLimitDecorator(NotifierDecorator):
    def __init__(self, wrapped: Notifier, limit: int = 5):
        super().__init__(wrapped)
        self._limit = limit
        self._count = 0

    def send(self, recipient: str, message: str) -> None:
        if self._count >= self._limit:
            raise RateLimitExceeded(
                f"Rate limit of {self._limit} notifications exceeded"
            )
        self._count += 1
        self._wrapped.send(recipient, message)


class PrefixDecorator(NotifierDecorator):
    def __init__(self, wrapped: Notifier, prefix: str = "[URGENT] "):
        super().__init__(wrapped)
        self._prefix = prefix

    def send(self, recipient: str, message: str) -> None:
        self._wrapped.send(recipient, f"{self._prefix}{message}")
```

---

## Part B answer: ordering matters

```python
# Composition A: RateLimitDecorator is outermost
notifier_a = RateLimitDecorator(LoggingDecorator(EmailNotifier()), limit=2)

# Composition B: LoggingDecorator is outermost
notifier_b = LoggingDecorator(RateLimitDecorator(EmailNotifier(), limit=2))
```

Output for composition A (rate limit outside):

```
EMAIL to alice@example.com: message 1
EMAIL to alice@example.com: message 2
Blocked: Rate limit of 2 notifications exceeded
```

No logging at all — the rate limit check happens before `LoggingDecorator` ever gets a call.

Output for composition B (logging outside):

```
SENDING notification to alice@example.com
EMAIL to alice@example.com: message 1
SENT notification to alice@example.com
SENDING notification to alice@example.com
EMAIL to alice@example.com: message 2
SENT notification to alice@example.com
SENDING notification to alice@example.com
Blocked: Rate limit of 2 notifications exceeded
```

Logging happens for every attempt — including the blocked third one — because `LoggingDecorator` acts before the rate limit check.

The mental model:

```
Call flows inward (outermost acts first).
Result flows outward (outermost acts last).
```

So the outermost decorator has the first word and the last word on every call.

**Answers:**

1. Composition B logs even when the rate limit is exceeded, because logging is outside the rate limit.
2. Because the outermost decorator is the first to intercept the call.
3. Use composition B if you want to audit every attempted send including blocked ones.
4. Use composition A if you only want to log sends that actually went through.

---

## Part C: the production composition

```python
notifier = LoggingDecorator(
    RateLimitDecorator(
        RetryDecorator(
            PrefixDecorator(EmailNotifier(), prefix="[ALERT] "),
            max_retries=2,
        ),
        limit=10,
    )
)
```

Reading the layers from outside in:

| Layer | Why it sits here |
|---|---|
| `LoggingDecorator` | Outermost — logs every attempt, including rate-limited ones |
| `RateLimitDecorator` | Inside logging — rate-limited calls still appear in audit log |
| `RetryDecorator` | Inside rate limit — each retry attempt counts as one send |
| `PrefixDecorator` | Close to the metal — the prefix is part of the message content |
| `EmailNotifier` | The real sender |

If `RetryDecorator` were outside `RateLimitDecorator`, each retry would consume an extra slot from the rate limit. Placing retry inside means one logical send uses one rate-limit slot, even if it takes two attempts.

---

## A common mistake: putting retry outside rate limit

```python
# Risky composition
notifier = RetryDecorator(
    RateLimitDecorator(EmailNotifier(), limit=10),
    max_retries=3,
)
```

Now a rate-limited send gets retried three times — each retry hits the rate limit again and raises. The retry logic is useless here and the error message is confusing. Retry should live inside rate limiting, not outside it.

---

## The general rule for ordering

Think about what each layer should *see*:

- A **logging** layer that should audit all attempts goes outside everything.
- A **rate limit** that counts logical sends goes outside retry but inside logging.
- A **retry** layer that handles transient failures goes close to the real sender.
- A **transform** (prefix, uppercase) that changes the message goes as close to the sender as possible, so all other layers see the original message.

---

[Exercise 2](exercise2.md) · [Exercise 3](exercise3.md)
