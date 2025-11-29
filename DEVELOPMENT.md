# MD2Angebot - Development Guide

## Running in Development Mode

To run the application in development mode:

```bash
cd /Users/eberendsen/Documents/DEV/md2angebot
python3 main.py
```

## Template Loading Behavior

The application has different template loading priorities depending on how it's run:

### Development Mode (Running from Source)

When running via `python3 main.py`, templates are loaded in this priority order:

1. **Source templates** (`/templates/` in project directory) - **HIGHEST PRIORITY**
2. User config templates (`~/.config/md2angebot/templates/`) - Fallback

This ensures that any edits you make to template files in your project directory are **immediately picked up** when the preview refreshes.

### Production Mode (Bundled .app)

When running the bundled application (`MD2Angebot.app`), templates are loaded in this order:

1. **User config templates** (`~/.config/md2angebot/templates/`) - User customizations
2. Bundled templates (frozen at build time) - Defaults

## Important Notes for Development

### Template Editing Workflow

**✅ Recommended for Development:**
1. Edit templates directly in the source directory: `/templates/*.html` and `/templates/*.css`
2. Save your changes
3. Restart the app OR wait for the preview to refresh (auto-reloads on changes)

**❌ Avoid During Development:**
- Using the in-app template editor (Settings → Edit HTML button)
- This saves templates to `~/.config/md2angebot/templates/`, which creates cached copies

### Clearing Cached Templates

If you've used the in-app template editor and now want to work with source templates:

```bash
# Remove cached templates from user config
rm -f ~/.config/md2angebot/templates/*.html
rm -f ~/.config/md2angebot/templates/*.css

# Or remove the entire templates directory
rm -rf ~/.config/md2angebot/templates/
```

After removing cached templates, restart the application.

## Template Auto-Reload

The application is configured to automatically reload templates when files change:

- **Jinja2 cache** is cleared before each render
- **File modification times** are checked automatically
- Changes take effect on the next preview refresh (typically < 1 second while typing)

## Building for Production

To build the macOS application bundle:

```bash
# Build the app
./build_app.sh

# Create DMG (optional)
./create_dmg.sh
```

After building, templates are bundled into the `.app` and frozen at that point. The bundled app will only see template changes if you:
1. Edit templates in the source directory
2. Rebuild the app

## Project Structure

```
md2angebot/
├── templates/          # Template files (HTML + CSS)
│   ├── modern-split.html
│   ├── modern-split.css
│   ├── elegant-centered.html
│   └── ...
├── src/
│   └── md2angebot/
│       ├── core/
│       │   ├── renderer.py    # Template rendering logic
│       │   └── config.py      # Configuration management
│       └── ui/
│           └── config_dialog.py  # Settings dialog with template editor
└── main.py            # Application entry point
```

## Testing Template Changes

1. Edit a template file (e.g., `templates/modern-split.css`)
2. Run the app: `python3 main.py`
3. Open or create a markdown document
4. The preview should show your changes immediately

If changes don't appear:
- Check which template file is being used (based on the selected preset)
- Verify there are no cached templates in `~/.config/md2angebot/templates/`
- Restart the application

## FAQ

**Q: I edited a template but don't see changes. Why?**

A: Check if you have cached templates in `~/.config/md2angebot/templates/`. Remove them to use source templates.

**Q: Should I use the in-app template editor during development?**

A: No, edit templates directly in the source directory using your preferred editor (VS Code, etc.).

**Q: Will my template changes be included in the bundled app?**

A: Yes, but you need to rebuild the app after making changes. Templates are frozen at build time.

**Q: How do I reset everything to defaults?**

A: Remove the entire config directory:
```bash
rm -rf ~/.config/md2angebot/
```

