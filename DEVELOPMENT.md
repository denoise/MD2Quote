# MD2Quote - Development Guide

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run in development mode
python3 main.py
```

---

## Layout System

### Layout Loading Priority

The application detects whether it's running from source or as a bundled `.app`:

| Mode | Priority Order |
|------|----------------|
| **Development** | Source layouts (`./templates/`) → User config (`~/.config/md2quote/templates/`) |
| **Production** | User config → Bundled layouts |

In development mode, source layouts always take priority for fast iteration.

### Layout Structure

Each template requires two layout files:
- `preset_N.html` — Jinja2 HTML template
- `preset_N.css` — Stylesheet

### Available Layout Variables

Layouts receive these context variables:

```jinja2
{# Company info #}
{{ company.name }}
{{ company.tagline }}
{{ company.logo }}  {# file:// URL #}
{{ company.show_name }}
{{ company.show_tagline }}
{{ company.show_logo }}

{# Contact #}
{{ contact.street }}
{{ contact.city }}
{{ contact.postal_code }}
{{ contact.country }}
{{ contact.phone }}
{{ contact.email }}
{{ contact.website }}

{# Legal #}
{{ legal.tax_id }}
{{ legal.chamber_of_commerce }}

{# Bank #}
{{ bank.holder }}
{{ bank.iban }}
{{ bank.bic }}
{{ bank.bank_name }}

{# Quotation #}
{{ quotation.number }}
{{ quotation.date }}
{{ quotation.valid_days }}

{# Client #}
{{ client.name }}
{{ client.email }}
{{ client.address }}

{# Content (rendered HTML from Markdown) #}
{{ content }}

{# Snippets #}
{{ snippets.intro_text }}
{{ snippets.terms }}
{{ snippets.signature_block }}
{{ snippets.custom_footer }}

{# Defaults #}
{{ defaults.currency }}
{{ defaults.vat_type }}  {# "german_vat", "kleinunternehmer", "none" #}
{{ defaults.tax_rate }}
{{ defaults.payment_days }}
{{ defaults.language }}

{# Typography #}
{{ typography.heading }}
{{ typography.body }}
{{ typography.mono }}
{{ typography.sizes.company_name }}
{{ typography.sizes.heading1 }}
{{ typography.sizes.heading2 }}
{{ typography.sizes.body }}
{{ typography.sizes.small }}

{# Colors #}
{{ colors.primary }}
{{ colors.accent }}
{{ colors.background }}
{{ colors.text }}
{{ colors.muted }}
{{ colors.border }}
{{ colors.table_alt }}

{# Layout #}
{{ layout.page_margins }}  {# [top, right, bottom, left] #}
```

### Layout Auto-Reload

- Jinja2 cache is cleared before each render
- Changes take effect on the next preview refresh
- No restart required during development

### Creating Custom Layouts

1. Create `your_layout.html` and `your_layout.css` in `./templates/`
2. Use the variables above in your Jinja2 template
3. The layout will be available immediately

---

## Project Architecture

### Core Modules (`src/md2quote/core/`)

| Module | Responsibility |
|--------|----------------|
| `config.py` | Configuration loading, template management, template import/export |
| `parser.py` | Markdown parsing with YAML frontmatter extraction |
| `renderer.py` | Jinja2 template rendering |
| `pdf.py` | PDF generation using Qt WebEngine |
| `llm.py` | OpenRouter/OpenAI API integration |

### UI Modules (`src/md2quote/ui/`)

| Module | Responsibility |
|--------|----------------|
| `main_window.py` | Application window, toolbar, file operations |
| `editor.py` | Markdown editor with syntax highlighting, multi-cursor |
| `preview.py` | PDF preview panel |
| `header.py` | Quotation/client input forms, LLM panel |
| `config_dialog.py` | Settings and Templates dialogs |
| `styles.py` | Theme colors, spacing, global stylesheet |
| `icons.py` | Material icons via TTF font |

---

## Key Patterns

### Preview Refresh

The preview updates on a debounced timer (800ms after last keystroke):

```python
self.preview_timer = QTimer()
self.preview_timer.setSingleShot(True)
self.preview_timer.setInterval(800)
self.preview_timer.timeout.connect(self.refresh_preview)

self.editor.textChanged.connect(self.on_text_changed)

def on_text_changed(self):
    self.preview_timer.start()  # Restarts the timer
```

### LLM Streaming

LLM responses stream into the editor in real-time:

```python
class LLMWorker(QObject):
    chunk_received = pyqtSignal(str)
    
    def run(self):
        for chunk in self.llm_service.generate_stream(instruction, context):
            self.chunk_received.emit(chunk)
```

### Configuration Persistence

The `ConfigLoader` singleton manages all settings:

```python
from ..core.config import config

# Get active template
preset = config.get_active_preset()

# Generate quotation number
number = config.generate_quotation_number(preset_key)

# Save changes
config._save_config()
```

---

## Building

### Development Build

```bash
./build_app.sh
```

This creates `dist/MD2Quote.app` using PyInstaller.

### Distribution Build

```bash
./create_dmg.sh
```

Creates a DMG installer for distribution.

### What Gets Bundled

- Python interpreter and dependencies
- All source code
- Layouts from `./templates/`
- Assets from `./assets/`
- Fonts from `./assets/fonts/`

---

## Testing

### Smoke Test

```bash
python3 test_core.py
```

Tests the core parsing and rendering pipeline.

### Manual Testing Checklist

- [ ] Create new quotation
- [ ] Open existing `.md` file
- [ ] Save file
- [ ] Export PDF
- [ ] Switch templates
- [ ] Generate quotation number
- [ ] Edit layout and verify preview updates
- [ ] Test LLM generation (if API key configured)
- [ ] Import/Export template

---

## Troubleshooting

### Layout Changes Not Appearing

In development, layouts load from `./templates/`. If changes aren't appearing:

1. Check you're editing files in the source `./templates/` directory
2. Force a preview refresh with `⌘+R`
3. Verify the template is using the expected layout

### LLM Not Working

1. Check API key is set in Settings → LLM
2. Verify network connectivity
3. Check console for error messages
4. Try a different model

### PDF Export Issues

1. Ensure WeasyPrint is installed correctly
2. Check for font loading errors in console
3. Verify HTML/CSS syntax in layouts

### Reset to Defaults

Remove the config directory to start fresh:

```bash
rm -rf ~/.config/md2quote/
```

---

## Common Tasks

### Adding a New Template

1. Create `preset_N.html` and `preset_N.css` in `./templates/`
2. Add the template configuration to `examples/config.yaml`
3. Update `DEFAULT_PRESET_KEYS` in `config.py` if it should be a default

### Adding a New LLM Model

Edit `src/md2quote/core/llm.py`:

```python
OPENROUTER_MODELS = {
    'new-provider/new-model': 'Display Name',
    # ...existing models
}
```

### Changing the Default Theme

Edit `src/md2quote/ui/styles.py`:

```python
COLORS = {
    'bg_dark': '#0d1117',
    'accent': '#58a6ff',
    # ...
}
```

---

## Dependencies

Core dependencies and their purposes:

| Package | Purpose |
|---------|---------|
| PyQt6 | GUI framework |
| PyQt6-WebEngine | PDF preview rendering |
| WeasyPrint | HTML to PDF conversion |
| Jinja2 | Template rendering |
| mistune | Markdown parsing |
| PyYAML | Configuration files |
| certifi | SSL certificates for API calls |

---

## Contributing

1. Follow existing code style (4-space indentation, type hints)
2. Keep core logic in `core/`, UI in `ui/`
3. Test changes with `python3 test_core.py`
4. Update documentation if adding features
