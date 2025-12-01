# MD2Angebot — Project Context

## What It Does
Converts Markdown → professional PDF quotations with live preview, multiple company profiles, LLM-powered content, and customizable templates.

## Tech Stack
- **GUI**: PyQt6 + PyQt6-WebEngine (preview)
- **PDF**: WeasyPrint (export)
- **Templates**: Jinja2 HTML/CSS
- **Markdown**: Mistune
- **LLM**: OpenRouter / OpenAI APIs

## Structure
```
src/md2angebot/
├── core/
│   ├── config.py     # Profiles, quotation numbering, import/export
│   ├── parser.py     # Markdown + YAML frontmatter
│   ├── renderer.py   # Jinja2 rendering
│   ├── pdf.py        # Qt WebEngine PDF generation
│   └── llm.py        # OpenRouter/OpenAI streaming
├── ui/
│   ├── main_window.py   # Main app, toolbar, file ops
│   ├── editor.py        # Multi-cursor markdown editor
│   ├── preview.py       # PDF preview pane
│   ├── header.py        # Forms + LLM panel
│   └── config_dialog.py # Settings/Profiles dialogs
templates/               # preset_1-5.html/.css
```

## Key Features
- Live PDF preview (800ms debounce)
- 5 profiles with company/contact/bank info
- Quotation numbering: `{YYYY}-{NNN}`, auto-reset
- LLM: Claude, GPT-4o, Gemini, Llama (streaming)
- Multi-cursor editing (⌘+D)
- Page breaks: `+++`
- VAT: German, Kleinunternehmer, None

## Dev Commands
```bash
python3 main.py       # Dev mode (templates hot-reload)
python3 test_core.py  # Smoke test
./build_app.sh        # Build .app
```

## Config
Stored in `~/.config/md2angebot/`:
- `config.yaml` — All profiles and LLM settings
- `templates/` — User template overrides
- `logos/` — Stored logo files

## Architecture Notes
- `config` singleton manages state + persistence
- `LLMWorker` runs in `QThread`, emits `chunk_received` signal
- Templates: dev mode loads `./templates/` first
- Preview timer restarts on each keystroke
