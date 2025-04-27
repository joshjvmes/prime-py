"""
particle_field: GPU-accelerated particle morphing library.
"""
try:
    from .field import ParticleField
except ImportError:
    ParticleField = None  # vispy not installed or backend missing
from .shapes import (
    generate_sphere,
    generate_cube,
    generate_pyramid,
    generate_torus,
    generate_galaxy,
    generate_wave,
)

__all__ = [
    "ParticleField",
    "generate_sphere",
    "generate_cube",
    "generate_pyramid",
    "generate_torus",
    "generate_galaxy",
    "generate_wave",
]