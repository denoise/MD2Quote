# MD2Angebot

A modern markdown-to-quotation generator with live PDF preview.

## Quick Start

### Development Mode

```bash
python3 main.py
```

### Building

```bash
./build_app.sh
```

## Documentation

- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Developer guide with template editing workflow and troubleshooting
- **[SPEC.md](SPEC.md)** - Application specification

## Features

- Live markdown editor with PDF preview
- Multiple preset templates (Modern Split, Elegant Centered, etc.)
- Configurable company profiles
- Automatic quotation numbering
- VAT/Tax calculation support
- Template customization (HTML/CSS)

## Development

For detailed development instructions, including how to edit templates and avoid caching issues, see **[DEVELOPMENT.md](DEVELOPMENT.md)**.

### Key Points

- **Running from source**: Templates are loaded from `templates/` directory (live editing)
- **Template changes**: Automatically picked up on next preview refresh
- **Cached templates**: If you've used the in-app editor, run `./clear_template_cache.sh`

## Project Structure

```
md2angebot/
├── templates/          # HTML/CSS templates
├── src/md2angebot/     # Application source
│   ├── core/          # Business logic
│   └── ui/            # User interface
├── examples/          # Example markdown files
├── main.py           # Entry point
└── build_app.sh      # Build script
```

## Requirements

- Python 3.13+
- PyQt6
- WeasyPrint
- Jinja2
- See `requirements.txt` for full list

## License

[Your License Here]

