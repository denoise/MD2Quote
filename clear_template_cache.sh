#!/bin/bash
# Clear cached templates from user config directory
# Run this if you've used the in-app template editor and want to revert to source templates

CONFIG_DIR="$HOME/.config/md2angebot/templates"

if [ -d "$CONFIG_DIR" ]; then
    echo "Clearing cached templates from: $CONFIG_DIR"
    rm -f "$CONFIG_DIR"/*.html
    rm -f "$CONFIG_DIR"/*.css
    echo "✓ Template cache cleared!"
    echo ""
    echo "Source templates will now be used when running: python3 main.py"
else
    echo "No cached templates directory found at: $CONFIG_DIR"
    echo "Nothing to clear."
fi

