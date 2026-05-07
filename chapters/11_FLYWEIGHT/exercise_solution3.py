"""
Flyweight Exercise 3 — Solution
"""

from dataclasses import dataclass
import random


def load_texture(particle_type: str) -> bytes:
    sizes = {"flame": 512_000, "ember": 128_000, "smoke": 256_000}
    return bytes(sizes.get(particle_type, 65_536))


def load_mesh(particle_type: str) -> list[float]:
    counts = {"flame": 200, "ember": 80, "smoke": 160}
    return [0.0] * counts.get(particle_type, 40)


# ---------------------------------------------------------------------------
# Part A — ParticleType with draw() that receives extrinsic state.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ParticleType:
    name: str
    color: tuple[int, int, int]
    texture_data: bytes
    blend_mode: str
    mesh_vertices: tuple[float, ...]

    def draw(self, x: float, y: float, lifetime: float) -> str:
        """Render this particle type at the given position.

        x, y, lifetime are extrinsic — they come from the caller (Particle context).
        color, blend_mode, texture_data are intrinsic — they live on self.

        This is the canonical Flyweight method shape:
            flyweight.operation(extrinsic_state)
        The flyweight acts on per-instance data it does not own.
        """
        r, g, b = self.color
        return (
            f"{self.name} at ({x:.1f}, {y:.1f}) "
            f"lifetime={lifetime:.2f}s "
            f"[{self.blend_mode}, rgb({r},{g},{b})]"
        )


# ---------------------------------------------------------------------------
# Particle — unchanged.
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
# Part B — extensible factory.
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
        if name in cls._registry:
            raise ValueError(f"Particle type '{name}' is already registered")
        cls._registry[name] = {
            "color": color,
            "texture_data": texture_data,
            "blend_mode": blend_mode,
            "mesh_vertices": mesh_vertices,
        }

    @classmethod
    def get(cls, name: str) -> ParticleType:
        if name not in cls._registry:
            raise ValueError(
                f"Unknown particle type: '{name}'. "
                f"Available: {sorted(cls._registry)}"
            )
        if name not in cls._cache:
            cfg = cls._registry[name]
            cls._cache[name] = ParticleType(
                name=name,
                color=cfg["color"],
                texture_data=cfg["texture_data"],
                blend_mode=cfg["blend_mode"],
                mesh_vertices=cfg["mesh_vertices"],
            )
        return cls._cache[name]

    @classmethod
    def available_types(cls) -> set[str]:
        return set(cls._registry)

    @classmethod
    def instance_count(cls) -> int:
        return len(cls._cache)

    @classmethod
    def clear(cls) -> None:
        cls._cache.clear()
        cls._registry.clear()


# Pre-register built-in types.
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
# Part C — Scene.
# ---------------------------------------------------------------------------

class Scene:
    def __init__(self):
        self.particles: list[Particle] = []

    def spawn(self, particle_type: str, count: int = 1) -> None:
        pt = ParticleTypeFactory.get(particle_type)
        for _ in range(count):
            self.particles.append(Particle(
                x=random.uniform(0, 800),
                y=random.uniform(0, 600),
                vx=random.uniform(-1, 1),
                vy=random.uniform(-2, 0),
                lifetime=random.uniform(0.5, 3.0),
                particle_type_ref=pt,
            ))

    def tick(self, dt: float) -> None:
        for p in self.particles:
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.lifetime -= dt
        # Remove dead particles in one pass — no intermediate list needed.
        self.particles = [p for p in self.particles if p.lifetime > 0]

    def render(self) -> list[str]:
        return [
            p.particle_type_ref.draw(p.x, p.y, p.lifetime)
            for p in self.particles
        ]

    def particle_count(self) -> int:
        return len(self.particles)


# ---------------------------------------------------------------------------
# Part D — custom type registration.
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
