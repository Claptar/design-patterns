"""
Flyweight Exercise 2 — The Factory That Enforces Sharing

Your tasks are in exercise2.md.
"""

from dataclasses import dataclass
import random


# ---------------------------------------------------------------------------
# These two classes come from your Exercise 1 solution. Do not change them.
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Helper functions — do not change these.
# ---------------------------------------------------------------------------

def load_texture(particle_type: str) -> bytes:
    """Simulate loading a texture from disk."""
    sizes = {"flame": 512_000, "ember": 128_000, "smoke": 256_000}
    return bytes(sizes[particle_type])


def load_mesh(particle_type: str) -> list[float]:
    """Simulate loading mesh geometry."""
    counts = {"flame": 200, "ember": 80, "smoke": 160}
    return [0.0] * counts[particle_type]


_CONFIGS = {
    "flame": {"color": (255, 140,   0), "blend_mode": "additive"},
    "ember": {"color": (255, 200,  50), "blend_mode": "additive"},
    "smoke": {"color": (100, 100, 100), "blend_mode": "alpha"},
}


# ---------------------------------------------------------------------------
# Part A — implement ParticleTypeFactory.
# ---------------------------------------------------------------------------

class ParticleTypeFactory:
    _cache: dict[str, ParticleType] = {}

    @classmethod
    def get(cls, name: str) -> ParticleType:
        """Return the cached ParticleType for name, creating it if necessary."""
        # TODO: if name is not in _cache, create the ParticleType and store it
        # TODO: return the cached instance
        ...

    @classmethod
    def instance_count(cls) -> int:
        """Return how many flyweight objects have been created."""
        # TODO
        ...


# ---------------------------------------------------------------------------
# Part B — update create_particle to use the factory.
# ---------------------------------------------------------------------------

def create_particle(particle_type: str) -> Particle:
    """Create one particle. The ParticleType must come from the factory."""
    # TODO: get the ParticleType from ParticleTypeFactory (not constructing new)
    # TODO: return a Particle with random x, y, vx, vy, lifetime
    ...


# ---------------------------------------------------------------------------
# Part D — implement simulate and render.
# ---------------------------------------------------------------------------

def simulate(particles: list[Particle], dt: float) -> None:
    """Advance all particles by one time step."""
    # TODO: update x, y by velocity; decrease lifetime by dt
    ...


def render(particles: list[Particle]) -> None:
    """Pretend to render all particles (access texture and mesh via the ref)."""
    # TODO: for each particle, "use" particle.particle_type_ref.texture_data
    #       and particle.particle_type_ref.mesh_vertices
    ...


# ---------------------------------------------------------------------------
# Part C — memory measurement. Run with: python exercise2.py
# ---------------------------------------------------------------------------

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
