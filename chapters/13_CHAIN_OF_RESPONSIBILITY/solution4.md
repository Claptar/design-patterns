---
layout: default
title: "Solution 4: Scoped and Conditional Modifiers"
---

# Solution 4: Scoped and Conditional Modifiers

## Part A — context manager on the base class

The cleanest place for `__enter__` and `__exit__` is the `Modifier` base class. Every subclass automatically inherits both:

```python
class Modifier:
    ...

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.remove()
        return False
```

`__exit__` returns `False` — this tells Python not to suppress any exception that caused the `with` block to exit. The modifier is removed regardless, but the exception still propagates. This is the correct behavior for a resource-cleanup `__exit__`.

If you return `True`, exceptions are swallowed silently, which is almost never what you want.

The test that verifies exception safety:

```python
try:
    with FlatBonusModifier(broker, "hero", "attack", 20):
        raise RuntimeError("boom")
except RuntimeError:
    pass

assert hero.get_attack() == 10  # cleaned up despite the exception
```

This works because `__exit__` is always called by Python's `with` machinery, even if the body raised. It's the same guarantee you get with `finally`.

---

## Part B — ConditionalModifier

```python
class ConditionalModifier(Modifier):
    def _handle(self, query: StatQuery) -> None:
        if self._matches(query) and self._condition():
            query.value += self._bonus
```

The key is `self._condition()` — called at handle time, not at registration time. The lambda passed in:

```python
condition=lambda: hero.health < hero.max_health * 0.25
```

captures a reference to `hero`, not a snapshot of `hero.health`. So every time `_condition()` is called, it reads the *current* value of `hero.health`. This is what makes the modifier reactive to live game state.

If you wrote `condition=hero.health < 25` instead (without a lambda), you'd capture a bool at registration time, and the modifier would never react to health changes afterward.

---

## Part C discussion

The full scenario demonstrates several things working together:

**Two characters on one broker.** The character name filter ensures each modifier only affects its intended target. `villain_armor` affects only `villain.get_defense()`.

**Scoped berserk inside a `with` block.** Everything inside the `with` block sees the berserk buff. Everything outside does not. The cleanup is guaranteed, which matters in game logic — a berserk effect that never expires is a bug.

**Conditional modifier reads live state.** `last_stand` is registered at the start of the scenario but produces no effect until `hero.health` drops below 25%. When health is restored, it deactivates automatically — no explicit enable/disable needed.

**Order of the assertions matters.** Step 3 (hero health drop) happens *inside* the `with` block, so both berserk and last stand are active simultaneously. Step 4 (after `with`) removes berserk but not last stand. Step 5 restores health, deactivating last stand through the condition.

---

## Pitfalls

**Forgetting `return False` in `__exit__`.**

Returning `True` or `None` instead of `False` changes exception handling:

```python
def __exit__(self, exc_type, exc_val, exc_tb):
    self.remove()
    # implicitly returns None, which Python treats as False — fine
    # but being explicit is clearer
    return False
```

Both `None` and `False` are equivalent here, but `return False` makes intent explicit.

**Mutating the broker's handler list while iterating.**

If a modifier's `_handle` method called `self.remove()` on itself during a publish, it would mutate `self._handlers` while `publish` is iterating over it. This causes a `RuntimeError: list changed size during iteration`.

To guard against this, `publish` can iterate over a copy:

```python
def publish(self, query: StatQuery) -> None:
    for handler in list(self._handlers):   # iterate over snapshot
        handler(query)
```

This is a good defensive practice when self-removal during handling is possible.

**Lambda capture in a loop.**

A subtle Python pitfall: if you create `ConditionalModifier` instances in a loop and the condition references the loop variable, all modifiers will share the final loop value:

```python
# Bug: all lambdas capture the same `i` variable
for i in range(3):
    ConditionalModifier(broker, "hero", "attack", i * 10,
                        condition=lambda: i > 1)  # always uses final i
```

Fix with a default argument:

```python
for i in range(3):
    ConditionalModifier(broker, "hero", "attack", i * 10,
                        condition=lambda i=i: i > 1)  # captures current i
```

This is a general Python lambda-in-loop pitfall, not specific to the broker chain.

---

## Summary of the full pattern

After all four exercises, the complete broker chain implementation has these parts:

| Part | Role |
|---|---|
| `StatQuery` | Mutable container — carries the value being computed |
| `StatBroker` | Event bus — subscribe, unsubscribe, publish |
| `Character` | Creates queries fresh per call, reads result back |
| `Modifier` | Base class — subscribes `_handle`, provides `remove()` and context manager |
| `FlatBonusModifier` | Adds a constant to the stat |
| `MultiplierModifier` | Multiplies the stat |
| `ConditionalModifier` | Applies a bonus only when a runtime condition is true |

Each piece has one job. None of them know about the others. The broker is the only shared link.

---

[Exercise 4](exercise4.md) · [Back to Method Chain](chain_of_responsibility_method_chain.md) · [Back to Broker Chain](chain_of_responsibility_broker.md)
