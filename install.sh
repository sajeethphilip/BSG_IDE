#!/bin/bash
# install.sh - Simplified installation script for BSG-IDE

set -e

echo "=========================================="
echo "BSG-IDE - Beamer Slide Generator IDE"
echo "=========================================="
echo

# Check Python version
python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
required_version="3.7"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python $required_version or higher required (found $python_version)"
    exit 1
fi

echo "✓ Python $python_version found"

# Check if we're in a virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    echo "✓ Using virtual environment: $VIRTUAL_ENV"
else
    echo "ℹ Using system Python (no virtual environment)"
fi

# Install dependencies
echo
echo "Installing dependencies..."
pip3 install --user --upgrade pip
pip3 install --user -r requirements.txt

# Install BSG-IDE
echo
echo "Installing BSG-IDE..."
pip3 install --user .

# Add to PATH if needed
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo
    echo "Add ~/.local/bin to PATH:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo
fi

echo
echo "=========================================="
echo "✓ BSG-IDE installed successfully!"
echo
echo "Run: bsg-ide"
echo
echo "If you encounter missing dependencies, install them with:"
echo "  pip install --user <package-name>"
echo "=========================================="
