"""
Flyweight Exercise 3 — Extrinsic State, Registry, and Real-World Pressures

Your tasks are in exercise3.md.
"""

from dataclasses import dataclass
import random


# ---------------------------------------------------------------------------
# Helper functions — do not change these.
# ---------------------------------------------------------------------------

def load_texture(particle_type: str) -> bytes:
    sizes = {"flame": 512_000, "ember": 128_000, "smoke": 256_000}
    return bytes(sizes.get(particle_type, 65_536))


def load_mesh(particle_type: str) -> list[float]:
    counts = {"flame": 200, "ember": 80, "smoke": 160}
    return [0.0] * counts.get(particle_type, 40)


# ---------------------------------------------------------------------------
# Part A — add a draw() method to ParticleType.
#
# draw(self, x, y, lifetime) receives extrinsic state at call time.
# It should NOT store x, y, or lifetime on self.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ParticleType:
    name: str
    color: tuple[int, int, int]
    texture_data: bytes
    blend_mode: str
    mesh_vertices: tuple[float, ...]

    def draw(self, x: float, y: float, lifetime: float) -> str:
        """Return a render description string.

        x, y, lifetime are extrinsic — passed in from the Particle context.
        color, blend_mode, texture_data are intrinsic — read from self.
        """
        # TODO: return something like:
        # "flame at (120.3, 340.1) lifetime=1.82s [additive, rgb(255,140,0)]"
        ...


# ---------------------------------------------------------------------------
# Particle (context) — unchanged from Exercise 2.
# ---------------------------------------------------------------------------

@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    lifetime: float
    particle_type_ref: ParticleType


# ---------------------------------------------------------------------------
# Part B — extensible factory with register() and available_types().
# ---------------------------------------------------------------------------

class ParticleTypeFactory:
    _cache: dict[str, ParticleType] = {}
    _registry: dict[str, dict] = {}

    @classmethod
    def register(
        cls,
        name: str,
        color: tuple[int, int, int],
        texture_data: bytes,
        blend_mode: str,
        mesh_vertices: tuple[float, ...],
    ) -> None:
        """Register a new particle type.

        Raises ValueError if the name is already registered.
        """
        # TODO
        ...

    @classmethod
    def get(cls, name: str) -> ParticleType:
        """Return the cached ParticleType for name.

        Raises ValueError with a clear message if name is not registered.
        """
        # TODO: raise ValueError("Unknown particle type: 'lava'") if not found
        # TODO: lazy-create and cache on first access
        ...

    @classmethod
    def available_types(cls) -> set[str]:
        """Return the set of registered type names."""
        # TODO
        ...

    @classmethod
    def instance_count(cls) -> int:
        """Return how many flyweights have been instantiated (not just registered)."""
        return len(cls._cache)

    @classmethod
    def clear(cls) -> None:
        """Reset factory state. Use in tests only."""
        cls._cache.clear()
        cls._registry.clear()


# Pre-register the three built-in types.
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


# ---------------------------------------------------------------------------
# Part C — Scene with spawn, tick (dead-particle cleanup), and render.
# ---------------------------------------------------------------------------

class Scene:
    def __init__(self):
        self.particles: list[Particle] = []

    def spawn(self, particle_type: str, count: int = 1) -> None:
        """Spawn `count` new particles of the given type."""
        # TODO
        ...

    def tick(self, dt: float) -> None:
        """Advance simulation by dt and remove dead particles (lifetime <= 0)."""
        # TODO: simulate all particles
        # TODO: remove dead particles
        ...

    def render(self) -> list[str]:
        """Return a render string for each living particle."""
        # TODO: call particle_type_ref.draw(p.x, p.y, p.lifetime) for each particle
        ...

    def particle_count(self) -> int:
        return len(self.particles)


# ---------------------------------------------------------------------------
# Part D — register a custom type and verify flyweight count.
# Run with: python exercise3.py
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    ParticleTypeFactory.register(
        "spark",
        color=(255, 255, 180),
        texture_data=b"\xff" * 64_000,
        blend_mode="additive",
        mesh_vertices=tuple([0.0] * 40),
    )

    scene = Scene()
    scene.spawn("spark", 200)
    scene.spawn("flame", 100)

    print(f"Registered types:  {sorted(ParticleTypeFactory.available_types())}")
    print(f"Particles:         {scene.particle_count()}")
    print(f"Flyweight objects: {ParticleTypeFactory.instance_count()}")
    print(f"(Expected: 2 — only spark and flame were requested)")
    print()

    lines = scene.render()
    print("First 3 render lines:")
    for line in lines[:3]:
        print(f"  {line}")

    scene.tick(dt=0.1)
    print(f"\nAfter tick — particles alive: {scene.particle_count()}")
