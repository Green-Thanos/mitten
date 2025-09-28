#!/bin/bash
# Simple build script for Render deployment

set -e

echo "🚀 Simple Build for Render"
echo "========================="

# Install uv
echo "📦 Installing uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Verify installation
echo "🔍 Verifying uv..."
$HOME/.local/bin/uv --version

# Install dependencies
echo "📦 Installing dependencies..."
$HOME/.local/bin/uv sync --frozen

# Create static directory
echo "📁 Creating static directories..."
mkdir -p static/images

echo "✅ Build completed!"
