# MD2Angebot - Development Guide

## Running in Development Mode

```bash
cd /Users/eberendsen/Documents/DEV/md2angebot
python3 main.py
```

## Template Loading

The application automatically detects whether it's running from source or as a bundled `.app`:

| Mode | Priority |
|------|----------|
| **Development** | Source templates (`./templates/`) → User config (`~/.config/md2angebot/templates/`) |
| **Production** | User config → Bundled templates |

In development mode, your source templates always take priority. Edit files in `./templates/` and changes are picked up immediately on preview refresh.

## Template Auto-Reload

- Jinja2 cache is cleared before each render
- File modification times are checked automatically
- Changes take effect on the next preview refresh (< 1 second while typing)

## Building for Production

```bash
# Build the app
./build_app.sh

# Create DMG (optional)
./create_dmg.sh
```

Templates are bundled into the `.app` and frozen at build time.

## Project Structure

```
md2angebot/
├── templates/          # Template files (HTML + CSS) - edit these during development
├── src/md2angebot/
│   ├── core/
│   │   ├── renderer.py    # Template rendering logic
│   │   └── config.py      # Configuration management
│   └── ui/
│       └── config_dialog.py  # Settings dialog with template editor
└── main.py            # Application entry point
```

## FAQ

**Q: Will my template changes be included in the bundled app?**

A: Yes, but you need to rebuild the app after making changes.

**Q: How do I reset everything to defaults?**

A: Remove the config directory:
```bash
rm -rf ~/.config/md2angebot/
```
