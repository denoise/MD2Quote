#!/bin/bash
# Create a DMG installer for MD2Angebot
# Run this after running build_app.sh

set -e

APP_NAME="MD2Angebot"
DMG_NAME="MD2Angebot-Installer"
APP_PATH="dist/${APP_NAME}.app"
DMG_PATH="dist/${DMG_NAME}.dmg"

if [ ! -d "$APP_PATH" ]; then
    echo "❌ Error: $APP_PATH not found. Run build_app.sh first."
    exit 1
fi

echo "📦 Creating DMG installer..."

# Remove old DMG if exists
rm -f "$DMG_PATH"

# Create a temporary directory for DMG contents
DMG_TEMP="dist/dmg_temp"
rm -rf "$DMG_TEMP"
mkdir -p "$DMG_TEMP"

# Copy app to temp directory
cp -R "$APP_PATH" "$DMG_TEMP/"

# Create a symlink to Applications folder
ln -s /Applications "$DMG_TEMP/Applications"

# Create DMG
hdiutil create -volname "$APP_NAME" -srcfolder "$DMG_TEMP" -ov -format UDZO "$DMG_PATH"

# Clean up
rm -rf "$DMG_TEMP"

echo ""
echo "✅ DMG created: $DMG_PATH"
echo ""
echo "Users can drag the app to Applications folder from this DMG."


