---
layout: default
title: "Flyweight Exercise 1 — Solution & Discussion"
---

# Flyweight Exercise 1 — Solution & Discussion

## Part A — measured memory (representative figures)

With 5,000 particles before any refactoring:

```
Particles:    5,000
Current RAM:  ~2,150 MB
Peak RAM:     ~2,150 MB
Per particle: ~440 KB
```

The per-particle cost breaks down roughly as:
- `texture_data` for flame: 512 KB, ember: 128 KB, smoke: 256 KB
- `mesh_vertices` for flame: ~1.6 KB (200 floats × 8 bytes), ember: ~0.6 KB, smoke: ~1.3 KB
- Position, velocity, lifetime: negligible (~56 bytes)

All of that texture and mesh data is loaded fresh for each particle, even though every
flame has exactly the same texture, every ember has the same mesh, and so on.

---

## Part B — field classification

| Field | Intrinsic or Extrinsic? | Reason |
|---|---|---|
| `x` | **Extrinsic** | Every particle is at a different position |
| `y` | **Extrinsic** | Every particle is at a different position |
| `vx` | **Extrinsic** | Velocity is randomised per particle |
| `vy` | **Extrinsic** | Velocity is randomised per particle |
| `lifetime` | **Extrinsic** | Decreases independently per particle |
| `particle_type` | **Intrinsic** | Defines the flyweight — it *is* the key |
| `color` | **Intrinsic** | All flames share the same orange; all smoke shares the same gray |
| `texture_data` | **Intrinsic** | Identical for all particles of the same type |
| `blend_mode` | **Intrinsic** | Determined by type, never per-particle |
| `mesh_vertices` | **Intrinsic** | Identical geometry for all particles of the same type |

A useful cross-check: if two particles of the same type could legitimately have *different*
values for a field, it must be extrinsic. Position, velocity, and lifetime clearly pass that
test. Color and texture do not — you would never want two flames to have different colors
(that would mean they are different types, not the same type with unique state).

---

## Part C — the split

`ParticleType` (flyweight — intrinsic state):
```
name, color, texture_data, blend_mode, mesh_vertices
```

`Particle` (context — extrinsic state + reference):
```
x, y, vx, vy, lifetime, particle_type_ref: ParticleType
```

At runtime: **3 `ParticleType` objects** exist, regardless of whether there are 100 or
100,000 particles. One for flame, one for ember, one for smoke.

---

## Part D — the stubs

```python
@dataclass(frozen=True)
class ParticleType:
    name: str
    color: tuple[int, int, int]
    texture_data: bytes
    blend_mode: str
    mesh_vertices: tuple[float, ...]


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    lifetime: float
    particle_type_ref: ParticleType
```

Two decisions worth explaining:

**`frozen=True` on `ParticleType`**: The flyweight's intrinsic state must be immutable.
If it were mutable, changing the flame texture would silently affect every particle in the
scene. `frozen=True` enforces this at runtime and makes the object hashable (useful in
Exercise 2 when the factory needs the type as a dict key).

**`tuple` instead of `list` for `mesh_vertices`**: A `frozen=True` dataclass requires all
fields to be hashable. Lists are not hashable; tuples are. This is a side effect of
choosing the right immutability tool — `tuple` communicates "this data does not change
after construction" in a way that `list` does not.

---

## What is still missing

The stubs pass the tests, but memory is not better yet. Nothing enforces that two
flame particles share the *same* `ParticleType` object — if `create_particle` calls
`make_particle_type("flame")` twice, it creates two separate objects with separate
copies of the texture.

The factory that prevents this duplication is Exercise 2's job.

---

## Pitfalls to watch for

**Mutable intrinsic state** is the most common Flyweight bug. If you forget `frozen=True`
and later write `particle.particle_type_ref.color = (255, 0, 0)`, you have accidentally
recolored every single particle of that type. The error is silent and very hard to debug.

**Treating the type string as the extrinsic state**: some people keep `particle_type: str`
in the context object and look up the flyweight lazily. That works, but it defers the
lookup to render time and can hide the fact that sharing is not happening. Better to store
the reference directly.

---

[Exercise 2](exercise2.md) · [Back to Flyweight](flyweight.md)
