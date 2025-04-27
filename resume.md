# ParticleField: Pure Python GPU-Accelerated Renderer

## Overview

We will build a pure-Python, GPU-accelerated particle morphing library inspired by the Three.js reference implementation. This library will enable real-time, animatable point-cloud visualization and morphing entirely from Python, without a browser.

Key features:
- Shape generation (sphere, cube, pyramid, torus, galaxy, wave) via NumPy
- Morphing between shapes with noise-driven intermediate states
- Color schemes (fire, neon, nature, rainbow) driven by HSL and noise
- Real-time rendering using VisPy with custom GLSL shaders
- Python-friendly API: `set_shape()`, `set_color()`, `trigger_morph()`, `load_custom_points()`
- Modular architecture for future extensions: TTS/emotion modules, AI-driven interactions, custom data inputs

## Dependencies

- Python 3.8+
- numpy
- opensimplex
- vispy (or alternately pyglet + moderngl)
- (optional) colorcet or matplotlib for palettes

## Step-by-Step Plan

1. Project scaffolding
   - Create package skeleton (`particle_field/`)
   - Add `pyproject.toml` or `setup.py` with dependencies
   - Set up basic CI (e.g., GitHub Actions) and pre-commit hooks

2. Shape generators
   - Port each JS generator to NumPy functions:
     - `generate_sphere(count, size)`
     - `generate_cube(count, size)`
     - `generate_pyramid(count, size)`
     - `generate_torus(count, size)`
     - `generate_galaxy(count, size)`
     - `generate_wave(count, size)`

3. ParticleField core
   - Develop `ParticleField` class
   - Initialize a VisPy `SceneCanvas` and `Markers` visual for points
   - Manage GPU buffers for positions, colors, sizes

4. Morph logic
   - Maintain arrays: `source_positions`, `target_positions`, `swarm_positions`
   - Implement noise-driven swarm interpolation
   - Use a timer callback (VisPy `canvas.app.Timer`) to update positions over time

5. Color schemes
   - Implement HSL-based coloring with noise perturbations
   - Expose color schemes: `fire`, `neon`, `nature`, `rainbow`

6. API methods
   - `set_shape(name: str)`
   - `set_color(scheme: str)`
   - `trigger_morph(duration_ms: int = 4000)`
   - `load_custom_points(points: np.ndarray)`

7. Demo script
   - Write `examples/demo.py` to launch a `ParticleField` instance
   - Showcase shape morphing, color changes

8. Iteration and extensions
   - Hook up TTS/emotion modules
   - Integrate AI chat loop to push new shapes or react in real-time
   - Support arbitrary data sources: chart points, facial landmarks, emoji shapes

Once the scaffolding is ready, we can dive into implementing each module in turn.