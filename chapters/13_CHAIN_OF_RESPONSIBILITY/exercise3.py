"""
Exercise 3: Broker Chain — Basic Stat System

Build the three-part core of a broker chain:
  StatQuery   — mutable value container
  StatBroker  — event bus (subscribe / unsubscribe / publish)
  Character   — creates queries and reads results back
  FlatBonusModifier    — adds a fixed bonus to one stat
  MultiplierModifier   — multiplies one stat by a factor
"""

from __future__ import annotations
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Part A — Query
# ---------------------------------------------------------------------------

@dataclass
class StatQuery:
    character_name: str
    stat: str           # "attack" or "defense"
    value: int          # starts at base value; modifiers write here


# ---------------------------------------------------------------------------
# Part A — Broker
# ---------------------------------------------------------------------------

class StatBroker:
    def __init__(self):
        self._handlers: list[callable] = []

    def subscribe(self, handler: callable) -> None:
        # TODO: append handler to self._handlers
        ...

    def unsubscribe(self, handler: callable) -> None:
        # TODO: remove handler from self._handlers
        ...

    def publish(self, query: StatQuery) -> None:
        # TODO: call every handler with the query
        ...


# ---------------------------------------------------------------------------
# Part A — Character
# ---------------------------------------------------------------------------

class Character:
    def __init__(self, name: str, broker: StatBroker):
        self.name = name
        self._broker = broker
        self.base_attack  = 10
        self.base_defense = 5

    def get_attack(self) -> int:
        # TODO: create StatQuery for "attack", publish, return query.value
        ...

    def get_defense(self) -> int:
        # TODO: create StatQuery for "defense", publish, return query.value
        ...

    def __str__(self) -> str:
        return f"{self.name}: ATK={self.get_attack()} DEF={self.get_defense()}"


# ---------------------------------------------------------------------------
# Part B — FlatBonusModifier
# ---------------------------------------------------------------------------

class FlatBonusModifier:
    def __init__(
        self,
        broker: StatBroker,
        character_name: str,
        stat: str,
        bonus: int,
    ):
        self._broker         = broker
        self._character_name = character_name
        self._stat           = stat
        self._bonus          = bonus
        broker.subscribe(self._handle)

    def _handle(self, query: StatQuery) -> None:
        # TODO: if query matches character_name and stat, add self._bonus to query.value
        ...

    def remove(self) -> None:
        # TODO: unsubscribe self._handle from the broker
        ...


# ---------------------------------------------------------------------------
# Part C — MultiplierModifier
# ---------------------------------------------------------------------------

class MultiplierModifier:
    def __init__(
        self,
        broker: StatBroker,
        character_name: str,
        stat: str,
        multiplier: float,
    ):
        self._broker         = broker
        self._character_name = character_name
        self._stat           = stat
        self._multiplier     = multiplier
        broker.subscribe(self._handle)

    def _handle(self, query: StatQuery) -> None:
        # TODO: if query matches, multiply query.value and cast to int
        ...

    def remove(self) -> None:
        # TODO: unsubscribe self._handle from the broker
        ...


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def make_hero() -> tuple[StatBroker, Character]:
    broker = StatBroker()
    hero   = Character("hero", broker)
    return broker, hero


def test_no_modifiers():
    _, hero = make_hero()
    assert hero.get_attack()  == 10
    assert hero.get_defense() == 5


def test_flat_bonus_attack(capsys):
    broker, hero = make_hero()
    FlatBonusModifier(broker, "hero", "attack", 10)
    assert hero.get_attack()  == 20
    assert hero.get_defense() == 5   # defense unchanged


def test_flat_bonuses_stack():
    broker, hero = make_hero()
    FlatBonusModifier(broker, "hero", "attack", 10)
    FlatBonusModifier(broker, "hero", "attack",  5)
    assert hero.get_attack() == 25


def test_multiplier():
    broker, hero = make_hero()
    MultiplierModifier(broker, "hero", "attack", 2.0)
    assert hero.get_attack() == 20


def test_flat_then_multiplier():
    broker, hero = make_hero()
    FlatBonusModifier(broker, "hero", "attack", 10)   # 10 + 10 = 20
    MultiplierModifier(broker, "hero", "attack", 2.0) # 20 * 2 = 40
    assert hero.get_attack() == 40


def test_remove_restores_base():
    broker, hero = make_hero()
    sword   = FlatBonusModifier(broker, "hero", "attack", 10)
    berserk = MultiplierModifier(broker, "hero", "attack", 2.0)
    assert hero.get_attack() == 40

    berserk.remove()
    assert hero.get_attack() == 20

    sword.remove()
    assert hero.get_attack() == 10


def test_modifier_only_affects_own_character():
    broker = StatBroker()
    hero   = Character("hero",  broker)
    enemy  = Character("enemy", broker)
    FlatBonusModifier(broker, "hero", "attack", 10)
    assert hero.get_attack()  == 20
    assert enemy.get_attack() == 10   # enemy unaffected


if __name__ == "__main__":
    broker, hero = make_hero()
    print(hero)

    sword = FlatBonusModifier(broker, "hero", "attack", 10)
    print(f"After sword:   {hero}")

    shield = FlatBonusModifier(broker, "hero", "defense", 5)
    print(f"After shield:  {hero}")

    berserk = MultiplierModifier(broker, "hero", "attack", 2.0)
    print(f"Berserk on:    {hero}")

    berserk.remove()
    print(f"Berserk off:   {hero}")

    sword.remove()
    shield.remove()
    print(f"No modifiers:  {hero}")
