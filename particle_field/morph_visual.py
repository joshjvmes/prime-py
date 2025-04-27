"""
MorphMarkersVisual: a GPU-based morphing point visual using GLSL.
"""
import numpy as np
from vispy import gloo
from vispy.visuals import Visual
from vispy.visuals.transforms import STTransform

class MorphMarkersVisual(Visual):
    """
    Visual that morphs between three point sets entirely on the GPU.
    Attributes:
      a_source, a_swarm, a_target: vec3 arrays
      a_axis: vec3 rotation axes per point
      a_size: float per point
      a_color: vec3 per point
    Uniforms:
      u_progress: morph interpolation [0,1]
      u_swirl: global swirl intensity
      u_transform: combined projection*view matrix
    """
    VERT_SHADER = """
    attribute vec3 a_source;
    attribute vec3 a_swarm;
    attribute vec3 a_target;
    attribute vec3 a_axis;
    attribute float a_size;
    attribute vec3 a_color;
    uniform float u_progress;
    uniform float u_swirl;
    uniform mat4 u_transform;
    varying vec4 v_color;
    void main() {
        float t = u_progress;
        float ti = 1.0 - t;
        float ti2 = ti * ti;
        float t2 = t * t;
        vec3 p = a_source * ti2 + a_swarm * (2.0 * ti * t) + a_target * t2;
        // swirl around axis
        vec3 v = p - a_source;
        float ang = u_swirl * t;
        float c = cos(ang);
        float s = sin(ang);
        v = v * c + cross(a_axis, v) * s + a_axis * dot(a_axis, v) * (1.0 - c);
        p = a_source + v;
        gl_Position = u_transform * vec4(p, 1.0);
        gl_PointSize = a_size;
        v_color = vec4(a_color, 1.0);
    }
    """
    FRAG_SHADER = """
    varying vec4 v_color;
    void main() {
        gl_FragColor = v_color;
    }
    """

    def __init__(self, source, swarm, target, colors, sizes, axes):
        super().__init__(vcode=self.VERT_SHADER, fcode=self.FRAG_SHADER)
        # Convert inputs to numpy arrays
        N = len(source)
        self.program['a_source'] = gloo.VertexBuffer(np.asarray(source, dtype=np.float32))
        self.program['a_swarm'] = gloo.VertexBuffer(np.asarray(swarm, dtype=np.float32))
        self.program['a_target'] = gloo.VertexBuffer(np.asarray(target, dtype=np.float32))
        self.program['a_axis'] = gloo.VertexBuffer(np.asarray(axes, dtype=np.float32))
        self.program['a_size'] = gloo.VertexBuffer(np.asarray(sizes, dtype=np.float32))
        self.program['a_color'] = gloo.VertexBuffer(np.asarray(colors, dtype=np.float32))
        # Default uniforms
        self.program['u_progress'] = 0.0
        self.program['u_swirl'] = 0.0
        self._transform = STTransform()
        self.transforms.add_transform(self, self._transform)

    def set_progress(self, t: float):
        self.program['u_progress'] = float(t)

    def set_swirl(self, swirl: float):
        self.program['u_swirl'] = float(swirl)

    def set_transform(self, mat):
        # mat: 4x4 numpy
        self.program['u_transform'] = mat.astype(np.float32)
        self._transform.matrix = mat

    def draw(self):
        self.program.draw('points')