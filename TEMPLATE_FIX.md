# Template Loading Fix - Summary

## Problem

When running the application from source (`python3 main.py`), template edits made in VS Code weren't being picked up, even after restarting the application. Changes only appeared after opening the settings dialog and saving.

## Root Cause

The template renderer was prioritizing the **user config directory** (`~/.config/md2angebot/templates/`) over source templates. When using the in-app template editor, it would save templates to this directory, creating cached copies that override source templates.

## Solution

Modified `src/md2angebot/core/renderer.py` to detect if the app is running from source or bundled, and adjust template loading priority accordingly:

### Development Mode (Running from source)
```
Priority:
1. Source templates (templates/ directory) - HIGHEST PRIORITY
2. User config (~/.config/md2angebot/templates/) - Fallback
```

### Production Mode (Bundled .app)
```
Priority:
1. User config (~/.config/md2angebot/templates/) - User customizations
2. Bundled templates - Defaults
```

## Changes Made

### 1. Updated `renderer.py`

- Added detection for bundled vs source execution
- Reversed template directory priority for development mode
- Added cache clearing before each render to ensure file changes are detected
- Added comprehensive documentation in docstrings

### 2. Created `DEVELOPMENT.md`

Complete developer guide covering:
- Template loading behavior
- Development workflow
- Troubleshooting steps
- How to clear cached templates
- FAQ

### 3. Created `clear_template_cache.sh`

Utility script to quickly remove cached templates:
```bash
./clear_template_cache.sh
```

### 4. Created `README.md`

Main project README with links to development documentation.

## How It Works Now

### During Development

1. Edit templates in `templates/` directory using any editor
2. Save changes
3. Changes are immediately picked up on next preview refresh (< 1 second)
4. No need to restart the app or save settings

### Cache Clearing

The renderer now:
- Clears Jinja2's template cache before each render
- Checks file modification times automatically (`auto_reload=True`)
- Ensures template changes are always visible

## Testing

To verify the fix works:

1. Run `python3 main.py`
2. Edit a template file (e.g., `templates/modern-split.css`)
3. Switch to the app and wait for preview refresh
4. Changes should be visible immediately

If changes don't appear:
- Check for cached templates: `ls -la ~/.config/md2angebot/templates/`
- Clear cache: `./clear_template_cache.sh`
- Restart app

## Best Practices for Development

✅ **DO:**
- Edit templates directly in the source `templates/` directory
- Use your preferred code editor (VS Code, etc.)
- Save files and wait for auto-refresh

❌ **DON'T:**
- Use the in-app template editor during development (creates cached copies)
- Edit files inside the bundled .app (changes will be lost on rebuild)

## Future Considerations

Potential improvements:
- Add a "Development Mode" toggle in settings
- Show which template file is being used in the UI
- Add file watcher for instant reload without waiting for render
- Template versioning/backup system

