#!/bin/bash
# Build script for MD2Angebot macOS app

set -e

echo "🔨 Building MD2Angebot.app..."
echo ""

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist

# Check if we're in a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Warning: Not in a virtual environment. Consider using one."
    echo ""
fi

# Install dependencies if needed
echo "Installing dependencies..."
pip3 install -q py2app

# Build the app
echo "Building app bundle..."
python3 setup.py py2app

echo ""
echo "✅ Build complete!"
echo ""
echo "📦 Your app is located at: dist/MD2Angebot.app"
echo ""
echo "To run it:"
echo "  open dist/MD2Angebot.app"
echo ""
echo "To install it:"
echo "  cp -r dist/MD2Angebot.app /Applications/"
echo ""
echo "⚠️  Note: Users still need to install system dependencies once:"
echo "  brew install pango glib gobject-introspection"

