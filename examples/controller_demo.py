#!/usr/bin/env python3
"""
Demo of ParticleField with remote JSON TCP controller.
Run this, then in another shell:
  nc localhost 8765
  {"command":"set_shape","args":["cube"]}
  {"command":"trigger_morph","args":[1500]}
  {"command":"express","args":["joy", 1.0, 2000]}
"""
from vispy import app
from particle_field import ParticleField
from particle_field.controller import FieldController

def main():
    # Create the particle field
    field = ParticleField(count=8000, size=12.0)
    # Start the remote controller
    controller = FieldController(field)
    # Run the VisPy loop
    app.run()

if __name__ == '__main__':
    main()