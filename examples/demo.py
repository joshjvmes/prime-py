#!/usr/bin/env python3
"""
Demo script for the ParticleField library.
Controls:
  Space or Right Arrow: cycle to next shape and morph
  C: cycle to next color scheme
  Q or Esc: quit
"""
import sys
from vispy import app
from particle_field import ParticleField

def main():
    # Initialize field with a moderate number of particles
    # Initialize particle field
    field = ParticleField(count=10000, size=12.0)
    # Performance mode: disable swirl and noise for faster transitions
    field.swirl_factor = 0.0
    field.noise_max_strength = 0.0
    # Available shapes, colors, and emotions
    shapes = list(field._generators.keys())
    colors = list(field.color_schemes.keys())
    emotions = list(field.emotion_configs.keys())
    shape_idx = color_idx = emotion_idx = 0

    def on_key(event):
        nonlocal shape_idx, color_idx, emotion_idx
        key = event.key.name if hasattr(event.key, 'name') else event.key
        if key in (' ', 'Right'):
            # Next shape
            shape_idx = (shape_idx + 1) % len(shapes)
            name = shapes[shape_idx]
            print(f"Morphing to shape: {name}")
            field.set_shape(name)
            field.trigger_morph(2000)
        elif key in ('C', 'c'):
            # Next color
            color_idx = (color_idx + 1) % len(colors)
            scheme = colors[color_idx]
            print(f"Changing color scheme: {scheme}")
            field.set_color(scheme)
        elif key in ('Q', 'q', 'Escape'):
            print("Quitting demo.")
            sys.exit(0)
        elif key in ('E', 'e'):
            # Express emotion
            emotion_idx = (emotion_idx + 1) % len(emotions)
            emo = emotions[emotion_idx]
            print(f"Expressing emotion: {emo}")
            field.express(emo, intensity=1.0, duration_ms=2000)

    # Connect key events
    field.canvas.events.key_press.connect(on_key)

    print("Demo controls:")
    print("  Space/Right -> next shape & morph")
    print("  C -> next color scheme")
    print("  Q/Esc -> quit")
    print("  E -> cycle emotion expression")
    print(f"Starting shape: {shapes[shape_idx]}, color: {colors[color_idx]}, emotion: {emotions[emotion_idx]}")

    # Initial display
    field.set_shape(shapes[shape_idx])
    field.set_color(colors[color_idx])
    field.trigger_morph(2000)

    # Start VisPy event loop
    app.run()

if __name__ == '__main__':
    main()