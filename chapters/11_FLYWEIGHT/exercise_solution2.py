"""
Flyweight Exercise 2 — Solution
"""

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


_CONFIGS = {
    "flame": {"color": (255, 140,   0), "blend_mode": "additive"},
    "ember": {"color": (255, 200,  50), "blend_mode": "additive"},
    "smoke": {"color": (100, 100, 100), "blend_mode": "alpha"},
}


# ---------------------------------------------------------------------------
# Part A — factory implementation.
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Part B — create_particle uses the factory.
# ---------------------------------------------------------------------------

def create_particle(particle_type: str) -> Particle:
    return Particle(
        x=random.uniform(0, 800),
        y=random.uniform(0, 600),
        vx=random.uniform(-1, 1),
        vy=random.uniform(-2, 0),
        lifetime=random.uniform(0.5, 3.0),
        particle_type_ref=ParticleTypeFactory.get(particle_type),
    )


# ---------------------------------------------------------------------------
# Part D — simulate and render.
# ---------------------------------------------------------------------------

def simulate(particles: list[Particle], dt: float) -> None:
    for p in particles:
        p.x += p.vx * dt
        p.y += p.vy * dt
        p.lifetime -= dt


def render(particles: list[Particle]) -> None:
    for p in particles:
        _ = p.particle_type_ref.texture_data    # heavy — but only 3 objects in RAM
        _ = p.particle_type_ref.mesh_vertices


# ---------------------------------------------------------------------------
# Part C — memory measurement.
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
