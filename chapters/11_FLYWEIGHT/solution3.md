---
layout: default
title: "Flyweight Exercise 3 — Solution & Discussion"
---

# Flyweight Exercise 3 — Solution & Discussion

## Part A — extrinsic state passed into the flyweight

```python
def draw(self, x: float, y: float, lifetime: float) -> str:
    r, g, b = self.color
    return (
        f"{self.name} at ({x:.1f}, {y:.1f}) "
        f"lifetime={lifetime:.2f}s "
        f"[{self.blend_mode}, rgb({r},{g},{b})]"
    )
```

This is the canonical Flyweight method signature. Compare the two shapes:

```python
# Non-flyweight: method reads all state from self
def draw(self) -> str:
    return f"{self.name} at ({self.x:.1f}, {self.y:.1f}) ..."

# Flyweight: method receives extrinsic state from the caller
def draw(self, x: float, y: float, lifetime: float) -> str:
    return f"{self.name} at ({x:.1f}, {y:.1f}) ..."
```

In the flyweight version, `draw` reads `self.name`, `self.color`, `self.blend_mode` from
the flyweight (intrinsic — same for all flames), and it reads `x`, `y`, `lifetime` from
parameters (extrinsic — unique per particle, passed in from the context).

The flyweight does not store `x`, `y`, or `lifetime`. It cannot — it is shared among
thousands of particles, each at a different position. The caller is responsible for
holding the extrinsic state and handing it over at call time.

This is the key conceptual shift that separates Flyweight from regular objects: the
method *receives* context rather than *reading* it from `self`.

---

## Part B — the extensible registry

```python
class ParticleTypeFactory:
    _cache: dict[str, ParticleType] = {}
    _registry: dict[str, dict] = {}

    @classmethod
    def register(cls, name, color, texture_data, blend_mode, mesh_vertices) -> None:
        if name in cls._registry:
            raise ValueError(f"Particle type '{name}' is already registered")
        cls._registry[name] = {
            "color": color,
            "texture_data": texture_data,
            "blend_mode": blend_mode,
            "mesh_vertices": mesh_vertices,
        }

    @classmethod
    def get(cls, name: str) -> ParticleType:
        if name not in cls._registry:
            raise ValueError(
                f"Unknown particle type: '{name}'. "
                f"Available: {sorted(cls._registry)}"
            )
        if name not in cls._cache:
            cfg = cls._registry[name]
            cls._cache[name] = ParticleType(name=name, **cfg)
        return cls._cache[name]
```

The design now has two separate dictionaries with two separate jobs.

`_registry` is the **catalogue**: it holds the *spec* for each type. Adding a type to the
registry is cheap — it just stores a dict with some bytes and numbers.

`_cache` is the **instance pool**: it holds the actual `ParticleType` objects. A
`ParticleType` is only constructed when someone calls `get("spark")` for the first time.
This is why `instance_count()` returns the number of *instantiated* flyweights, not the
number of registered types. Four types can be registered while only two are ever requested
— only two flyweights exist.

The `ValueError` with a helpful message matters more than it might seem. In a game engine,
a bad type name might come from a level config file. A raw `KeyError` tells the level
designer nothing; `"Unknown particle type: 'lava'. Available: ['ember', 'flame', 'smoke']"`
tells them exactly what to fix.

---

## Part C — the Scene loop

```python
class Scene:
    def tick(self, dt: float) -> None:
        for p in self.particles:
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.lifetime -= dt
        self.particles = [p for p in self.particles if p.lifetime > 0]
```

The list comprehension at the end of `tick` is the standard Python idiom for filtering in
place. It replaces the list in one step rather than deleting while iterating (which is
unsafe and error-prone).

Notice what does *not* happen here: the flyweights are unaffected. Particles die and are
garbage-collected. The `ParticleType` objects in `_cache` remain alive for the duration of
the program — they are referenced by the cache dict, so the garbage collector cannot
reclaim them. This is correct: flyweights should outlive the individual contexts.

---

## Part D — custom type registration

```
Registered types:  ['ember', 'flame', 'smoke', 'spark']
Particles:         300
Flyweight objects: 2
```

Only 2 flyweights despite 4 registered types, because `"ember"` and `"smoke"` were never
requested. Their config lives in `_registry` but no `ParticleType` object was ever
created for them.

This demonstrates that the registry and the instance pool are genuinely different
concerns. You can ship a game with 50 registered particle types in the catalogue, while a
given scene instantiates only the 6 it actually uses.

---

## The full Flyweight picture after three exercises

| Concern | Where it lives | Exercise |
|---|---|---|
| Intrinsic state (texture, mesh, color) | `ParticleType` fields | 1 |
| Extrinsic state (x, y, lifetime) | `Particle` fields | 1 |
| Sharing guarantee | `ParticleTypeFactory._cache` | 2 |
| Acting on extrinsic state | `ParticleType.draw(x, y, lifetime)` | 3 |
| Extensible catalogue | `ParticleTypeFactory._registry` | 3 |
| Context lifecycle management | `Scene.tick()` cleanup | 3 |

---

## Common improvements to consider

**Thread safety**: If particles are spawned from multiple threads, two threads could
simultaneously find `name not in cls._cache` and both attempt to create the flyweight.
The fix is a `threading.Lock` around the creation block.

```python
import threading

class ParticleTypeFactory:
    _cache: dict[str, ParticleType] = {}
    _registry: dict[str, dict] = {}
    _lock = threading.Lock()

    @classmethod
    def get(cls, name: str) -> ParticleType:
        if name not in cls._cache:             # fast path — no lock
            with cls._lock:
                if name not in cls._cache:     # double-checked locking
                    ...
        return cls._cache[name]
```

**Weak references for very large flyweight pools**: In most cases flyweights should live
as long as the factory. But if you have thousands of distinct flyweight types and want
unused ones to be garbage-collected, the cache values can be `weakref.ref` objects. When
no `Particle` holds a reference to a `ParticleType`, the GC can reclaim it, and the next
`get()` recreates it.

**Separating `clear()` from production code**: The `clear()` method exists for testing.
In production you would never expose it. A common pattern is to move it behind a
`TYPE_CHECKING` guard or into a test fixture.

---

## Summary mental model

After three exercises, the Flyweight pattern reduces to three decisions and one rule.

The three decisions:

1. What is intrinsic? → put it in the flyweight, make it immutable.
2. What is extrinsic? → keep it in the context, pass it into flyweight methods.
3. Who enforces sharing? → the factory, via a cache keyed on intrinsic identity.

The one rule:

> The number of flyweight objects is bounded by the number of distinct intrinsic
> states, not the number of context objects.

Three particle types → three flyweights → no matter if you have 300 or 3,000,000 particles.

---

[Exercise 2](exercise2.md) · [Back to Flyweight](flyweight.md)
