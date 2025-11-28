# MD2Angebot - Software Requirements Specification

## 1. Project Overview

**MD2Angebot** is a minimal desktop application for macOS that converts Markdown-formatted text into professionally styled PDF quotations. It is designed for power users, specifically advanced programmers and technical freelancers, who prefer manual configuration via text files over complex graphical user interfaces.

### Target User Profile
- **Role:** Advanced programmer / technical freelancer
- **Skills:** Comfortable editing YAML and Markdown files directly, understands file paths and config structures
- **Services:** Photography, 3D/CGI, Programming
- **OS:** macOS (primary target)
- **Primary Language:** German (defaults to "de")

---

## 2. Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Language** | Python 3.11+ | Robust ecosystem for text processing and file handling. |
| **GUI** | PyQt6 | Native macOS look and feel, high performance, minimal overhead. |
| **Markdown** | mistune | Fast, specification-compliant, and extensible Markdown parser. |
| **PDF Engine** | WeasyPrint | Allows for CSS-based styling of PDFs, ensuring high design quality. |
| **Templating** | Jinja2 | Industry-standard templating for separating logic from presentation. |
| **Packaging** | py2app | Creates standalone native macOS .app bundles. |

---

## 3. User Interface (Minimalist)

The application features a simple, two-pane window designed for efficiency.

### 3.1 Layout
```
┌─────────────────────────────────────────────────────────┐
│ MD2Angebot                                    [—][□][×] │
├───────────────────────────┬─────────────────────────────┤
│                           │                             │
│   Markdown Editor         │   Live PDF Preview          │
│   (Left Pane)             │   (Right Pane)              │
│   - Syntax highlighting   │   - Rendered PDF view       │
│   - Line numbers          │   - Auto-refreshes          │
│                           │                             │
├───────────────────────────┴─────────────────────────────┤
│ [Open] [Save] [Export PDF]              Q-2025-042.md   │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Key Features
- **Split-pane View:** Simultaneous editing and previewing.
- **Live Preview:** The PDF preview updates automatically when the Markdown file is saved (or after a debounce period).
- **Drag-and-Drop:** Support for dragging `.md` files directly into the window to open them.
- **Keyboard Shortcuts:**
  - `⌘ + O`: Open File
  - `⌘ + S`: Save File
  - `⌘ + E`: Export to PDF
- **Minimalist Interaction:** No setup wizards or complex settings dialogs. Configuration is handled entirely through files.

---

## 4. Configuration

Configuration is file-based, stored in the user's standard config directory.

### 4.1 User Config File
**Path:** `~/.config/md2angebot/config.yaml`

This YAML file contains all user-specific data. The application reads this on startup.

#### Structure
- **company:** Name, tagline, and logo path.
- **contact:** Address, phone, email, website.
- **legal:** Tax ID, Chamber of Commerce number.
- **bank:** Banking details (IBAN, BIC, Bank Name).
- **defaults:** Default currency, tax rate, payment terms, language (defaults to "de").
- **typography:** Font families and sizes.
- **colors:** Hex codes for the document theme.

### 4.2 Templates & Styles
- **Templates:** Custom Jinja2 templates can be placed in `~/.config/md2angebot/templates/`.
- **Styles:** Custom CSS files can be placed in `~/.config/md2angebot/styles/`.

---

## 5. Quotation Markdown Format

The input files are standard Markdown with a YAML frontmatter block defining the specific details of the quotation.

### 5.1 Frontmatter (YAML)
Must be at the top of the `.md` file, between `---` delimiters.

```yaml
---
client:
  name: "Client Name"
  address: "Client Address"
  email: "client@email.com"
quotation:
  number: "Q-YYYY-NUM"
  date: YYYY-MM-DD
  valid_days: 30
template: programming  # Optional: specific template to use
---
```

### 5.2 Body Content
- **Project Title:** Level 1 Header (`# Title`)
- **Description:** Standard Markdown text.
- **Line Items:** A Markdown table defining the services.
  - Columns: Description, Qty, Unit, Rate, Total.
  - *Note:* The application can calculate the Total column and Subtotals if the table follows a strict structure, or the user can fill them manually.
- **Notes/Terms:** Standard Markdown lists or text at the bottom.

---

## 6. Design Specifications

### 6.1 Visual Style
- **Clean & Professional:** Ample whitespace, clear hierarchy.
- **Typography:** 
  - Headings: **Montserrat** (SemiBold)
  - Body: **Source Sans Pro** (Regular)
  - Data/Numbers: **JetBrains Mono** (Monospace for alignment)
- **Color Palette:**
  - Primary: `#1a1a2e` (Deep Navy)
  - Accent: `#e94560` (Coral Red)
  - Background: `#ffffff` (White)
  - Text: `#2d2d2d` (Dark Grey)
  - Muted: `#6c757d` (Grey)
  - Borders: `#dee2e6` (Light Grey)

### 6.2 PDF Layout
- **Format:** A4
- **Margins:** 20mm (all sides)
- **Header:** Logo (left) and Company Info (right).
- **Footer:** Bank details and page numbers (e.g., "Page 1 of 1").
- **Tables:** 
  - Full width.
  - Alternating row background colors (`#f8f9fa` for alt rows).
  - Right-aligned numerical columns.

---

## 7. File Structure

Proposed source code structure for the project:

```
md2angebot/
├── src/
│   ├── main.py           # Application entry point
│   ├── app.py            # PyQt6 application logic
│   ├── ui/
│   │   ├── main_window.py # Main UI layout
│   │   ├── editor.py     # Editor widget
│   │   └── preview.py    # Preview widget
│   ├── core/
│   │   ├── parser.py     # Markdown & YAML parsing logic
│   │   ├── renderer.py   # Jinja2 rendering logic
│   │   ├── pdf.py        # WeasyPrint PDF generation
│   │   └── config.py     # Configuration loader
│   └── utils/
│       └── helpers.py    # Utility functions
├── templates/
│   ├── base.html         # Base HTML template
│   ├── photography.html  # Service-specific template
│   ├── 3d_artist.html    # Service-specific template
│   ├── programming.html  # Service-specific template
│   └── quotation.css     # CSS for PDF styling
├── assets/
│   ├── fonts/            # Bundled font files
│   └── icons/            # App icons
├── examples/
│   ├── config.yaml       # Sample configuration
│   ├── photography.md    # Sample quotation
│   ├── 3d_artist.md      # Sample quotation
│   └── programming.md    # Sample quotation
├── requirements.txt      # Python dependencies
├── setup.py              # Installation script
└── README.md             # Project documentation
```

---

## 8. Implementation Plan

1.  **Core Logic:** Implement configuration loading, Markdown parsing, and PDF generation.
2.  **UI Development:** Build the split-pane PyQt6 interface.
3.  **Integration:** Connect the editor and preview panes with the core logic.
4.  **Styling:** Refine HTML templates and CSS to match design specs.
5.  **Packaging:** Configure `py2app` for macOS distribution.

