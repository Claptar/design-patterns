---
layout: default
title: "Flyweight Exercise 2: The Factory That Enforces Sharing"
---

# Flyweight Exercise 2: The Factory That Enforces Sharing

## Where we are

In Exercise 1 you split `Particle` into two classes:

- `ParticleType` — holds intrinsic state (texture, mesh, color, blend mode)
- `Particle` — holds extrinsic state (position, velocity, lifetime) + a reference

But the split alone does not save memory. If every call to `create_particle` constructs
a brand-new `ParticleType`, you still end up with 5,000 separate texture objects in RAM.

The factory is what makes sharing real. It ensures that there is exactly one `ParticleType`
per unique type name, no matter how many particles are created.

---

## Starting code

Copy your `ParticleType` and `Particle` from Exercise 1 (or use the provided solution),
then build the factory and the new `create_particle` function in `exercise2.py`.

```python
# exercise2.py  — start from your Exercise 1 solution
from dataclasses import dataclass
import random


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


def load_texture(particle_type: str) -> bytes:
    sizes = {"flame": 512_000, "ember": 128_000, "smoke": 256_000}
    return bytes(sizes[particle_type])


def load_mesh(particle_type: str) -> list[float]:
    counts = {"flame": 200, "ember": 80, "smoke": 160}
    return [0.0] * counts[particle_type]
```

---

## Tasks

### Part A — implement the factory

Add a `ParticleTypeFactory` class with a single class method `get(name)`.

Rules:
- The first call to `get("flame")` must create the `ParticleType` and cache it.
- Every subsequent call to `get("flame")` must return the **same object** (use `is`, not `==`).
- The factory must work for all three types: `"flame"`, `"ember"`, `"smoke"`.
- Add a class method `instance_count()` that returns how many flyweights are cached.

```python
class ParticleTypeFactory:
    _cache: dict[str, ParticleType] = {}

    @classmethod
    def get(cls, name: str) -> ParticleType:
        # TODO: implement
        ...

    @classmethod
    def instance_count(cls) -> int:
        # TODO: implement
        ...
```

---

### Part B — wire up create_particle

Update `create_particle` so it uses the factory instead of constructing a fresh
`ParticleType` each time.

```python
def create_particle(particle_type: str) -> Particle:
    # TODO: get the ParticleType from the factory (not constructing a new one)
    # then return a Particle with random position, velocity, and lifetime
    ...
```

---

### Part C — measure the improvement

Add this measurement block to the bottom of `exercise2.py` and run it.
Compare the numbers against your Exercise 1 baseline.

```python
if __name__ == "__main__":
    import tracemalloc

    tracemalloc.start()

    COUNT = 5_000
    particles = [
        create_particle(random.choice(["flame", "ember", "smoke"]))
        for _ in range(COUNT)
    ]

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"Particles:          {COUNT}")
    print(f"Flyweight objects:  {ParticleTypeFactory.instance_count()}")
    print(f"Current RAM:        {current / 1_048_576:.2f} MB")
    print(f"Peak RAM:           {peak / 1_048_576:.2f} MB")
    print(f"Per particle:       {current / COUNT:.0f} bytes")
```

You should see `Flyweight objects: 3` and a per-particle cost of roughly 200–300 bytes
(position, velocity, lifetime, a pointer) rather than hundreds of kilobytes.

---

### Part D — simulate and render

Implement `simulate` and `render` using the new split. Notice that `render` must now
reach into `particle.particle_type_ref` to get the texture and mesh.

```python
def simulate(particles: list[Particle], dt: float) -> None:
    # TODO: update x, y, lifetime for every particle
    ...


def render(particles: list[Particle]) -> None:
    # TODO: "use" the texture and mesh from each particle's ParticleType
    ...
```

---

## Tests

```python
# tests2.py  (run with: python tests2.py)
import random
from exercise2 import ParticleTypeFactory, Particle, create_particle

def test_factory_returns_same_object():
    a = ParticleTypeFactory.get("flame")
    b = ParticleTypeFactory.get("flame")
    assert a is b, "Factory must return the same object for the same type"
    print("PASS test_factory_returns_same_object")

def test_factory_returns_different_objects_for_different_types():
    flame = ParticleTypeFactory.get("flame")
    smoke = ParticleTypeFactory.get("smoke")
    assert flame is not smoke
    print("PASS test_factory_returns_different_objects_for_different_types")

def test_instance_count_caps_at_three():
    for _ in range(100):
        ParticleTypeFactory.get(random.choice(["flame", "ember", "smoke"]))
    assert ParticleTypeFactory.instance_count() == 3, \
        f"Expected 3 flyweights, got {ParticleTypeFactory.instance_count()}"
    print("PASS test_instance_count_caps_at_three")

def test_particles_share_type():
    p1 = create_particle("flame")
    p2 = create_particle("flame")
    assert p1.particle_type_ref is p2.particle_type_ref, \
        "Two flame particles must share the same ParticleType object"
    print("PASS test_particles_share_type")

def test_particles_have_independent_positions():
    random.seed(42)
    p1 = create_particle("ember")
    p2 = create_particle("ember")
    # Positions are randomised — extremely unlikely to be identical
    assert (p1.x, p1.y) != (p2.x, p2.y)
    print("PASS test_particles_have_independent_positions")

def test_particle_has_no_texture_field():
    import dataclasses
    field_names = {f.name for f in dataclasses.fields(Particle)}
    assert "texture_data" not in field_names
    assert "mesh_vertices" not in field_names
    print("PASS test_particle_has_no_texture_field")

if __name__ == "__main__":
    test_factory_returns_same_object()
    test_factory_returns_different_objects_for_different_types()
    test_instance_count_caps_at_three()
    test_particles_share_type()
    test_particles_have_independent_positions()
    test_particle_has_no_texture_field()
    print("\nAll tests passed.")
```

---

## What you are practising

- Implementing a flyweight factory with a cache
- Ensuring that the factory — not the caller — controls object creation
- Verifying identity (`is`) not just equality (`==`)
- Measuring actual memory savings

The key insight: the factory is not optional decoration. Without it, callers can
accidentally create duplicate flyweights and the whole pattern fails silently.

---

[Exercise 1](exercise1.md) · [Exercise 3](exercise3.md) · [Back to Flyweight](flyweight.md)
