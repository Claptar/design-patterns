---
layout: default
title: "Exercise 4: Broker Chain — Scoped and Conditional Modifiers"
---

# Exercise 4: Broker Chain — Scoped and Conditional Modifiers

## Context

We continue with the stat system from Exercise 3. The base code — `StatQuery`, `StatBroker`, `Character`, `FlatBonusModifier`, `MultiplierModifier` — is already in place.

This exercise adds two real-world requirements: modifiers that clean themselves up automatically, and modifiers that react to live character state.

---

## Part A — ScopedModifier (context manager)

Make modifiers work as context managers so temporary effects are guaranteed to clean up, even if an exception is raised.

Implement a `ScopedModifier` base class (or mixin) that adds `__enter__` and `__exit__`:

```python
with FlatBonusModifier(broker, "hero", "attack", 20) as _:
    print(hero.get_attack())   # 30 (base 10 + bonus 20)

print(hero.get_attack())       # 10 — modifier removed on exit
```

Both `FlatBonusModifier` and `MultiplierModifier` should support the context manager protocol.

Verify that the modifier is removed even when the `with` block raises an exception:

```python
try:
    with FlatBonusModifier(broker, "hero", "attack", 20):
        raise RuntimeError("something went wrong")
except RuntimeError:
    pass

assert hero.get_attack() == 10  # still cleaned up
```

---

## Part B — ConditionalModifier

Add a `ConditionalModifier` that only applies its effect when a runtime condition is true.

```python
ConditionalModifier(
    broker,
    character_name="hero",
    stat="defense",
    bonus=15,
    condition=lambda: hero.health < hero.max_health * 0.25,
)
```

This modifier should add `+15` defense, but **only when the condition returns `True` at the moment the query fires** — not at registration time.

Verify:

```python
hero.health = 100
assert hero.get_defense() == 5    # condition false, no bonus

hero.health = 20                  # below 25% of 100
assert hero.get_defense() == 20   # condition true, bonus applied
```

---

## Part C — putting it all together

Wire a scenario with two characters sharing one broker. Use all four modifier types:

- `hero` has a sword (`FlatBonusModifier`, permanent)
- `hero` has a Last Stand effect (`ConditionalModifier`, activates at low health)
- `villain` gets a temporary berserk buff (`MultiplierModifier`, scoped)
- `villain` has armor (`FlatBonusModifier`, permanent)

Walk through a sequence of game events and assert the stats at each step:

1. Start — verify base stats plus permanent modifiers.
2. Villain's berserk activates (enter `with` block) — verify villain's boosted attack.
3. Hero's health drops below 25% — verify hero's Last Stand defense.
4. Villain's berserk expires (exit `with` block) — verify villain's attack is back to normal.
5. Hero's health is restored — verify Last Stand is inactive again.

---

## Skeleton

See `exercise4.py`.

---

## Hints

- `ScopedModifier.__enter__` should return `self`. `__exit__` should call `self.remove()` and return `False` (don't suppress exceptions).
- `ConditionalModifier._handle` should call `self._condition()` at handle time, not at registration time. The lambda captures a reference to `hero`, so it always reads the *current* value of `hero.health`.
- For Part C, the `with` block for the villain's berserk should contain all the assertions that depend on the buff being active.

---

[Exercise 3](exercise3.md) · [Solution 4](solution4.md)
