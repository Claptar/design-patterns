"""
Exercise 4 — Solution: Scoped and Conditional Modifiers
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable


@dataclass
class StatQuery:
    character_name: str
    stat: str
    value: int


class StatBroker:
    def __init__(self):
        self._handlers: list[Callable] = []

    def subscribe(self, handler: Callable) -> None:
        self._handlers.append(handler)

    def unsubscribe(self, handler: Callable) -> None:
        self._handlers.remove(handler)

    def publish(self, query: StatQuery) -> None:
        for handler in self._handlers:
            handler(query)


class Character:
    def __init__(self, name: str, broker: StatBroker):
        self.name = name
        self._broker = broker
        self.base_attack  = 10
        self.base_defense = 5
        self.health       = 100
        self.max_health   = 100

    def get_attack(self) -> int:
        q = StatQuery(self.name, "attack", self.base_attack)
        self._broker.publish(q)
        return q.value

    def get_defense(self) -> int:
        q = StatQuery(self.name, "defense", self.base_defense)
        self._broker.publish(q)
        return q.value

    def __str__(self) -> str:
        return (
            f"{self.name}: "
            f"ATK={self.get_attack()} "
            f"DEF={self.get_defense()} "
            f"HP={self.health}/{self.max_health}"
        )


# ---------------------------------------------------------------------------
# Modifier base — with context manager support (Part A)
# ---------------------------------------------------------------------------

class Modifier:
    def __init__(self, broker: StatBroker, character_name: str, stat: str):
        self._broker         = broker
        self._character_name = character_name
        self._stat           = stat
        broker.subscribe(self._handle)

    def _handle(self, query: StatQuery) -> None:
        raise NotImplementedError

    def _matches(self, query: StatQuery) -> bool:
        return (
            query.character_name == self._character_name
            and query.stat == self._stat
        )

    def remove(self) -> None:
        self._broker.unsubscribe(self._handle)

    # --- Part A: context manager ---

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.remove()
        return False    # do not suppress exceptions


class FlatBonusModifier(Modifier):
    def __init__(self, broker, character_name, stat, bonus: int):
        super().__init__(broker, character_name, stat)
        self._bonus = bonus

    def _handle(self, query: StatQuery) -> None:
        if self._matches(query):
            query.value += self._bonus


class MultiplierModifier(Modifier):
    def __init__(self, broker, character_name, stat, multiplier: float):
        super().__init__(broker, character_name, stat)
        self._multiplier = multiplier

    def _handle(self, query: StatQuery) -> None:
        if self._matches(query):
            query.value = int(query.value * self._multiplier)


# ---------------------------------------------------------------------------
# Part B — ConditionalModifier
# ---------------------------------------------------------------------------

class ConditionalModifier(Modifier):
    def __init__(
        self,
        broker: StatBroker,
        character_name: str,
        stat: str,
        bonus: int,
        condition: Callable[[], bool],
    ):
        super().__init__(broker, character_name, stat)
        self._bonus     = bonus
        self._condition = condition

    def _handle(self, query: StatQuery) -> None:
        if self._matches(query) and self._condition():
            query.value += self._bonus


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def make_hero() -> tuple[StatBroker, Character]:
    broker = StatBroker()
    return broker, Character("hero", broker)


def test_scoped_modifier_removes_on_exit():
    broker, hero = make_hero()

    with FlatBonusModifier(broker, "hero", "attack", 20):
        assert hero.get_attack() == 30

    assert hero.get_attack() == 10


def test_scoped_modifier_removes_on_exception():
    broker, hero = make_hero()

    try:
        with FlatBonusModifier(broker, "hero", "attack", 20):
            assert hero.get_attack() == 30
            raise RuntimeError("boom")
    except RuntimeError:
        pass

    assert hero.get_attack() == 10


def test_scoped_multiplier_removes_on_exit():
    broker, hero = make_hero()

    with MultiplierModifier(broker, "hero", "attack", 3.0):
        assert hero.get_attack() == 30

    assert hero.get_attack() == 10


def test_conditional_inactive_when_condition_false():
    broker, hero = make_hero()
    hero.health = 100

    ConditionalModifier(
        broker, "hero", "defense", 15,
        condition=lambda: hero.health < hero.max_health * 0.25,
    )

    assert hero.get_defense() == 5


def test_conditional_active_when_condition_true():
    broker, hero = make_hero()
    hero.health = 20

    ConditionalModifier(
        broker, "hero", "defense", 15,
        condition=lambda: hero.health < hero.max_health * 0.25,
    )

    assert hero.get_defense() == 20


def test_conditional_reacts_to_live_state():
    broker, hero = make_hero()

    ConditionalModifier(
        broker, "hero", "defense", 15,
        condition=lambda: hero.health < hero.max_health * 0.25,
    )

    hero.health = 100
    assert hero.get_defense() == 5

    hero.health = 20
    assert hero.get_defense() == 20

    hero.health = 80
    assert hero.get_defense() == 5


def test_part_c_full_scenario():
    broker  = StatBroker()
    hero    = Character("hero",    broker)
    villain = Character("villain", broker)

    FlatBonusModifier(broker, "hero",    "attack",  10)
    FlatBonusModifier(broker, "villain", "defense",  8)
    ConditionalModifier(
        broker, "hero", "defense", 15,
        condition=lambda: hero.health < hero.max_health * 0.25,
    )

    hero.health = 100
    assert hero.get_attack()     == 20
    assert hero.get_defense()    == 5
    assert villain.get_attack()  == 10
    assert villain.get_defense() == 13

    with MultiplierModifier(broker, "villain", "attack", 2.0):
        assert villain.get_attack() == 20

        hero.health = 20
        assert hero.get_defense() == 20

    assert villain.get_attack() == 10

    hero.health = 80
    assert hero.get_defense() == 5


if __name__ == "__main__":
    broker  = StatBroker()
    hero    = Character("hero",    broker)
    villain = Character("villain", broker)

    FlatBonusModifier(broker, "hero",    "attack",  10)
    FlatBonusModifier(broker, "villain", "defense",  8)
    ConditionalModifier(
        broker, "hero", "defense", 15,
        condition=lambda: hero.health < hero.max_health * 0.25,
    )

    print("=== Step 1: initial state ===")
    print(hero)
    print(villain)

    print("\n=== Step 2: villain berserk ===")
    with MultiplierModifier(broker, "villain", "attack", 2.0):
        print(villain)

        print("\n=== Step 3: hero nearly dead ===")
        hero.health = 20
        print(hero)

    print("\n=== Step 4: berserk expired ===")
    print(villain)

    print("\n=== Step 5: hero recovered ===")
    hero.health = 80
    print(hero)
