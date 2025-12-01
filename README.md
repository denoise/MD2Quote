# MD2Quote

A modern markdown-to-quotation generator with live PDF preview, AI-powered content generation, and professional templating.

![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-GUI-green.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)

## Features

### Core Functionality
- **Live PDF Preview** — See your quotation rendered in real-time as you type
- **Markdown Editor** — Syntax-highlighted editor with line numbers
- **Multi-Cursor Editing** — VS Code-style `⌘+D` to select and edit multiple occurrences
- **Page Breaks** — Use `+++` on its own line to insert page breaks

### Profile Management
- **5 Configurable Profiles** — Switch between different company identities instantly
- **Company Branding** — Custom logo, name, tagline with visibility controls
- **Contact Details** — Address, phone, email, website
- **Legal Information** — Tax ID, Chamber of Commerce number
- **Bank Details** — IBAN, BIC, bank name for payment info
- **Import/Export** — Share profiles as `.zip` archives

### Quotation Numbering
- **Custom Formats** — Use placeholders like `{YYYY}`, `{MM}`, `{NNN}`, `{PREFIX}`
- **Auto-Increment** — Counter resets yearly or monthly based on format
- **One-Click Generation** — Generate new numbers with a single click

### AI-Powered Content Generation
- **LLM Integration** — Connect to OpenRouter or OpenAI APIs
- **Multiple Models** — Claude Sonnet 4, GPT-4o, Gemini 2.0 Flash, Llama 3.3, and more
- **Streaming Responses** — See content generated in real-time
- **Context-Aware** — AI understands your current document for better suggestions
- **Custom System Prompts** — Tailor the AI behavior to your needs

### Templates & Styling
- **5 Built-in Templates** — Professional designs ready to use
- **Custom HTML/CSS** — Create your own templates with Jinja2
- **Typography Control** — Configure fonts for headings, body, and monospace text
- **Color Themes** — Customize primary, accent, background, and text colors
- **Page Margins** — Adjustable margins per profile

### VAT & Tax Support
- **German VAT** — Standard VAT calculation with configurable rates
- **Kleinunternehmer** — Small business exemption notice
- **No VAT** — Option to hide VAT entirely

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/md2quote.git
cd md2quote

# Install dependencies
pip install -r requirements.txt

# Run the application
python3 main.py
```

### Building for macOS

```bash
# Build the .app bundle
./build_app.sh

# Create a DMG (optional)
./create_dmg.sh
```

---

## Usage

### Creating a Quotation

1. **Select a Profile** — Choose from the toolbar dropdown
2. **Fill Client Details** — Enter name, email, and address in the header
3. **Write Content** — Use Markdown in the editor pane
4. **Preview** — See the PDF update live on the right
5. **Export** — Click "Export PDF" or press `⌘+E`

### Markdown Format

Quotations use standard Markdown with optional YAML frontmatter:

```markdown
---
client:
  name: "Acme Corp"
  address: "123 Main St, Berlin"
  email: "contact@acme.com"
quotation:
  number: "Q-2025-001"
  date: 2025-01-15
  valid_days: 30
---

# Project Proposal

## Scope of Work

Professional development services for your new platform.

## Line Items

| Description | Qty | Unit | Rate | Total |
|-------------|-----|------|------|-------|
| Planning & Architecture | 8 | hrs | €95 | €760 |
| Development | 24 | hrs | €95 | €2,280 |
| Testing & QA | 8 | hrs | €85 | €680 |

+++

## Terms & Conditions

Payment is due within 14 days of invoice date.
```

### Page Breaks

Insert `+++` on its own line to create a page break in the PDF output.

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `⌘+N` | New quotation |
| `⌘+O` | Open file |
| `⌘+S` | Save file |
| `⌘+E` | Export to PDF |
| `⌘+P` | Open Profiles |
| `⌘+,` | Open Settings |
| `⌘+D` | Select next occurrence (multi-cursor) |
| `⌘+B` | Bold text |
| `⌘+I` | Italic text |
| `⌘+K` | Insert link |
| `Alt+↑/↓` | Move line up/down |
| `Esc` | Clear multi-cursors |

---

## Configuration

### User Config Directory

All configuration is stored in `~/.config/md2quote/`:

```
~/.config/md2quote/
├── config.yaml      # Main configuration file
├── templates/       # Custom HTML/CSS templates
├── logos/           # Stored logo files
└── styles/          # Custom stylesheets
```

### Profile Configuration

Each profile supports these settings:

```yaml
preset_1:
  name: "My Company"
  
  company:
    name: "My Company Ltd"
    tagline: "Professional Services"
    logo: "logo.svg"
    logo_width: 40
    show_name: true
    show_tagline: true
    show_logo: true

  contact:
    street: "123 Business Ave"
    city: "Amsterdam"
    postal_code: "1012 AB"
    country: "Netherlands"
    phone: "+31 6 1234 5678"
    email: "hello@mycompany.com"
    website: "www.mycompany.com"

  legal:
    tax_id: "NL123456789B01"
    chamber_of_commerce: "12345678"

  bank:
    holder: "My Company Ltd"
    iban: "NL91 ABNA 0417 1643 00"
    bic: "ABNANL2A"
    bank_name: "ABN AMRO"

  defaults:
    currency: "EUR"
    vat_type: "german_vat"  # "german_vat", "kleinunternehmer", or "none"
    tax_rate: 19
    payment_days: 14
    language: "de"

  quotation_number:
    enabled: true
    format: "{PREFIX}-{YYYY}-{NNN}"
    counter: 0
```

### Quotation Number Placeholders

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{YYYY}` | Full year | 2025 |
| `{YY}` | Two-digit year | 25 |
| `{MM}` | Month (01-12) | 01 |
| `{DD}` | Day (01-31) | 15 |
| `{N}` | Counter (no padding) | 1 |
| `{NN}` | Counter (2 digits) | 01 |
| `{NNN}` | Counter (3 digits) | 001 |
| `{NNNN}` | Counter (4 digits) | 0001 |
| `{PREFIX}` | Company initials | ABC |

---

## LLM Configuration

Configure AI assistance in Settings (`⌘+,`):

### Supported Providers

- **OpenRouter** — Access multiple models through one API
- **OpenAI** — Direct OpenAI API access

### Available Models (via OpenRouter)

- Claude Sonnet 4 / 4.5
- Claude 3.5 Sonnet
- GPT-4o / GPT-4o Mini
- Gemini 2.0 Flash
- Llama 3.3 70B

### Using the LLM Assistant

1. Enter your API key in Settings
2. Type instructions in the "LLM Assistant" panel
3. Press `⌘+Enter` or click the send button
4. Watch the content stream into your editor

---

## Project Structure

```
md2quote/
├── main.py               # Application entry point
├── src/md2quote/
│   ├── core/
│   │   ├── config.py     # Configuration management
│   │   ├── parser.py     # Markdown/YAML parsing
│   │   ├── renderer.py   # Jinja2 template rendering
│   │   ├── pdf.py        # PDF generation (Qt WebEngine)
│   │   └── llm.py        # LLM API integration
│   ├── ui/
│   │   ├── main_window.py   # Main application window
│   │   ├── editor.py        # Markdown editor widget
│   │   ├── preview.py       # PDF preview widget
│   │   ├── header.py        # Header form widgets
│   │   ├── config_dialog.py # Settings/Profiles dialogs
│   │   ├── styles.py        # Theme and styling
│   │   └── icons.py         # Material icons
│   └── utils/
│       └── __init__.py   # Path utilities
├── templates/            # Built-in HTML/CSS templates
├── assets/
│   ├── fonts/            # Material icons font
│   └── images/           # Default logos
├── examples/             # Sample markdown files
├── build_app.sh          # macOS build script
└── create_dmg.sh         # DMG creation script
```

---

## Development

For detailed development instructions, see **[DEVELOPMENT.md](DEVELOPMENT.md)**.

### Running from Source

```bash
python3 main.py
```

Templates in `./templates/` are loaded directly — edit and refresh to see changes.

### Template Editing

- Templates use Jinja2 + HTML/CSS
- Each preset has its own template (`preset_1.html`, `preset_1.css`, etc.)
- User templates in `~/.config/md2quote/templates/` take priority in production

### Running Tests

```bash
python3 test_core.py
```

---

## Requirements

- Python 3.13+
- PyQt6 / PyQt6-WebEngine
- WeasyPrint
- Jinja2
- mistune
- PyYAML
- certifi

See `requirements.txt` for the complete list.

---

## License

MIT License — See [LICENSE](LICENSE) for details.
