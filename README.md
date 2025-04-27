# Particle Field

A pure-Python, GPU-accelerated particle morphing library using VisPy and NumPy. Inspired by a Three.js reference implementation, it supports dynamic shape morphing, noise-driven effects, and flexible color schemes.

## Features
- Multiple built-in shape generators: sphere, cube, pyramid, torus, galaxy, wave
- Smooth morphing with swarm, swirl, and noise effects
- HSL-based color schemes with noise perturbation: fire, neon, nature, rainbow
- Live interactive demo via VisPy `SceneCanvas`
- Python API: `set_shape()`, `set_color()`, `trigger_morph()`, `load_custom_points()`

## Installation
1. Create a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install core dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install the package in editable mode:
   ```bash
   pip install -e .
   ```
4. Install a GUI backend for VisPy (required to open the canvas). We recommend PyQt6:
   ```bash
   pip install PyQt6
   ```

## Usage
Run the interactive demo:
```bash
python3 examples/demo.py
```

### Remote Control Demo
You can also start a TCP JSON controller:
```bash
python3 examples/controller_demo.py
```
Then connect via `netcat`:
```bash
nc localhost 8765
{"command":"set_shape","args":["cube"]}
{"command":"trigger_morph","args":[1500]}
{"command":"express","args":["joy",1.0,2000]}
```

### Jupyter Notebook Demo
Open `examples/demo_notebook.ipynb` in Jupyter (uses VisPy external window):
```bash
jupyter notebook examples/demo_notebook.ipynb
```

```bash
jupyter notebook examples/demo_notebook.ipynb
```

### Controls
- Space or Right Arrow: cycle to next shape and morph
- C: cycle to next color scheme
- Q or Esc: quit

## Examples
Embed `ParticleField` in your own scripts:
```python
from particle_field import ParticleField
field = ParticleField(count=20000, size=15.0)
field.set_shape('galaxy')
field.set_color('rainbow')
field.trigger_morph(3000)
# The VisPy canvas runs its own event loop
```

## Continuous Deployment to PyPI

We use GitHub Actions to automatically publish new versions to PyPI upon creating a Git tag of the form `vX.Y.Z`.

1. Generate a PyPI API token:
   - Login to PyPI, go to Account settings → API tokens → Add Token → give it a name and expire policy.
   - Copy the token.
2. Add the token to your GitHub repository as a secret:
   - In GitHub, go to **Settings → Secrets and variables → Actions → New repository secret**.
   - Name: `PYPI_API_TOKEN`
   - Value: *paste the token here*
3. Tag a new release and push the tag:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```
4. GitHub Actions will build the package and publish to PyPI.

### GitHub Actions Workflow
See `.github/workflows/publish.yml` for the deployment configuration.

## License
This project is MIT licensed. See LICENSE.txt in the reference folder for details.