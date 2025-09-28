#!/bin/bash
# Build script for Render deployment

set -e

echo "🚀 Building Mitten Backend for Render"
echo "====================================="

# Install uv if not present
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

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
