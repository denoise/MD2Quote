# MD2Angebot Project Context

## Project Overview
**MD2Angebot** is a Python-based desktop application that generates professional PDF quotations and proposals from Markdown text. It features a live preview, multiple styling templates, and tax calculation logic.

## Technical Stack
- **Language:** Python 3.13+
- **GUI Framework:** PyQt6
- **PDF Engine:** WeasyPrint (HTML/CSS to PDF)
- **Templating:** Jinja2
- **Markdown Parser:** Mistune
- **Configuration:** PyYAML

## Project Structure
```
md2angebot/
├── templates/          # HTML/CSS source templates for PDF generation
├── src/md2angebot/     # Main application source code
│   ├── core/           # Business logic (Renderer, Parser, Config)
│   └── ui/             # PyQt6 User Interface components
├── examples/           # Example markdown files for testing
├── main.py             # Development entry point
├── build_app.sh        # Script to build the standalone macOS .app
├── requirements.txt    # Python dependencies
└── DEVELOPMENT.md      # Detailed developer guide
```

## Development Workflow

### 1. Setup
Ensure Python 3.13+ is installed.
```bash
pip install -r requirements.txt
```

### 2. Running (Dev Mode)
Start the application directly from the source to enable hot-reloading of templates.
```bash
python3 main.py
```

### 3. Building (Production)
Create a standalone macOS application bundle.
```bash
./build_app.sh
```

## Key Development Notes

### Template System
*   **Location:** Source templates are in `templates/`.
*   **Priority:** When running from source (`main.py`), files in `templates/` take precedence over user configs.
*   **Caching Warning:** Avoid using the in-app "Edit HTML" feature during development, as it saves copies to `~/.config/md2angebot/templates/` which override source files.
*   **Clearing Cache:** If template changes aren't showing, run `./clear_template_cache.sh` to remove user overrides.

### Architecture Highlights
*   **`core/renderer.py`**: Handles the conversion of Markdown + Data -> HTML -> PDF.
*   **`ui/main_window.py`**: The primary GUI container.
*   **`ui/preview.py`**: Handles the live PDF preview pane.

## Common Commands
*   **Run App:** `python3 main.py`
*   **Clean Cache:** `./clear_template_cache.sh`
*   **Build App:** `./build_app.sh`
