#!/bin/bash
# Fixed build script for Render deployment

set -e

echo "🚀 Building Mitten Backend for Render (Fixed)"
echo "============================================="

# Install uv if not present
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Add uv to PATH
    export PATH="$HOME/.local/bin:$PATH"
fi

# Verify uv is available
echo "🔍 Verifying uv installation..."
uv --version

# Install dependencies
echo "📦 Installing dependencies..."
uv sync --frozen

# Create static directory
echo "📁 Creating static directories..."
mkdir -p static/images

# Set permissions
echo "🔧 Setting permissions..."
chmod +x main.py

echo "✅ Build completed successfully!"
echo ""
echo "📊 Summary:"
echo "- Dependencies installed with uv"
echo "- Static directories created"
echo "- Permissions set"
echo ""
echo "🚀 Ready for deployment!"
