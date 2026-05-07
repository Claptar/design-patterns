"""
Flyweight Exercise 1 — Solution

Key decisions:
- ParticleType is frozen so it cannot be accidentally mutated (which would silently
  change the appearance of every particle sharing it).
- Particle no longer holds texture_data or mesh_vertices — those live in ParticleType.
- particle_type_ref replaces the old particle_type string + the heavy fields.
"""

from dataclasses import dataclass
import random


# ---------------------------------------------------------------------------
# ParticleType — the flyweight (intrinsic state only).
#
# frozen=True means:
#   1. It is hashable (can be used as a dict key or set member).
#   2. It cannot be mutated after creation — safe to share between many Particles.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ParticleType:
    name: str
    color: tuple[int, int, int]
    texture_data: bytes
    blend_mode: str
    mesh_vertices: tuple[float, ...]   # tuple, not list, so the dataclass stays hashable


# ---------------------------------------------------------------------------
# Particle — the context (extrinsic state only + reference to flyweight).
# ---------------------------------------------------------------------------

@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    lifetime: float
    particle_type_ref: ParticleType   # shared flyweight — NOT a copy


# ---------------------------------------------------------------------------
# Helper functions (unchanged from exercise skeleton).
# ---------------------------------------------------------------------------

def load_texture(particle_type: str) -> bytes:
    sizes = {"flame": 512_000, "ember": 128_000, "smoke": 256_000}
    return bytes(sizes[particle_type])


def load_mesh(particle_type: str) -> list[float]:
    counts = {"flame": 200, "ember": 80, "smoke": 160}
    return [0.0] * counts[particle_type]


# ---------------------------------------------------------------------------
# create_particle updated to use the new split.
# Note: there is still no factory here — sharing is not enforced yet.
# We'll fix that in Exercise 2.
# ---------------------------------------------------------------------------

def make_particle_type(name: str) -> ParticleType:
    configs = {
        "flame": {"color": (255, 140,   0), "blend_mode": "additive"},
        "ember": {"color": (255, 200,  50), "blend_mode": "additive"},
        "smoke": {"color": (100, 100, 100), "blend_mode": "alpha"},
    }
    cfg = configs[name]
    return ParticleType(
        name=name,
        color=cfg["color"],
        texture_data=load_texture(name),
        blend_mode=cfg["blend_mode"],
        mesh_vertices=tuple(load_mesh(name)),
    )


def create_particle(particle_type_ref: ParticleType) -> Particle:
    return Particle(
        x=random.uniform(0, 800),
        y=random.uniform(0, 600),
        vx=random.uniform(-1, 1),
        vy=random.uniform(-2, 0),
        lifetime=random.uniform(0.5, 3.0),
        particle_type_ref=particle_type_ref,
    )


def simulate(particles: list[Particle], dt: float) -> None:
    for p in particles:
        p.x += p.vx * dt
        p.y += p.vy * dt
        p.lifetime -= dt


def render(particles: list[Particle]) -> None:
    for p in particles:
        _ = p.particle_type_ref.texture_data
        _ = p.particle_type_ref.mesh_vertices


if __name__ == "__main__":
    import tracemalloc

    tracemalloc.start()

    # Still not sharing — creating a fresh ParticleType per particle.
    # Sharing is Exercise 2's job. This just validates the split.
    COUNT = 5_000
    particles = [
        create_particle(make_particle_type(random.choice(["flame", "ember", "smoke"])))
        for _ in range(COUNT)
    ]

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"Particles:    {COUNT}")
    print(f"Current RAM:  {current / 1_048_576:.1f} MB")
    print(f"Peak RAM:     {peak / 1_048_576:.1f} MB")
    print(f"Per particle: {current / COUNT / 1024:.1f} KB")
    print()
    print("Note: memory is still high here — sharing comes in Exercise 2.")
