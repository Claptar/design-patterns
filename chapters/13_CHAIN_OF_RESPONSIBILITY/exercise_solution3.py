"""
Exercise 3 — Solution: Broker Chain Basic Stat System
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class StatQuery:
    character_name: str
    stat: str
    value: int


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


class Character:
    def __init__(self, name: str, broker: StatBroker):
        self.name = name
        self._broker = broker
        self.base_attack  = 10
        self.base_defense = 5

    def get_attack(self) -> int:
        q = StatQuery(self.name, "attack", self.base_attack)
        self._broker.publish(q)
        return q.value

    def get_defense(self) -> int:
        q = StatQuery(self.name, "defense", self.base_defense)
        self._broker.publish(q)
        return q.value

    def __str__(self) -> str:
        return f"{self.name}: ATK={self.get_attack()} DEF={self.get_defense()}"


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
        if query.character_name == self._character_name and query.stat == self._stat:
            query.value += self._bonus

    def remove(self) -> None:
        self._broker.unsubscribe(self._handle)


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
        if query.character_name == self._character_name and query.stat == self._stat:
            query.value = int(query.value * self._multiplier)

    def remove(self) -> None:
        self._broker.unsubscribe(self._handle)


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
    assert hero.get_defense() == 5


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
    FlatBonusModifier(broker, "hero", "attack", 10)
    MultiplierModifier(broker, "hero", "attack", 2.0)
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
    assert enemy.get_attack() == 10


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
