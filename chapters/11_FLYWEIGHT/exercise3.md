---
layout: default
title: "Flyweight Exercise 3: Extrinsic State, Registry, and Real-World Pressures"
---

# Flyweight Exercise 3: Extrinsic State, Registry, and Real-World Pressures

## Where we are

Exercise 2 gave us a working Flyweight: a factory that caches `ParticleType` objects,
and lightweight `Particle` contexts that hold only unique state.

This exercise adds three realistic pressures that come up in real codebases:

1. **Extrinsic state passed into flyweight methods** — instead of the context always
   forwarding to the flyweight, sometimes the flyweight needs to *act on* per-particle
   data. This requires passing extrinsic state in at call time.

2. **An extensible type registry** — right now the three types are hardcoded in
   `_CONFIGS`. A real engine lets you register new particle types at runtime without
   editing the factory.

3. **Dead particle cleanup** — particles have a lifetime. The scene needs to remove
   dead particles and spawn new ones, all while keeping the flyweight count stable.

---

## Starting code

Begin from your Exercise 2 solution (or `exercise_solution2.py`).

```python
# exercise3.py — build on your Exercise 2 solution
```

---

## Tasks

### Part A — pass extrinsic state into the flyweight

Currently `render` is a module-level function that loops over particles. In a real engine,
rendering logic often lives on the type itself, because the type knows its blend mode,
texture, and mesh — but it also needs per-particle position, which it does not own.

Add a `draw(self, x: float, y: float, lifetime: float) -> str` method to `ParticleType`.
It should return a string describing what it would render. The caller (the scene loop)
passes in the extrinsic state.

```python
@dataclass(frozen=True)
class ParticleType:
    # ... existing fields ...

    def draw(self, x: float, y: float, lifetime: float) -> str:
        """Render this particle type at the given position with the given lifetime.

        x, y, lifetime are extrinsic — they come from the Particle context.
        texture_data, blend_mode, color are intrinsic — they live on self.
        """
        # TODO: return a string like:
        # "flame at (120.3, 340.1) lifetime=1.82s [additive, rgb(255,140,0)]"
        ...
```

Then update `render` to call `p.particle_type_ref.draw(p.x, p.y, p.lifetime)` rather
than accessing fields manually.

---

### Part B — make the registry extensible

Replace `_CONFIGS` with a proper registry on the factory. It should support:

- `ParticleTypeFactory.register(name, color, texture_data, blend_mode, mesh_vertices)`
  — register a new type. Raises `ValueError` if the name is already registered.
- `ParticleTypeFactory.get(name)` — unchanged interface, but now raises a clear
  `ValueError("Unknown particle type: 'lava'")` instead of a raw `KeyError`.
- `ParticleTypeFactory.available_types()` — returns the set of registered type names.

Pre-register the three built-in types at import time so existing code keeps working.

```python
class ParticleTypeFactory:
    _cache: dict[str, ParticleType] = {}
    _registry: dict[str, dict] = {}   # name -> config dict

    @classmethod
    def register(cls, name: str, color, texture_data: bytes,
                 blend_mode: str, mesh_vertices) -> None:
        # TODO: add to _registry; raise ValueError if already registered
        ...

    @classmethod
    def get(cls, name: str) -> ParticleType:
        # TODO: raise ValueError with a clear message if name not in _registry
        # TODO: lazy-create and cache the ParticleType
        ...

    @classmethod
    def available_types(cls) -> set[str]:
        # TODO
        ...

    @classmethod
    def instance_count(cls) -> int:
        ...

    @classmethod
    def clear(cls) -> None:
        """Reset for testing. Do not call in production."""
        cls._cache.clear()
        cls._registry.clear()


# Pre-register built-in types at module level
ParticleTypeFactory.register(
    "flame",
    color=(255, 140, 0),
    texture_data=load_texture("flame"),
    blend_mode="additive",
    mesh_vertices=tuple(load_mesh("flame")),
)
ParticleTypeFactory.register(
    "ember",
    color=(255, 200, 50),
    texture_data=load_texture("ember"),
    blend_mode="additive",
    mesh_vertices=tuple(load_mesh("ember")),
)
ParticleTypeFactory.register(
    "smoke",
    color=(100, 100, 100),
    texture_data=load_texture("smoke"),
    blend_mode="alpha",
    mesh_vertices=tuple(load_mesh("smoke")),
)
```

---

### Part C — implement the scene loop with dead-particle cleanup

A real scene spawns particles, simulates them, removes dead ones, and keeps spawning.
Implement the `Scene` class below. The Flyweight count must never exceed the number of
registered types, even after many spawn-and-die cycles.

```python
class Scene:
    def __init__(self):
        self.particles: list[Particle] = []

    def spawn(self, particle_type: str, count: int = 1) -> None:
        """Spawn `count` new particles of the given type."""
        # TODO
        ...

    def tick(self, dt: float) -> None:
        """Advance simulation and remove dead particles (lifetime <= 0)."""
        # TODO: simulate all particles
        # TODO: remove particles where lifetime <= 0
        ...

    def render(self) -> list[str]:
        """Return render strings for all living particles."""
        # TODO: call particle_type_ref.draw(...) for each particle
        ...

    def particle_count(self) -> int:
        return len(self.particles)
```

---

### Part D — register a custom type

Use the registry to add a `"spark"` particle type without modifying any existing class.
Then spawn 200 sparks and verify the flyweight count is still just 4.

```python
ParticleTypeFactory.register(
    "spark",
    color=(255, 255, 180),
    texture_data=b"\xff" * 64_000,   # 64KB texture
    blend_mode="additive",
    mesh_vertices=tuple([0.0] * 40),
)

scene = Scene()
scene.spawn("spark", 200)
scene.spawn("flame", 100)

print(f"Particles:         {scene.particle_count()}")
print(f"Flyweight objects: {ParticleTypeFactory.instance_count()}")
# Expected: Flyweight objects: 2  (only "spark" and "flame" were actually requested)
```

---

## Tests

```python
# tests3.py  (run with: python tests3.py)
import random
from exercise3 import ParticleTypeFactory, Scene, Particle

def setup():
    ParticleTypeFactory.clear()
    from exercise3 import load_texture, load_mesh
    for name, color, blend in [
        ("flame", (255, 140, 0), "additive"),
        ("ember", (255, 200, 50), "additive"),
        ("smoke", (100, 100, 100), "alpha"),
    ]:
        ParticleTypeFactory.register(
            name, color=color,
            texture_data=load_texture(name),
            blend_mode=blend,
            mesh_vertices=tuple(load_mesh(name)),
        )

def test_draw_returns_string():
    setup()
    pt = ParticleTypeFactory.get("flame")
    result = pt.draw(x=10.0, y=20.0, lifetime=1.5)
    assert isinstance(result, str)
    assert "flame" in result
    assert "10" in result or "10.0" in result
    print("PASS test_draw_returns_string")

def test_unknown_type_raises():
    setup()
    try:
        ParticleTypeFactory.get("lava")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "lava" in str(e)
    print("PASS test_unknown_type_raises")

def test_duplicate_register_raises():
    setup()
    try:
        ParticleTypeFactory.register(
            "flame", color=(0,0,0), texture_data=b"", blend_mode="alpha", mesh_vertices=()
        )
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    print("PASS test_duplicate_register_raises")

def test_available_types():
    setup()
    types = ParticleTypeFactory.available_types()
    assert "flame" in types
    assert "ember" in types
    assert "smoke" in types
    print("PASS test_available_types")

def test_scene_removes_dead_particles():
    setup()
    scene = Scene()
    scene.spawn("flame", 10)
    assert scene.particle_count() == 10
    # Force all particles to expire
    for p in scene.particles:
        p.lifetime = 0.001
    scene.tick(dt=1.0)
    assert scene.particle_count() == 0
    print("PASS test_scene_removes_dead_particles")

def test_flyweight_count_stable_across_spawn_cycles():
    setup()
    scene = Scene()
    for _ in range(20):
        scene.spawn("flame", 50)
        scene.spawn("smoke", 30)
        scene.tick(dt=0.1)
    # No matter how many spawn cycles, only the used types are flyweights
    assert ParticleTypeFactory.instance_count() <= 2
    print("PASS test_flyweight_count_stable_across_spawn_cycles")

def test_custom_type_registration():
    setup()
    ParticleTypeFactory.register(
        "spark",
        color=(255, 255, 180),
        texture_data=b"\xff" * 64_000,
        blend_mode="additive",
        mesh_vertices=tuple([0.0] * 40),
    )
    assert "spark" in ParticleTypeFactory.available_types()
    pt = ParticleTypeFactory.get("spark")
    assert pt.color == (255, 255, 180)
    result = pt.draw(x=5.0, y=5.0, lifetime=0.5)
    assert "spark" in result
    print("PASS test_custom_type_registration")

def test_render_returns_one_string_per_particle():
    setup()
    scene = Scene()
    scene.spawn("flame", 5)
    scene.spawn("ember", 3)
    lines = scene.render()
    assert len(lines) == 8
    print("PASS test_render_returns_one_string_per_particle")

if __name__ == "__main__":
    test_draw_returns_string()
    test_unknown_type_raises()
    test_duplicate_register_raises()
    test_available_types()
    test_scene_removes_dead_particles()
    test_flyweight_count_stable_across_spawn_cycles()
    test_custom_type_registration()
    test_render_returns_one_string_per_particle()
    print("\nAll tests passed.")
```

---

## What you are practising

- Passing extrinsic state into flyweight methods at call time (not storing it on the flyweight)
- Building an extensible registry that separates registration from instantiation
- Managing the lifecycle of context objects while flyweights remain stable
- Verifying that the flyweight count is always bounded by the number of *types*, not *instances*

The key insight for Part A: the flyweight's method signature changes shape. Instead of
`draw(self)` reading `self.x`, it becomes `draw(self, x, y, lifetime)`. The flyweight
does not own the extrinsic data — it *receives* it. This is the canonical Flyweight method
signature pattern.

---

[Exercise 2](exercise2.md) · [Back to Flyweight](flyweight.md)
