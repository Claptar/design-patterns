---
layout: default
title: "Solution 3: Broker Chain — Basic Stat System"
---

# Solution 3: Broker Chain — Basic Stat System

## Part A — the three core pieces

The broker is deliberately minimal:

```python
class StatBroker:
    def __init__(self):
        self._handlers: list[callable] = []

    def subscribe(self, handler: callable) -> None:
        self._handlers.append(handler)

    def unsubscribe(self, handler: callable) -> None:
        self._handlers.remove(handler)

    def publish(self, query: StatQuery) -> None:
        for handler in self._handlers:
            handler(query)
```

`publish` is just a loop. Nothing more is needed. The power comes from the fact that every subscribed handler sees the same `query` object — mutations accumulate.

The character creates a fresh query for every call to `get_attack`:

```python
def get_attack(self) -> int:
    q = StatQuery(self.name, "attack", self.base_attack)
    self._broker.publish(q)
    return q.value
```

This is important: the query is **not stored**. It lives only for the duration of the publish call. This is what keeps `get_attack` a pure query in the CQS sense — calling it twice gives the same result, and nothing is persisted.

---

## Part B — FlatBonusModifier

```python
def _handle(self, query: StatQuery) -> None:
    if query.character_name == self._character_name and query.stat == self._stat:
        query.value += self._bonus
```

Two conditions must match: the right character and the right stat. Without both guards, a sword intended for the hero would also buff the enemy.

**Stacking** works automatically. Two `FlatBonusModifier` instances for the same stat register two separate `_handle` methods. Both run on every `publish`. The query's `value` gets incremented twice.

---

## Part C — MultiplierModifier and removal

```python
def _handle(self, query: StatQuery) -> None:
    if query.character_name == self._character_name and query.stat == self._stat:
        query.value = int(query.value * self._multiplier)
```

The `int()` cast is necessary because `value` starts as `int` and Python arithmetic with a `float` multiplier produces a `float`. Keeping `value` as `int` throughout avoids surprising type changes downstream.

**Removal** works because `_handle` is a bound method — `self._broker.unsubscribe(self._handle)` removes the exact same object that was subscribed. Python bound methods support identity comparison via their `__eq__`, which checks both the function and the `self` they're bound to.

---

## Discussion and pitfalls

**Modifier order is significant.**

`FlatBonus(+10)` then `Multiplier(×2)`:

```text
base=10 → +10 → 20 → ×2 → 40
```

`Multiplier(×2)` then `FlatBonus(+10)`:

```text
base=10 → ×2 → 20 → +10 → 30
```

The same modifiers produce different results depending on subscription order. In a real game system, you would define a priority or ordering mechanism — for example, giving each modifier a numeric priority and sorting `_handlers` by it in `publish`. For this exercise, insertion order (subscription order) is enough.

**Fresh query per call is essential.**

If the character stored the query object and reused it, modifiers would accumulate across calls instead of starting fresh from the base value each time. The pattern only works correctly because `get_attack` creates a new `StatQuery(... base_attack)` every time it's called.

**Multiple characters on one broker.**

The character name filter (`query.character_name == self._character_name`) is what allows multiple characters to share one broker safely. Without it, equipping a sword on the hero would also buff the enemy. This is tested in `test_modifier_only_affects_own_character`.

**Possible improvement — a Modifier base class.**

Both `FlatBonusModifier` and `MultiplierModifier` share the same constructor shape and `remove()` method. Extracting a base class removes the duplication:

```python
class Modifier:
    def __init__(self, broker, character_name, stat):
        self._broker         = broker
        self._character_name = character_name
        self._stat           = stat
        broker.subscribe(self._handle)

    def _handle(self, query: StatQuery) -> None:
        raise NotImplementedError

    def _matches(self, query: StatQuery) -> bool:
        return (query.character_name == self._character_name
                and query.stat == self._stat)

    def remove(self) -> None:
        self._broker.unsubscribe(self._handle)
```

Then each concrete modifier only needs to implement `_handle` and call `self._matches(query)`.

---

[Exercise 3](exercise3.md) · [Exercise 4](exercise4.md)
