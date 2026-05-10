---
layout: default
title: "Exercise 3: Broker Chain — Basic Stat System"
---

# Exercise 3: Broker Chain — Basic Stat System

## Goal

Build a basic character stat system using the Broker Chain pattern. This exercise focuses on the three-part core: **Query**, **Broker**, and **Modifier**.

---

## Part A — the three core pieces

Implement:

**`StatQuery`** — a mutable object with:
- `character_name: str`
- `stat: str` (e.g. `"attack"`, `"defense"`)
- `value: int` — starts at the base value, modifiers change it

**`StatBroker`** — an event bus with:
- `subscribe(handler)` — registers a callable
- `unsubscribe(handler)` — removes a callable
- `publish(query)` — calls every registered handler with the query

**`Character`** — holds base stats and a broker reference:
- `base_attack = 10`, `base_defense = 5`
- `get_attack() -> int` — creates a `StatQuery`, publishes it, returns `query.value`
- `get_defense() -> int` — same for defense

Verify the bare character with no modifiers:

```python
broker = StatBroker()
hero = Character("hero", broker)
assert hero.get_attack()  == 10
assert hero.get_defense() == 5
```

---

## Part B — flat bonus modifier

Add a `FlatBonusModifier` that adds a fixed integer to one stat of one character:

```python
FlatBonusModifier(broker, character_name="hero", stat="attack", bonus=10)
```

After registering, `hero.get_attack()` should return `20`.

Multiple `FlatBonusModifier` instances for the same stat should stack:

```python
FlatBonusModifier(broker, "hero", "attack", 10)
FlatBonusModifier(broker, "hero", "attack",  5)
assert hero.get_attack() == 25
```

---

## Part C — multiplier modifier and removal

Add a `MultiplierModifier` that multiplies a stat by a float:

```python
MultiplierModifier(broker, character_name="hero", stat="attack", multiplier=2.0)
```

Add a `remove()` method to both modifier classes that unsubscribes them from the broker.

Verify:

```python
sword  = FlatBonusModifier(broker, "hero", "attack", 10)   # attack = 20
berserk = MultiplierModifier(broker, "hero", "attack", 2.0) # attack = 40
assert hero.get_attack() == 40

berserk.remove()
assert hero.get_attack() == 20  # multiplier gone

sword.remove()
assert hero.get_attack() == 10  # back to base
```

---

## Skeleton

See `exercise3.py`.

---

## Hints

- `StatBroker.publish` is just a loop: `for h in self._handlers: h(query)`.
- `FlatBonusModifier` subscribes `self._handle` in `__init__`. `_handle` checks `query.character_name` and `query.stat` before modifying `query.value`.
- `MultiplierModifier._handle` should cast the result back to `int`: `query.value = int(query.value * self._multiplier)`.
- Modifier order matters: a flat bonus applied before a multiplier gives a different result than after. The order is determined by subscription order.

---

[Exercise 2](exercise2.md) · [Solution 3](solution3.md) · [Exercise 4](exercise4.md)
