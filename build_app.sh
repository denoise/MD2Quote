#!/bin/bash
# Build script for MD2Quote macOS app

set -e

echo "🔨 Building MD2Quote.app..."
echo ""

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist || { echo "Cleanup failed, retrying in 1s..."; sleep 1; rm -rf build dist; }

# Check if we're in a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Warning: Not in a virtual environment. Consider using one."
    echo ""
fi

# Install dependencies if needed
echo "Installing dependencies..."
pip3 install -q pyinstaller

# Build the app
echo "Building app bundle with PyInstaller..."
pyinstaller --clean --noconfirm md2quote.spec

echo ""
echo "✅ Build complete!"
echo ""
echo "📦 Your app is located at: dist/MD2Quote.app"
echo ""
echo "To run it:"
echo "  open dist/MD2Quote.app"
echo ""
echo "To install it:"
echo "  cp -r dist/MD2Quote.app /Applications/"
