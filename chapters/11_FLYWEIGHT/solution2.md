---
layout: default
title: "Flyweight Exercise 2 — Solution & Discussion"
---

# Flyweight Exercise 2 — Solution & Discussion

## Part A — the factory

```python
class ParticleTypeFactory:
    _cache: dict[str, ParticleType] = {}

    @classmethod
    def get(cls, name: str) -> ParticleType:
        if name not in cls._cache:
            cfg = _CONFIGS[name]
            cls._cache[name] = ParticleType(
                name=name,
                color=cfg["color"],
                texture_data=load_texture(name),
                blend_mode=cfg["blend_mode"],
                mesh_vertices=tuple(load_mesh(name)),
            )
        return cls._cache[name]

    @classmethod
    def instance_count(cls) -> int:
        return len(cls._cache)
```

Three points worth noting about this implementation.

The cache is a **class variable**, not an instance variable. This means all callers share
the same cache. If `_cache` were an instance variable, every new `ParticleTypeFactory()`
would start empty and the sharing guarantee would evaporate. Class variables are the right
tool here because the factory is acting like a module-level registry.

The factory **only creates on the first access**. This is lazy initialisation — the
`"smoke"` `ParticleType` is not created until someone actually requests a smoke particle.
In a game that might never spawn smoke, this avoids loading the smoke texture entirely.

`load_texture` and `load_mesh` are called **inside the factory**, not at the call site.
That keeps the creation logic in one place. Callers just say `get("flame")` — they do
not need to know that textures and meshes are involved.

---

## Part B — create_particle

```python
def create_particle(particle_type: str) -> Particle:
    return Particle(
        x=random.uniform(0, 800),
        y=random.uniform(0, 600),
        vx=random.uniform(-1, 1),
        vy=random.uniform(-2, 0),
        lifetime=random.uniform(0.5, 3.0),
        particle_type_ref=ParticleTypeFactory.get(particle_type),
    )
```

The only change from the naïve version is `particle_type_ref=ParticleTypeFactory.get(...)`.
Everything else is the same. The caller's interface is unchanged — it still passes a type
name string. The sharing happens invisibly inside the factory.

---

## Part C — measured memory savings

Representative figures comparing Exercise 1 (no sharing) vs Exercise 2 (with factory):

| Metric | Before (Exercise 1) | After (Exercise 2) |
|---|---|---|
| Flyweight objects | 5,000 | 3 |
| Current RAM (5k particles) | ~2,150 MB | ~1.2 MB |
| Per particle | ~440 KB | ~240 bytes |
| Reduction | — | ~1,800× |

The three flyweights (`flame`, `ember`, `smoke`) together hold about 900 KB of texture and
mesh data — loaded once, shared by every particle. Each context object (`Particle`) holds
five numbers and a pointer, which is roughly 200–300 bytes on a 64-bit machine.

The numbers confirm the core Flyweight promise: the number of heavy objects is bounded by
the number of *types* (3), not the number of *instances* (5,000 or 5,000,000).

---

## Part D — simulate and render

```python
def simulate(particles: list[Particle], dt: float) -> None:
    for p in particles:
        p.x  += p.vx * dt
        p.y  += p.vy * dt
        p.lifetime -= dt


def render(particles: list[Particle]) -> None:
    for p in particles:
        _ = p.particle_type_ref.texture_data
        _ = p.particle_type_ref.mesh_vertices
```

Notice the render function accesses `p.particle_type_ref.texture_data` — one extra
attribute hop vs the old `p.texture_data`. This is the Flyweight pattern's only cost: a
small indirection at access time. In practice CPython resolves this in nanoseconds; it is
never the performance bottleneck when you have thousands of particles.

---

## A common mistake: checking equality instead of identity

The tests use `is` rather than `==`:

```python
assert a is b   # correct — same object
assert a == b   # wrong — only checks that values match
```

Why does this matter? `frozen=True` dataclasses implement `__eq__` by comparing field
values. Two separately constructed `ParticleType("flame", ...)` objects would be `==` even
though they are different objects wasting separate RAM. The Flyweight guarantee is about
**identity** — one object in memory, not two objects that happen to look the same.

---

## What is still missing

The factory works, but it has one rough edge: if you pass an unknown type name
(e.g. `"lava"`), Python raises a `KeyError` from the `_CONFIGS` lookup with a cryptic
error message. Exercise 3 adds a proper registry and better error handling.

---

## Pitfall: the class-level cache is shared between test runs

Because `_cache` is a class variable, it persists between tests in the same process.
`test_instance_count_caps_at_three` works because we call `get(...)` many times on the
same three types. But if you add a test that calls `get("lava")` expecting a `ValueError`,
and `_cache` already has entries from a previous test, the count will be off.

The cleanest fix is to add a `clear()` class method for tests:

```python
@classmethod
def clear(cls) -> None:
    cls._cache.clear()
```

Call it in `setUp` or `tearDown`. In production code you would never clear the cache —
that is what makes the flyweights worth keeping.

---

[Exercise 1](exercise1.md) · [Exercise 3](exercise3.md) · [Back to Flyweight](flyweight.md)
