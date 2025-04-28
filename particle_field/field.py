import numpy as np
import time
from vispy import scene, app
from vispy.scene import visuals
from opensimplex import OpenSimplex
import colorsys

from .shapes import (
    generate_sphere,
    generate_cube,
    generate_pyramid,
    generate_torus,
    generate_galaxy,
    generate_wave,
)

__all__ = ["ParticleField"]

class ParticleField:
    """
    Core class for the GPU-accelerated particle field.
    """

    def __init__(self, count: int = 15000, size: float = 14.0, use_gpu: bool = False,
                 init_canvas: bool = True):
        """
        ParticleField constructor.
        use_gpu: if True, offload morph to GPU via GLSL; else, use CPU path.
        """
        self.use_gpu = use_gpu
        # placeholder for scatter visual (will be set if init_canvas=True)
        self.scatter = None
        # Whether to initialize the VisPy canvas (disable for headless testing)
        self.init_canvas = init_canvas
        self.count = count
        self.size = size
        from .shapes import (
            generate_sphere, generate_cube, generate_pyramid,
            generate_torus, generate_galaxy, generate_wave,
            generate_helix, generate_lissajous, generate_spiral, generate_trefoil
        )
        self._generators = {
            "sphere": generate_sphere,
            "cube": generate_cube,
            "pyramid": generate_pyramid,
            "torus": generate_torus,
            "galaxy": generate_galaxy,
            "wave": generate_wave,
            "helix": generate_helix,
            "lissajous": generate_lissajous,
            "spiral": generate_spiral,
            "trefoil": generate_trefoil,
        }
        # initial shape and morph state
        self.current_shape = "sphere"
        self.source_positions = self._generators[self.current_shape](self.count, self.size)
        self.target_positions = self.source_positions.copy()
        # current rendered positions
        self.positions = self.source_positions.copy()
        # placeholder for swarm intermediate positions
        self.swarm_positions = self.source_positions.copy()
        self.morphing = False
        self._morph_start = 0.0
        self._morph_duration = 0.0
        # default colors (RGBA)
        self.colors = np.ones((self.count, 4), dtype=np.float32)
        # simplex noise for color perturbation and future effects (seeded for reproducibility)
        self.noise = OpenSimplex(seed=0)
        # morph/swarm configuration
        self.swarm_distance_factor = 1.5
        self.swirl_factor = 4.0
        self.noise_frequency = 0.1
        self.noise_time_scale = 0.04
        self.noise_max_strength = 2.8
        # color schemes: (start_hue, end_hue, base_saturation, base_lightness)
        self.color_schemes = {
            'fire':    (0.0,   45.0, 0.95, 0.6),
            'neon':    (300.0, 180.0, 1.00, 0.65),
            'nature':  (90.0,  160.0, 0.85, 0.55),
            'rainbow': (0.0,   360.0, 0.90, 0.6),
        }
        # active color scheme key
        self.current_color_scheme = 'fire'
        # default morph parameters for express/emotion
        self._default_swirl = self.swirl_factor
        self._default_noise = self.noise_max_strength
        self._default_color = self.current_color_scheme
        # event listeners and morph tracking
        self._listeners = []
        self._was_morphing = False
        # emotion-to-parameter mapping
        self.emotion_configs = {
            'joy':        {'swirl': 6.0,  'noise': 3.0, 'color': 'rainbow'},
            'calm':       {'swirl': 0.2,  'noise': 0.3, 'color': 'nature'},
            'angry':      {'swirl': 8.0,  'noise': 4.0, 'color': 'fire'},
            'neutral':    {'swirl': 0.0,  'noise': 0.0, 'color': 'neon'},
            'surprised':  {'swirl': 5.0,  'noise': 2.5, 'color': 'rainbow'},
            'thoughtful': {'swirl': 0.5,  'noise': 0.2, 'color': 'neon'},
            'sad':        {'swirl': 0.2,  'noise': 0.1, 'color': 'nature'},
            'excited':    {'swirl': 10.0, 'noise': 3.0, 'color': 'rainbow'},
        }
        # initialize VisPy canvas and visuals (if enabled)
        if self.init_canvas:
            self._init_canvas()
            # apply initial colors
            self.set_color(self.current_color_scheme)

    def add_listener(self, callback):
        """Register a listener callback for field events."""
        self._listeners.append(callback)

    def remove_listener(self, callback):
        """Unregister a previously registered listener."""
        self._listeners.remove(callback)

    def _emit(self, event, **kwargs):
        """Emit an event with additional data to all listeners."""
        msg = {'event': event}
        msg.update(kwargs)
        for cb in list(self._listeners):
            try:
                cb(msg)
            except Exception:
                pass

    def _init_canvas(self):
        # Create a VisPy canvas with a turntable camera
        self.canvas = scene.SceneCanvas(title="Particle Field", keys="interactive", show=True)
        self.view = self.canvas.central_widget.add_view()
        self.view.camera = 'turntable'
        # Choose visual: CPU or GPU
        if self.use_gpu:
            from .morph_visual import MorphMarkersVisual
            # Create GPU morph visual
            self.scatter = MorphMarkersVisual(
                source=self.source_positions,
                swarm=self.swarm_positions,
                target=self.target_positions,
                colors=self.colors[:, :3],
                sizes=np.full(self.count, 5.0, dtype=np.float32),
                axes=np.random.normal(size=(self.count, 3)).astype(np.float32),
            )
            # Initialize uniforms
            self.scatter.set_swirl(self.swirl_factor)
            self.scatter.set_progress(0.0)
        else:
            # CPU fallback
            self.scatter = visuals.Markers()
            self.scatter.set_data(self.positions, face_color=self.colors, size=5)
        self.view.add(self.scatter)
        # Timer for updates
        self.timer = app.Timer('auto', connect=self._on_timer, start=True)
        # Apply initial color scheme now that canvas and scatter exist
        try:
            self.set_color(self.current_color_scheme)
        except Exception:
            pass

    def _on_timer(self, event):
        # GPU path: update morph uniforms and redraw
        if self.use_gpu:
            if self.morphing:
                now = time.monotonic()
                elapsed = now - self._morph_start
                t = min(elapsed / self._morph_duration, 1.0) if self._morph_duration > 0 else 1.0
                if t >= 1.0:
                    self.morphing = False
                swirl_amt = self.swirl_factor * t
                self.scatter.set_progress(t)
                self.scatter.set_swirl(swirl_amt)
            # request redraw
            self.canvas.update()
            return
        # Called each frame; update positions/colors if morphing
        if self.morphing:
            now = time.monotonic()
            elapsed = now - self._morph_start
            t = elapsed / self._morph_duration if self._morph_duration > 0 else 1.0
            if t >= 1.0:
                t = 1.0
                self.morphing = False
            # Quadratic bezier interpolation: source -> swarm -> target
            t_inv = 1.0 - t
            t_inv_sq = t_inv * t_inv
            t_sq = t * t
            # swirl and noise intensities
            effect = np.sin(t * np.pi)
            swirl_amt = effect * self.swirl_factor
            noise_amp = effect * self.noise_max_strength
            # elapsed time for noise axis
            morph_time = elapsed
            # If no swirl and no noise, use vectorized bezier interpolation
            if swirl_amt == 0.0 and noise_amp == 0.0:
                self.positions = (
                    self.source_positions * t_inv_sq
                    + self.swarm_positions * (2.0 * t_inv * t)
                    + self.target_positions * t_sq
                )
            else:
                # Per-particle morph with swirl and noise
                for i in range(self.count):
                    src = self.source_positions[i]
                    swm = self.swarm_positions[i]
                    tgt = self.target_positions[i]
                    # bezier blend
                    p = src * t_inv_sq + swm * (2.0 * t_inv * t) + tgt * t_sq
                    # swirl around noise-driven axis
                    if swirl_amt > 0.01:
                        vec = p - src
                        ax = self.noise.noise3(i * 0.02, morph_time * 0.1, 0.0)
                        ay = self.noise.noise3(0.0, i * 0.02, morph_time * 0.1 + 5.0)
                        az = self.noise.noise3(morph_time * 0.1 + 10.0, 0.0, i * 0.02)
                        axis = np.array([ax, ay, az], dtype=np.float32)
                        norm = np.linalg.norm(axis)
                        if norm > 1e-6:
                            axis /= norm
                            angle = swirl_amt * (0.5 + np.random.random() * 0.5)
                            cos_a = np.cos(angle)
                            sin_a = np.sin(angle)
                            vec = (
                                vec * cos_a
                                + np.cross(axis, vec) * sin_a
                                + axis * (np.dot(axis, vec)) * (1.0 - cos_a)
                            )
                            p = src + vec
                    # noise offset
                    if noise_amp > 0.01:
                        nt = morph_time * self.noise_time_scale
                        nx = self.noise.noise4(
                            p[0] * self.noise_frequency,
                            p[1] * self.noise_frequency,
                            p[2] * self.noise_frequency,
                            nt,
                        )
                        ny = self.noise.noise4(
                            p[0] * self.noise_frequency + 100.0,
                            p[1] * self.noise_frequency + 100.0,
                            p[2] * self.noise_frequency + 100.0,
                            nt,
                        )
                        nz = self.noise.noise4(
                            p[0] * self.noise_frequency + 200.0,
                            p[1] * self.noise_frequency + 200.0,
                            p[2] * self.noise_frequency + 200.0,
                            nt,
                        )
                        p += np.array([nx, ny, nz], dtype=np.float32) * noise_amp
                    self.positions[i] = p
            # update colors and (if any) scatter visual on CPU path
            self._update_colors()
            if self.scatter is not None:
                try:
                    self.scatter.set_data(self.positions, face_color=self.colors, size=5)
                except Exception:
                    pass

    def set_shape(self, name: str):
        """
        Set the next target shape by name.
        """
        if name not in self._generators:
            raise ValueError(f"Unknown shape: {name!r}")
        self.current_shape = name
        self.target_positions = self._generators[name](self.count, self.size)

    def set_color(self, scheme: str):
        """
        Set the active color scheme (not yet implemented).
        """
        if scheme not in self.color_schemes:
            raise ValueError(f"Unknown color scheme: {scheme!r}")
        self.current_color_scheme = scheme
        # Recompute colors for current positions
        self._update_colors()
        # Update GPU buffer colors (if scatter visual exists)
        if self.scatter is not None:
            try:
                self.scatter.set_data(self.positions, face_color=self.colors, size=5)
            except Exception:
                pass

    def trigger_morph(self, duration_ms: int = 4000):
        """
        Begin morph from current to target positions over duration.
        """
        # Prepare morph: compute source, swarm, and target positions
        self.source_positions = self.positions.copy()
        # Compute intermediate swarm positions
        center_offset = self.size * getattr(self, 'swarm_distance_factor', 1.5)
        # Ensure swarm_positions array exists
        self.swarm_positions = np.zeros_like(self.source_positions)
        for i in range(self.count):
            src = self.source_positions[i]
            tgt = self.target_positions[i]
            # midpoint
            sw = src * 0.5 + tgt * 0.5
            # random offset direction via noise
            od = np.array([
                self.noise.noise3(i * 0.05, 10.0, 10.0),
                self.noise.noise3(20.0, i * 0.05, 20.0),
                self.noise.noise3(30.0, 30.0, i * 0.05),
            ], dtype=np.float32)
            nd = np.linalg.norm(od)
            if nd > 1e-6:
                od /= nd
            dist = np.linalg.norm(src - tgt)
            factor = dist * 0.1 + center_offset
            rnd = 0.5 + np.random.random() * 0.8
            sw = sw + od * (factor * rnd)
            self.swarm_positions[i] = sw
        # Start morph timer
        self._morph_duration = duration_ms / 1000.0
        self._morph_start = time.monotonic()
        self.morphing = True

    def load_custom_points(self, points: np.ndarray):
        """
        Load a custom array of shape (count, 3) as the next target.
        """
        if points.shape != (self.count, 3):
            raise ValueError(f"points must be of shape ({self.count}, 3)")
        self.target_positions = points.astype(np.float32)
        # After loading custom points, optionally start a morph
        try:
            # default morph to custom points
            self.trigger_morph(1000)
        except Exception:
            pass
        return
    
    def from_points(self, pts: np.ndarray, scale: float = 1.0,
                    morph: bool = True, duration_ms: int = 2000):
        """
        Load an arbitrary (N,3) array of points, scale and morph to them.
        Points will be resized by repeating/truncating to match self.count.
        """
        arr = np.asarray(pts, dtype=np.float32) * float(scale)
        # Ensure shape (N,3)
        if arr.ndim != 2 or arr.shape[1] != 3:
            raise ValueError(f"pts must be shape (N,3), got {arr.shape}")
        # Resize to self.count via numpy.resize (pads/truncates)
        pts_resized = np.resize(arr, (self.count, 3))
        self.target_positions = pts_resized
        if morph:
            self.trigger_morph(duration_ms)
        else:
            # instant update
            self.positions = pts_resized.copy()
            # Update scatter if available
            if self.scatter is not None:
                try:
                    self.scatter.set_data(self.positions, face_color=self.colors, size=5)
                except Exception:
                    pass
        return

    def from_dataframe(self, df, x_col='x', y_col='y', z_col=None,
                       scale: float = 1.0, morph: bool = True,
                       duration_ms: int = 2000):
        """
        Load points from a pandas DataFrame using specified columns.
        If z_col is None, z=0 plane.
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required for from_dataframe")
        # Extract columns
        xs = df[x_col].to_numpy()
        ys = df[y_col].to_numpy()
        if z_col is not None and z_col in df.columns:
            zs = df[z_col].to_numpy()
        else:
            zs = np.zeros_like(xs, dtype=np.float32)
        pts = np.stack([xs, ys, zs], axis=1)
        self.from_points(pts, scale=scale, morph=morph, duration_ms=duration_ms)
        return
    
    def express(self, emotion: str, intensity: float = 1.0, duration_ms: int = 2000):
        """
        Temporarily adjust morph parameters and color to express an emotion.
        Restores defaults after `duration_ms`.
        """
        cfg = self.emotion_configs.get(emotion)
        if cfg is None:
            raise ValueError(f"Unknown emotion: {emotion!r}")
        # Set new parameters
        self.swirl_factor = cfg['swirl'] * intensity
        self.noise_max_strength = cfg['noise'] * intensity
        self.set_color(cfg['color'])
        # Schedule revert (only if canvas/timer backend initialized)
        def _revert(ev=None):
            self.swirl_factor = self._default_swirl
            self.noise_max_strength = self._default_noise
            self.set_color(self._default_color)
        # Use VisPy timer only if canvas/timer system is active
        if self.init_canvas:
            try:
                app.Timer(duration_ms / 1000.0, connect=_revert, start=True)
            except Exception:
                pass
    
    def _update_colors(self):
        """
        Update the RGBA color array based on positions and current scheme.
        """
        start_hue, end_hue, base_sat, base_light = self.color_schemes[self.current_color_scheme]
        max_radius = self.size * 1.1
        # For each particle, compute HSL->RGB with noise perturbation
        for i in range(self.count):
            x, y, z = self.positions[i]
            dist = (x * x + y * y + z * z) ** 0.5
            # Hue mapping
            if self.current_color_scheme == 'rainbow':
                norm_x = (x / max_radius + 1.0) * 0.5
                norm_y = (y / max_radius + 1.0) * 0.5
                norm_z = (z / max_radius + 1.0) * 0.5
                hue = (norm_x * 120.0 + norm_y * 120.0 + norm_z * 120.0) % 360.0
            else:
                t = min(dist, max_radius) / max_radius
                hue = start_hue + t * (end_hue - start_hue)
            # Noise-driven saturation/lightness variation
            n = (self.noise.noise3(x * 0.2, y * 0.2, z * 0.2) + 1.0) * 0.5
            sat = max(0.0, min(1.0, base_sat * (0.9 + n * 0.2)))
            light = max(0.1, min(0.9, base_light * (0.85 + n * 0.3)))
            # Convert HSL (hue deg, light, sat) to RGB
            r, g, b = colorsys.hls_to_rgb(hue / 360.0, light, sat)
            self.colors[i, 0] = r
            self.colors[i, 1] = g
            self.colors[i, 2] = b
            self.colors[i, 3] = 1.0