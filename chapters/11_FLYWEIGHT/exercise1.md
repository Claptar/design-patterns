---
layout: default
title: "Flyweight Exercise 1: The Particle System Problem"
---

# Flyweight Exercise 1: The Particle System Problem

## Scenario

You are building a 2D game engine. The game renders a campfire scene with thousands of
particles simultaneously: flames, embers, and smoke puffs.

You have been given a working `Particle` class and a simple renderer. It works fine with
a dozen particles. But when the scene scales to 50,000 particles the program starts
consuming gigabytes of RAM and slowing to a crawl.

Your job in this exercise is **not** to fix it yet — it is to understand *why* it is slow
and to lay the groundwork for the Flyweight pattern by identifying which data is shared
and which data is unique.

---

## The starting code

```python
# exercise1.py
from dataclasses import dataclass
import random


@dataclass
class Particle:
    # Position — unique per particle
    x: float
    y: float

    # Velocity — unique per particle
    vx: float
    vy: float

    # Lifetime remaining — unique per particle
    lifetime: float

    # Visual properties — loaded from disk for each particle
    particle_type: str          # "flame", "ember", "smoke"
    color: tuple[int, int, int] # RGB
    texture_data: bytes         # simulated texture (heavy — 512KB per particle)
    blend_mode: str             # "additive", "alpha"
    mesh_vertices: list[float]  # simulated geometry (heavy — ~200 floats)


def load_texture(particle_type: str) -> bytes:
    """Simulate loading a texture from disk. Slow and produces large data."""
    sizes = {"flame": 512_000, "ember": 128_000, "smoke": 256_000}
    return bytes(sizes[particle_type])


def load_mesh(particle_type: str) -> list[float]:
    """Simulate loading mesh geometry. Produces many floats."""
    counts = {"flame": 200, "ember": 80, "smoke": 160}
    return [0.0] * counts[particle_type]


def create_particle(particle_type: str) -> Particle:
    """Create one particle of the given type."""
    configs = {
        "flame": {"color": (255, 140,   0), "blend_mode": "additive"},
        "ember": {"color": (255, 200,  50), "blend_mode": "additive"},
        "smoke": {"color": (100, 100, 100), "blend_mode": "alpha"},
    }
    cfg = configs[particle_type]
    return Particle(
        x=random.uniform(0, 800),
        y=random.uniform(0, 600),
        vx=random.uniform(-1, 1),
        vy=random.uniform(-2, 0),
        lifetime=random.uniform(0.5, 3.0),
        particle_type=particle_type,
        color=cfg["color"],
        texture_data=load_texture(particle_type),   # loaded fresh for every particle
        blend_mode=cfg["blend_mode"],
        mesh_vertices=load_mesh(particle_type),     # loaded fresh for every particle
    )


def simulate(particles: list[Particle], dt: float) -> None:
    """Advance all particles by one time step."""
    for p in particles:
        p.x += p.vx * dt
        p.y += p.vy * dt
        p.lifetime -= dt


def render(particles: list[Particle]) -> None:
    """Pretend to render all particles."""
    for p in particles:
        _ = p.texture_data   # "use" the texture
        _ = p.mesh_vertices  # "use" the mesh
```

---

## Tasks

### Part A — measure the problem

Run the code below and record the memory figures it prints.

```python
import sys
import tracemalloc

tracemalloc.start()

COUNT = 5_000   # try 10_000 if your machine allows it

particles = [
    create_particle(random.choice(["flame", "ember", "smoke"]))
    for _ in range(COUNT)
]

current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(f"Particles:    {COUNT}")
print(f"Current RAM:  {current / 1_048_576:.1f} MB")
print(f"Peak RAM:     {peak / 1_048_576:.1f} MB")
print(f"Per particle: {current / COUNT / 1024:.1f} KB")
```

Write down the numbers. You will compare them against your Flyweight solution in
Exercise 2.

---

### Part B — classify each field

Fill in the table below by deciding whether each `Particle` field is **intrinsic**
(same for all particles of the same type — candidate for the flyweight) or **extrinsic**
(unique per particle — must stay in the context object).

| Field | Intrinsic or Extrinsic? | Reason |
|---|---|---|
| `x` | ? | |
| `y` | ? | |
| `vx` | ? | |
| `vy` | ? | |
| `lifetime` | ? | |
| `particle_type` | ? | |
| `color` | ? | |
| `texture_data` | ? | |
| `blend_mode` | ? | |
| `mesh_vertices` | ? | |

---

### Part C — design the split on paper

Before writing any code, sketch the two classes you will need:

1. `ParticleType` — the flyweight. List only the fields that belong here.
2. `Particle` — the context. List only the fields that belong here, plus a reference
   to its `ParticleType`.

Also answer: how many `ParticleType` objects will exist at runtime, no matter how many
particles are in the scene?

---

### Part D — write a stub

In `exercise1.py`, add empty class stubs for `ParticleType` and update `Particle` so
it has a `particle_type_ref` field pointing at a `ParticleType`. Do not implement the
factory yet — that is Exercise 2. Just make the split clear in the type definitions.

The tests below should pass after your stubs:

```python
# basic_tests.py  (run with: python basic_tests.py)
from exercise1 import ParticleType, Particle

def test_particle_type_exists():
    pt = ParticleType(
        name="flame",
        color=(255, 140, 0),
        texture_data=b"fake",
        blend_mode="additive",
        mesh_vertices=[0.0, 1.0],
    )
    assert pt.name == "flame"
    assert pt.color == (255, 140, 0)
    print("PASS test_particle_type_exists")

def test_particle_has_ref():
    pt = ParticleType(
        name="flame",
        color=(255, 140, 0),
        texture_data=b"fake",
        blend_mode="additive",
        mesh_vertices=[0.0, 1.0],
    )
    p = Particle(x=10.0, y=20.0, vx=0.5, vy=-1.0, lifetime=2.0, particle_type_ref=pt)
    assert p.particle_type_ref is pt
    print("PASS test_particle_has_ref")

def test_particle_has_no_texture():
    import dataclasses
    field_names = {f.name for f in dataclasses.fields(Particle)}
    assert "texture_data" not in field_names, \
        "Particle should not store texture_data — that belongs in ParticleType"
    assert "mesh_vertices" not in field_names, \
        "Particle should not store mesh_vertices — that belongs in ParticleType"
    print("PASS test_particle_has_no_texture")

if __name__ == "__main__":
    test_particle_type_exists()
    test_particle_has_ref()
    test_particle_has_no_texture()
    print("\nAll tests passed.")
```

---

## What you are practising

- Reading existing code and identifying where memory waste comes from
- Distinguishing intrinsic state (shared, immutable) from extrinsic state (unique, mutable)
- Designing the flyweight split before touching the factory

The rule: if the data would be identical in every particle of the same type, it is
intrinsic. If it could differ between two particles of the same type, it is extrinsic.

---

[Exercise 2](exercise2.md) · [Back to Flyweight](flyweight.md)
