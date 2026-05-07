"""
Flyweight Exercise 1 — The Particle System Problem

Your tasks are in exercise1.md.

Parts A, B, C are analysis tasks (no code changes needed for them).

Part D: add ParticleType and update Particle below so the tests in basic_tests.py pass.
"""

from dataclasses import dataclass
import random


# ---------------------------------------------------------------------------
# Part D: Add ParticleType here.
#
# It should hold the fields that are IDENTICAL for every particle of the same
# type — the intrinsic state. Make it immutable (frozen=True on the dataclass).
# ---------------------------------------------------------------------------

# TODO: define ParticleType


# ---------------------------------------------------------------------------
# Part D: Update Particle.
#
# Remove texture_data and mesh_vertices (they belong in ParticleType).
# Add a particle_type_ref field that holds a reference to a ParticleType.
# Keep x, y, vx, vy, lifetime — these are extrinsic (unique per particle).
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Helper functions — do not change these yet.
# ---------------------------------------------------------------------------

def load_texture(particle_type: str) -> bytes:
    """Simulate loading a texture from disk."""
    sizes = {"flame": 512_000, "ember": 128_000, "smoke": 256_000}
    return bytes(sizes[particle_type])


def load_mesh(particle_type: str) -> list[float]:
    """Simulate loading mesh geometry."""
    counts = {"flame": 200, "ember": 80, "smoke": 160}
    return [0.0] * counts[particle_type]


def create_particle(particle_type: str) -> Particle:
    """Create one particle of the given type (naïve version — no sharing yet)."""
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
        texture_data=load_texture(particle_type),
        blend_mode=cfg["blend_mode"],
        mesh_vertices=load_mesh(particle_type),
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
        _ = p.texture_data
        _ = p.mesh_vertices


# ---------------------------------------------------------------------------
# Part A — run this block to measure the memory cost before your changes.
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

    print(f"Particles:    {COUNT}")
    print(f"Current RAM:  {current / 1_048_576:.1f} MB")
    print(f"Peak RAM:     {peak / 1_048_576:.1f} MB")
    print(f"Per particle: {current / COUNT / 1024:.1f} KB")
