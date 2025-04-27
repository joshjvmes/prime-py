import numpy as np

__all__ = [
    "generate_sphere",
    "generate_cube",
    "generate_pyramid",
    "generate_torus",
    "generate_galaxy",
    "generate_wave",
    "generate_helix",
    "generate_lissajous",
    "generate_spiral",
    "generate_trefoil",
]

def generate_sphere(count: int, size: float) -> np.ndarray:
    """
    Generate points on a sphere using the Fibonacci sphere algorithm.
    Returns an array of shape (count, 3) of dtype float32.
    """
    phi = np.pi * (np.sqrt(5) - 1)
    points = np.zeros((count, 3), dtype=np.float32)
    for i in range(count):
        y = 1 - (i / (count - 1)) * 2
        radius = np.sqrt(max(0.0, 1 - y * y))
        theta = phi * i
        x = np.cos(theta) * radius
        z = np.sin(theta) * radius
        points[i, 0] = x * size
        points[i, 1] = y * size
        points[i, 2] = z * size
    return points

def generate_cube(count: int, size: float) -> np.ndarray:
    """
    Generate points randomly distributed on the surface of a cube centered at the origin.
    """
    half = size / 2.0
    faces = np.random.randint(0, 6, size=count)
    u = np.random.uniform(-half, half, size=count)
    v = np.random.uniform(-half, half, size=count)
    points = np.zeros((count, 3), dtype=np.float32)
    # Assign points per face
    # +X face
    mask = (faces == 0)
    points[mask, 0] = half
    points[mask, 1] = u[mask]
    points[mask, 2] = v[mask]
    # -X face
    mask = (faces == 1)
    points[mask, 0] = -half
    points[mask, 1] = u[mask]
    points[mask, 2] = v[mask]
    # +Y face
    mask = (faces == 2)
    points[mask, 0] = u[mask]
    points[mask, 1] = half
    points[mask, 2] = v[mask]
    # -Y face
    mask = (faces == 3)
    points[mask, 0] = u[mask]
    points[mask, 1] = -half
    points[mask, 2] = v[mask]
    # +Z face
    mask = (faces == 4)
    points[mask, 0] = u[mask]
    points[mask, 1] = v[mask]
    points[mask, 2] = half
    # -Z face
    mask = (faces == 5)
    points[mask, 0] = u[mask]
    points[mask, 1] = v[mask]
    points[mask, 2] = -half
    return points

def generate_pyramid(count: int, size: float) -> np.ndarray:
    """
    Generate points randomly on a 4-sided pyramid (square base).
    """
    # Four-sided pyramid: square base and four triangular faces
    half_base = size / 2.0
    height = size * 1.2
    # Apex at top center
    apex = np.array([0.0, height / 2.0, 0.0], dtype=np.float32)
    # Base vertices (order: 0->1->2->3)
    base_vertices = np.array([
        [-half_base, -height / 2.0, -half_base],
        [ half_base, -height / 2.0, -half_base],
        [ half_base, -height / 2.0,  half_base],
        [-half_base, -height / 2.0,  half_base],
    ], dtype=np.float32)
    # Areas for weighting
    base_area = size * size
    side_height = np.sqrt(height * height + half_base * half_base)
    side_area = 0.5 * size * side_height
    total_area = base_area + 4 * side_area
    base_weight = base_area / total_area
    side_weight = side_area / total_area
    points = np.zeros((count, 3), dtype=np.float32)
    for i in range(count):
        r = np.random.random()
        if r < base_weight:
            # sample on base
            u = np.random.random()
            v = np.random.random()
            # bilinear interpolation on square
            p1 = base_vertices[0] * (1 - u) + base_vertices[1] * u
            p2 = base_vertices[3] * (1 - u) + base_vertices[2] * u
            p = p1 * (1 - v) + p2 * v
        else:
            # sample on one of the four triangular faces
            face_index = int((r - base_weight) / side_weight)
            # clamp face_index to [0,3]
            face_index = min(max(face_index, 0), 3)
            v1 = base_vertices[face_index]
            v2 = base_vertices[(face_index + 1) % 4]
            u = np.random.random()
            v = np.random.random()
            # ensure u+v <= 1 for triangle
            if u + v > 1.0:
                u = 1.0 - u
                v = 1.0 - v
            # point on triangle v1->v2->apex
            edge1 = v2 - v1
            edge2 = apex - v1
            p = v1 + edge1 * u + edge2 * v
        points[i] = p
    return points

def generate_torus(count: int, size: float) -> np.ndarray:
    """
    Generate points randomly on a torus.
    """
    # R: major radius, r: minor radius
    R = size * 0.7
    r = size * 0.3
    theta = np.random.uniform(0, 2 * np.pi, size=count)
    phi = np.random.uniform(0, 2 * np.pi, size=count)
    x = (R + r * np.cos(phi)) * np.cos(theta)
    y = r * np.sin(phi)
    z = (R + r * np.cos(phi)) * np.sin(theta)
    return np.stack([x, y, z], axis=1).astype(np.float32)

def generate_galaxy(count: int, size: float) -> np.ndarray:
    """
    Generate points in a spiral galaxy-like distribution.
    """
    # Parameters for spiral galaxy
    arms = 4
    arm_width = 0.6
    bulge_factor = 0.3
    points = np.zeros((count, 3), dtype=np.float32)
    for i in range(count):
        t = np.random.random() ** 1.5
        radius = t * size
        arm_index = np.random.randint(0, arms)
        arm_offset = (arm_index / arms) * 2 * np.pi
        rotation_amount = (radius / size) * 6.0
        angle = arm_offset + rotation_amount
        spread = (np.random.random() - 0.5) * arm_width * (1 - radius / size)
        theta = angle + spread
        x = radius * np.cos(theta)
        z = radius * np.sin(theta)
        y = (np.random.random() - 0.5) * size * 0.1 * (1 - radius / size * bulge_factor)
        points[i, 0] = x
        points[i, 1] = y
        points[i, 2] = z
    return points

def generate_wave(count: int, size: float) -> np.ndarray:
    """
    Generate points in a wave-like pattern on a plane.
    """
    wave_scale = size * 0.4
    frequency = 3.0
    points = np.zeros((count, 3), dtype=np.float32)
    for i in range(count):
        u = np.random.uniform(-1.0, 1.0)
        v = np.random.uniform(-1.0, 1.0)
        x = u * size
        z = v * size
        dist = np.sqrt(u * u + v * v)
        angle = np.arctan2(v, u)
        y = np.sin(dist * np.pi * frequency) * np.cos(angle * 2.0) * wave_scale * (1 - dist)
        points[i, 0] = x
        points[i, 1] = y
        points[i, 2] = z
    return points

def generate_helix(count: int, size: float, turns: int = 3) -> np.ndarray:
    """
    Generate a 3D helix (spiral along y-axis).
    """
    pts = np.zeros((count, 3), dtype=np.float32)
    radius = size * 0.4
    height = size
    for i in range(count):
        t = (i / (count - 1)) * turns * 2 * np.pi
        x = np.cos(t) * radius
        y = (i / (count - 1) - 0.5) * height
        z = np.sin(t) * radius
        pts[i] = [x, y, z]
    return pts

def generate_lissajous(count: int, size: float,
                        ax: int = 3, ay: int = 2,
                        delta: float = np.pi / 2) -> np.ndarray:
    """
    Generate a 2D Lissajous curve on the z=0 plane.
    """
    pts = np.zeros((count, 3), dtype=np.float32)
    for i in range(count):
        t = (i / (count - 1)) * 2 * np.pi
        x = np.sin(ax * t + delta)
        y = np.sin(ay * t)
        pts[i] = [x * size, y * size, 0.0]
    return pts

def generate_spiral(count: int, size: float, turns: int = 5) -> np.ndarray:
    """
    Generate a flat Archimedean spiral in the x-y plane.
    """
    pts = np.zeros((count, 3), dtype=np.float32)
    for i in range(count):
        t = (i / (count - 1)) * turns * 2 * np.pi
        r = (i / (count - 1)) * (size * 0.5)
        x = r * np.cos(t)
        y = r * np.sin(t)
        pts[i] = [x, y, 0.0]
    return pts

def generate_trefoil(count: int, size: float) -> np.ndarray:
    """
    Generate a trefoil knot scaled to the given size.
    """
    pts = np.zeros((count, 3), dtype=np.float32)
    scale = size / 3.0
    for i in range(count):
        t = (i / (count - 1)) * 2 * np.pi
        x = (2 + np.cos(3 * t)) * np.cos(2 * t)
        y = (2 + np.cos(3 * t)) * np.sin(2 * t)
        z = np.sin(3 * t)
        pts[i] = [x * scale, y * scale, z * scale]
    return pts