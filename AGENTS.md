# MD2Angebot — Agent Guidelines

## Overview
Python/PyQt6 desktop app that generates PDF quotations from Markdown. Features live preview, multiple profiles, LLM content generation, and Jinja2 templates.

## Structure
```
src/md2angebot/
├── core/          # Business logic (config, parser, renderer, pdf, llm)
├── ui/            # PyQt6 interface (main_window, editor, preview, header, config_dialog)
└── utils/         # Path helpers
templates/         # HTML/CSS templates (preset_1-5)
assets/            # Fonts, logos
examples/          # Sample files
```

## Commands
```bash
python3 main.py       # Run dev mode
python3 test_core.py  # Smoke test
./build_app.sh        # Build macOS .app
```

## Key Patterns
- **Config**: `config` singleton in `core/config.py` manages all state
- **Preview**: Debounced 800ms timer triggers `refresh_preview()`
- **LLM**: Streams via `LLMWorker` in background `QThread`
- **Templates**: `./templates/` takes priority in dev mode; changes apply on next refresh

## Config Location
`~/.config/md2angebot/` — config.yaml, templates/, logos/

## Coding Style
- Python 3, 4-space indent, type hints
- Core logic in `core/`, UI wiring in `ui/`
- Preserve template structure and comments

## Agent Rules
- Minimal, focused edits respecting existing patterns
- Don't modify build scripts or templates unless required
- Run `test_core.py` after core changes
