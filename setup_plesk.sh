#!/bin/bash
# Run this once via Plesk Terminal or SSH after uploading files
# This sets up the Python virtual environment and installs dependencies

set -e

echo "=== AI Reception API - Plesk Setup ==="

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created."
fi

# Activate and install packages
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "=== Setup complete ==="
echo "Make sure your .env file has correct values before restarting the app."
