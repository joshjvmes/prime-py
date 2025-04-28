#!/usr/bin/env bash
# Vendor all Python dependencies locally for offline installation
set -euo pipefail
# Directory to store downloaded packages
DEPS_DIR="deps"
echo "Creating dependency directory: $DEPS_DIR"
mkdir -p "$DEPS_DIR"
echo "Downloading packages listed in requirements.txt..."
pip download --dest "$DEPS_DIR" -r requirements.txt
echo "All dependencies have been downloaded to '$DEPS_DIR'"
echo "To install offline, run: pip install --no-index --find-links $DEPS_DIR -r requirements.txt"