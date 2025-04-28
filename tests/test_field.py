import numpy as np
import pytest

from particle_field.field import ParticleField

@pytest.mark.parametrize('shape', ['cube', 'galaxy', 'trefoil'])
def test_trigger_morph_cpu(shape):
    # Test CPU morph from initial to target positions completes immediately
    count = 5
    field = ParticleField(count=count, size=1.0, use_gpu=False, init_canvas=False)
    # set a different target shape
    field.set_shape(shape)
    target = field.target_positions.copy()
    # trigger morph with zero duration
    field.trigger_morph(duration_ms=0)
    assert field.morphing is True
    # simulate timer callback
    field._on_timer(event=None)
    # after zero-duration morph, should complete and match target
    assert field.morphing is False
    np.testing.assert_allclose(field.positions, target)

def test_express_sets_params(tmp_path, monkeypatch):
    # Test express sets swirl, noise, and color scheme
    field = ParticleField(count=10, size=1.0, use_gpu=False, init_canvas=False)
    default_swirl = field._default_swirl
    default_noise = field._default_noise
    default_color = field._default_color
    # Choose an emotion
    emotion = 'joy'
    cfg = field.emotion_configs[emotion]
    # Express with half intensity
    intensity = 0.5
    field.express(emotion, intensity=intensity, duration_ms=1)
    # Immediately should apply new parameters
    assert pytest.approx(field.swirl_factor, rel=1e-6) == cfg['swirl'] * intensity
    assert pytest.approx(field.noise_max_strength, rel=1e-6) == cfg['noise'] * intensity
    assert field.current_color_scheme == cfg['color']
    # Defaults remain stored
    assert field._default_swirl == default_swirl
    assert field._default_noise == default_noise
    assert field._default_color == default_color

def test_invalid_shape_raises():
    field = ParticleField(count=5, size=1.0, use_gpu=False, init_canvas=False)
    with pytest.raises(ValueError):
        field.set_shape('unknown_shape')

def test_invalid_express_raises():
    field = ParticleField(count=5, size=1.0, use_gpu=False, init_canvas=False)
    with pytest.raises(ValueError):
        field.express('no_such_emotion', intensity=1.0, duration_ms=100)