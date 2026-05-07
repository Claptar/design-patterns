---
layout: default
title: "Solution 3: Transparent Decorator"
---

# Solution 3: Transparent Decorator

## Part A — why the error happens

```
AttributeError: 'LoggingDecorator' object has no attribute 'set_from_address'
```

When Python evaluates `notifier.set_from_address(...)`, it looks for `set_from_address` on the `LoggingDecorator` instance. It does not find it — because `LoggingDecorator` only declares `send`. Python raises `AttributeError` before it ever thinks to check the wrapped `EmailNotifier`.

The decorator has hidden the inner object's richer interface. This is type erosion.

---

## Part B — the wrong fix and why

```python
class NotifierDecorator(Notifier):
    def send(self, recipient: str, message: str) -> None:
        self._wrapped.send(recipient, message)

    def set_from_address(self, address: str) -> None:
        self._wrapped.set_from_address(address)

    def set_reply_to(self, address: str) -> None:
        self._wrapped.set_reply_to(address)

    def get_sent_count(self) -> int:
        return self._wrapped.get_sent_count()

    def flush_queue(self) -> None:
        self._wrapped.flush_queue()
```

**Problems:**

1. You added 4 forwarding methods that do nothing but call the same method on `self._wrapped`. They add zero logic.
2. When `EmailNotifier` gets `set_bcc` next week, you must update `NotifierDecorator` and every decorator that overrides it.
3. With five decorators, you update five files — or one base and then check that none of the five have silently overridden the new method.
4. The forwarding methods make the class look more complex than it is. A reader must inspect each one to confirm it really does nothing interesting.

This is the scaling problem `__getattr__` solves in one line.

---

## Part C — the right fix

```python
class NotifierDecorator(Notifier):
    def __init__(self, wrapped: Notifier):
        self._wrapped = wrapped

    def send(self, recipient: str, message: str) -> None:
        self._wrapped.send(recipient, message)

    def __getattr__(self, name: str):
        return getattr(self._wrapped, name)
```

That is the entire change. All four forwarding methods are gone.

`__getattr__` fires only when Python's normal attribute lookup fails — which means it only fires for attributes the decorator does not declare itself. The decorator's own `send` method is found by normal lookup and never reaches `__getattr__`.

The lookup for `notifier.set_from_address`:

```
1. LoggingDecorator instance dict          → not found
2. LoggingDecorator and NotifierDecorator  → not found
3. NotifierDecorator.__getattr__("set_from_address")
        → getattr(self._wrapped, "set_from_address")
        → EmailNotifier.set_from_address
```

---

## Part D — chaining through a full stack

```python
notifier = LoggingDecorator(
    RateLimitDecorator(
        PrefixDecorator(EmailNotifier(), prefix="[ALERT] "),
        limit=10,
    )
)

notifier.set_from_address("alerts@company.com")
```

The chain:

```
LoggingDecorator.__getattr__("set_from_address")
    → getattr(RateLimitDecorator, "set_from_address")
    → RateLimitDecorator.__getattr__("set_from_address")
        → getattr(PrefixDecorator, "set_from_address")
        → PrefixDecorator.__getattr__("set_from_address")
            → getattr(EmailNotifier, "set_from_address")
            → EmailNotifier.set_from_address   ✓
```

Each layer delegates to the next until the method is found. This works for any depth of nesting, with no changes to any individual decorator.

For `notifier.get_sent_count()` — the count comes from `EmailNotifier._sent_count`, which is incremented by `EmailNotifier.send`. `PrefixDecorator` transforms the message but calls `EmailNotifier.send` underneath, so the count is correct.

---

## Part E — the static type checking trade-off

```python
def configure_notifier(notifier: EmailNotifier) -> None:
    notifier.set_from_address("alerts@company.com")

configure_notifier(LoggingDecorator(EmailNotifier()))  # runtime: fine
                                                        # mypy: error
```

**At runtime:** works. `__getattr__` forwards `set_from_address` to the inner `EmailNotifier`.

**To a type checker:** `LoggingDecorator` is a `Notifier`, not an `EmailNotifier`. The type checker sees that `LoggingDecorator` only declares `send`, and correctly reports that passing it where `EmailNotifier` is expected is a type error.

The type checker is not wrong. It is pointing out a real design tension: the function signature says "I need the full `EmailNotifier` interface" but you are passing something that only promises `Notifier`. The fact that it works at runtime due to `__getattr__` is invisible to static analysis.

**The trade-offs:**

| Approach | Runtime | Type checker |
|---|---|---|
| `__getattr__` forwarding | Works | Sees `Notifier`, not `EmailNotifier` |
| Manual forwarding methods | Works | Still sees `Notifier` unless you widen the base class |
| `# type: ignore` at call site | Works | Suppressed |
| Accept `Notifier` in the function signature | Works | Fine, but loses `EmailNotifier`-specific guarantees |

The transparent decorator trades static type visibility for zero maintenance cost on the forwarding layer. For most decorator use cases this is the right trade-off — the shared interface covers what matters, and the forwarded methods are incidental configuration. If static safety for those methods matters, you can widen the abstract base, use a Protocol, or add `__getattr__` stubs.

---

## Summary: what each exercise built toward

| Exercise | Core skill |
|---|---|
| 1 | Implement the decorator structure: same interface, wraps in constructor, calls through |
| 2 | Compose multiple decorators and reason about ordering |
| 3 | Fix type erosion with `__getattr__` so the decorator is transparent to the full interface |

The progression mirrors a real development workflow: you build it, you add more of them, and then the wrapped object's interface grows and you hit the type erasion problem and solve it.

---

[Exercise 3](exercise3.md) · [Back to Decorator](decorator.md)
