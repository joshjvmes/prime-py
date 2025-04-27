import numpy as np
import pytest

from particle_field.shapes import (
    generate_sphere,
    generate_cube,
    generate_pyramid,
    generate_torus,
    generate_galaxy,
    generate_wave,
)

@pytest.mark.parametrize("fn,size", [
    (generate_sphere, 1.5),
    (generate_cube, 2.0),
    (generate_pyramid, 3.0),
    (generate_torus, 1.0),
    (generate_galaxy, 2.5),
    (generate_wave, 2.0),
])
def test_point_generator(fn, size):
    count = 1000
    pts = fn(count, size)
    # shape and dtype
    assert isinstance(pts, np.ndarray)
    assert pts.shape == (count, 3)
    assert pts.dtype == np.float32
    # finite values
    assert np.isfinite(pts).all()

def test_sphere_radius():
    pts = generate_sphere(500, 3.0)
    r = np.linalg.norm(pts, axis=1)
    # radius should be <= size (allow small epsilon)
    assert r.max() <= pytest.approx(3.0, rel=1e-2)

def test_cube_bounds():
    size = 4.0
    pts = generate_cube(500, size)
    half = size / 2.0
    assert np.all(pts >= -half - 1e-6)
    assert np.all(pts <= half + 1e-6)

def test_from_points_and_dataframe():
    import pandas as pd
    from particle_field.field import ParticleField

    field = ParticleField(count=10, size=2.0, init_canvas=False)
    # test from_points longer array
    pts = np.array([[1,2,3],[4,5,6]], dtype=np.float32)
    field.from_points(pts, scale=1.0, morph=False)
    assert field.positions.shape == (10,3)
    # test from_dataframe
    df = pd.DataFrame({'x':[0,1,2],'y':[1,2,3]})
    field.from_dataframe(df, x_col='x', y_col='y', z_col=None, scale=2.0, morph=False)
    assert field.positions.shape == (10,3)

def test_set_color():
    from particle_field.field import ParticleField
    field = ParticleField(count=100, size=1.0, init_canvas=False)
    # default color
    field.set_color('fire')
    colors = field.colors
    assert colors.shape == (100,4)
    assert (colors >= 0).all() and (colors <= 1).all()