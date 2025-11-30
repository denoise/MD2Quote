"""
Modern, minimalistic styling for MD2Angebot.

Design System:
- Dark theme with warm undertones
- Accent: Soft coral/salmon
- Typography: Clean, readable
- Sharp corners, no border radius
- Tight spacing, compact UI
"""

# Color palette
COLORS = {
    # Background layers
    'bg_dark': '#1a1b1e',       # Deepest background
    'bg_base': '#25262b',       # Main background
    'bg_elevated': '#2c2e33',   # Cards, inputs
    'bg_hover': '#373a40',      # Hover states
    
    # Text
    'text_primary': '#e4e5e7',
    'text_secondary': '#909296',
    'text_muted': '#5c5f66',
    
    # Accent
    'accent': '#ff6b6b',
    'accent_hover': '#ff8787',
    'accent_muted': '#c92a2a',
    
    # Semantic
    'success': '#51cf66',
    'warning': '#fcc419',
    'error': '#ff6b6b',
    
    # Borders
    'border': '#373a40',
    'border_focus': '#ff6b6b',
    
    # Syntax highlighting
    'syntax_keyword': '#ff6b6b',
    'syntax_string': '#69db7c',
    'syntax_comment': '#5c5f66',
    'syntax_number': '#748ffc',
    'syntax_heading': '#ff6b6b',
    'syntax_bold': '#e4e5e7',
    'syntax_italic': '#c9cacc',
}

# Spacing (tight UI)
SPACING = {
    'xs': 2,
    'sm': 4,
    'md': 8,
    'lg': 12,
    'xl': 16,
}

# Border radius (none - sharp corners)
RADIUS = {
    'sm': 0,
    'md': 0,
    'lg': 0,
    'xl': 0,
}


def get_stylesheet():
    """Returns the complete application stylesheet."""
    return f"""
    /* ========================================
       GLOBAL STYLES
       ======================================== */
    
    QMainWindow {{
        background-color: {COLORS['bg_dark']};
    }}
    
    QWidget {{
        background-color: transparent;
        color: {COLORS['text_primary']};
        font-family: "Helvetica Neue", "Segoe UI", "Noto Sans", "Ubuntu", sans-serif;
        font-size: 13px;
    }}
    
    /* ========================================
       TOOLBAR
       ======================================== */
    
    QToolBar {{
        background-color: {COLORS['bg_base']};
        border: none;
        border-bottom: 1px solid {COLORS['border']};
        padding: {SPACING['sm']}px {SPACING['md']}px;
        spacing: {SPACING['sm']}px;
    }}
    
    QToolBar::separator {{
        background-color: {COLORS['border']};
        width: 1px;
        margin: 0 {SPACING['md']}px;
    }}
    
    QToolButton {{
        background-color: transparent;
        border: none;
        border-radius: 0;
        color: {COLORS['text_secondary']};
        font-size: 13px;
        font-weight: 500;
        padding: {SPACING['xs']}px {SPACING['sm']}px;
        min-height: 24px;
    }}
    
    QToolButton:hover {{
        background-color: {COLORS['bg_hover']};
        color: {COLORS['text_primary']};
    }}
    
    QToolButton:pressed {{
        background-color: {COLORS['bg_elevated']};
    }}
    
    /* ========================================
       COMBOBOX
       ======================================== */
    
    QComboBox {{
        background-color: {COLORS['bg_elevated']};
        border: 1px solid {COLORS['border']};
        border-radius: 0;
        color: {COLORS['text_primary']};
        padding: 4px 10px;
        padding-right: 30px;
        min-width: 140px;
        min-height: 26px;
        font-weight: 500;
        combobox-popup: 0;
    }}
    
    QComboBox:hover {{
        background-color: {COLORS['bg_hover']};
        border-color: {COLORS['text_muted']};
    }}
    
    QComboBox:focus {{
        border-color: {COLORS['accent']};
        background-color: {COLORS['bg_base']};
    }}
    
    QComboBox::drop-down {{
        border: none;
        width: 30px;
        background-color: transparent;
        subcontrol-origin: padding;
        subcontrol-position: center right;
    }}
    
    QComboBox::down-arrow {{
        image: none;
        width: 0;
        height: 0;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid {COLORS['text_muted']};
        margin-right: 8px;
    }}

    QComboBox::down-arrow:hover {{
        border-top-color: {COLORS['text_primary']};
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {COLORS['bg_elevated']};
        border: 1px solid {COLORS['border']};
        border-radius: 0;
        outline: none;
        selection-background-color: {COLORS['accent']};
        selection-color: {COLORS['bg_dark']};
        padding: 4px;
        margin-top: 30px;
    }}
    
    QComboBox QAbstractItemView::item {{
        padding: 8px 15px;
        min-height: 32px;
        border-radius: 0;
        color: {COLORS['text_primary']};
        margin: 0px;
    }}
    
    QComboBox QAbstractItemView::item:hover {{
        background-color: rgba(255, 107, 107, 0.1);
        color: {COLORS['text_primary']};
    }}
    
    QComboBox QAbstractItemView::item:selected {{
        background-color: {COLORS['accent']};
        color: {COLORS['bg_dark']};
    }}
    
    QComboBox QAbstractItemView::item:selected:hover {{
        background-color: {COLORS['accent']};
        color: {COLORS['bg_dark']};
    }}
    
    /* ========================================
       LINE EDIT & TEXT EDIT
       ======================================== */
    
    QLineEdit, QTextEdit, QPlainTextEdit {{
        background-color: {COLORS['bg_elevated']};
        border: 1px solid {COLORS['border']};
        border-radius: 0;
        color: {COLORS['text_primary']};
        padding: {SPACING['xs']}px {SPACING['sm']}px;
        selection-background-color: {COLORS['accent_muted']};
        selection-color: {COLORS['text_primary']};
    }}
    
    QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover {{
        border-color: {COLORS['text_muted']};
    }}
    
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
        border-color: {COLORS['accent']};
    }}
    
    QLineEdit::placeholder, QTextEdit::placeholder {{
        color: {COLORS['text_muted']};
    }}
    
    /* ========================================
       DATE EDIT
       ======================================== */
    
    QDateEdit {{
        background-color: {COLORS['bg_elevated']};
        border: 1px solid {COLORS['border']};
        border-radius: 0;
        color: {COLORS['text_primary']};
        padding: {SPACING['xs']}px {SPACING['sm']}px;
        min-height: 24px;
    }}
    
    QDateEdit:hover {{
        border-color: {COLORS['text_muted']};
    }}
    
    QDateEdit:focus {{
        border-color: {COLORS['accent']};
    }}
    
    QDateEdit::drop-down {{
        border: none;
        width: 24px;
        subcontrol-origin: padding;
        subcontrol-position: center right;
    }}
    
    QDateEdit::down-arrow {{
        image: none;
        width: 0;
        height: 0;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid {COLORS['text_secondary']};
        margin-right: 6px;
    }}
    
    QCalendarWidget {{
        background-color: {COLORS['bg_elevated']};
    }}
    
    QCalendarWidget QToolButton {{
        color: {COLORS['text_primary']};
        background-color: transparent;
        border-radius: 0;
        padding: 2px;
    }}
    
    QCalendarWidget QToolButton:hover {{
        background-color: {COLORS['bg_hover']};
    }}
    
    QCalendarWidget QWidget#qt_calendar_navigationbar {{
        background-color: {COLORS['bg_base']};
    }}
    
    /* ========================================
       LABELS
       ======================================== */
    
    QLabel {{
        color: {COLORS['text_secondary']};
        background-color: transparent;
    }}
    
    QLabel#section-title {{
        color: {COLORS['text_primary']};
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    /* ========================================
       SPLITTER
       ======================================== */
    
    QSplitter {{
        background-color: {COLORS['bg_dark']};
    }}
    
    QSplitter::handle {{
        background-color: {COLORS['border']};
        margin: 0;
    }}
    
    QSplitter::handle:horizontal {{
        width: 1px;
    }}
    
    QSplitter::handle:vertical {{
        height: 1px;
    }}
    
    /* ========================================
       STATUS BAR
       ======================================== */
    
    QStatusBar {{
        background-color: {COLORS['bg_base']};
        border-top: 1px solid {COLORS['border']};
        color: {COLORS['text_muted']};
        padding: {SPACING['xs']}px {SPACING['md']}px;
        font-size: 12px;
    }}
    
    /* ========================================
       SCROLLBARS
       ======================================== */
    
    QScrollBar:vertical {{
        background-color: transparent;
        width: 12px;
        margin: 0;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {COLORS['text_muted']};
        border-radius: 0;
        min-height: 40px;
        margin: 2px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {COLORS['text_secondary']};
    }}
    
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical,
    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {{
        height: 0;
        background: none;
    }}
    
    QScrollBar:horizontal {{
        background-color: transparent;
        height: 12px;
        margin: 0;
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {COLORS['text_muted']};
        border-radius: 0;
        min-width: 40px;
        margin: 2px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background-color: {COLORS['text_secondary']};
    }}
    
    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal,
    QScrollBar::add-page:horizontal,
    QScrollBar::sub-page:horizontal {{
        width: 0;
        background: none;
    }}
    
    /* ========================================
       FRAMES & SEPARATORS
       ======================================== */
    
    QFrame[frameShape="4"], /* HLine */
    QFrame[frameShape="5"]  /* VLine */ {{
        background-color: {COLORS['border']};
        border: none;
        max-height: 1px;
        max-width: 1px;
    }}
    
    /* ========================================
       MESSAGE BOX & DIALOGS
       ======================================== */
    
    QMessageBox {{
        background-color: {COLORS['bg_base']};
    }}
    
    QMessageBox QLabel {{
        color: {COLORS['text_primary']};
    }}

    /* ========================================
       MENUS
       ======================================== */

    QMenu {{
        background-color: {COLORS['bg_elevated']};
        border: 1px solid {COLORS['border']};
        color: {COLORS['text_primary']};
        padding: 4px;
    }}

    QMenu::item {{
        padding: 6px 20px 6px 10px;
        border-radius: 0;
        color: {COLORS['text_primary']};
        background-color: transparent;
    }}

    QMenu::item:hover {{
        background-color: rgba(255, 107, 107, 0.1);
        color: {COLORS['text_primary']};
    }}

    QMenu::item:selected {{
        background-color: {COLORS['accent']};
        color: {COLORS['bg_dark']};
    }}
    
    QMenu::item:selected:hover {{
        background-color: {COLORS['accent']};
        color: {COLORS['bg_dark']};
    }}

    QMenu::icon {{
        padding-left: 10px;
    }}
    
    QPushButton {{
        background-color: {COLORS['bg_elevated']};
        border: 1px solid {COLORS['border']};
        border-radius: 0;
        color: {COLORS['text_primary']};
        font-weight: 500;
        padding: {SPACING['xs']}px {SPACING['sm']}px;
        min-height: 24px;
        min-width: 60px;
    }}
    
    QPushButton:hover {{
        background-color: {COLORS['bg_hover']};
        border-color: {COLORS['text_muted']};
    }}
    
    QPushButton:pressed {{
        background-color: {COLORS['bg_base']};
    }}
    
    QPushButton:default {{
        background-color: {COLORS['accent']};
        border-color: {COLORS['accent']};
        color: white;
    }}
    
    QPushButton:default:hover {{
        background-color: {COLORS['accent_hover']};
        border-color: {COLORS['accent_hover']};
    }}
    
    QInputDialog {{
        background-color: {COLORS['bg_base']};
    }}
    
    QInputDialog QLabel {{
        color: {COLORS['text_primary']};
    }}
    
    QInputDialog QComboBox {{
        min-width: 200px;
    }}
    
    /* ========================================
       HEADER WIDGET
       ======================================== */
    
    #header-widget {{
        background-color: {COLORS['bg_base']};
        border-bottom: 1px solid {COLORS['border']};
    }}
    
    #header-section {{
        background-color: {COLORS['bg_elevated']};
        border-radius: 0;
        padding: {SPACING['sm']}px;
    }}
    
    #header-title {{
        color: {COLORS['accent']};
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: {SPACING['sm']}px;
    }}
    
    /* ========================================
       EDITOR WIDGET
       ======================================== */
    
    #editor-container {{
        background-color: {COLORS['bg_base']};
        border-right: 1px solid {COLORS['border']};
    }}
    
    #editor-label {{
        color: {COLORS['text_muted']};
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: {SPACING['sm']}px {SPACING['md']}px;
        background-color: {COLORS['bg_base']};
        border-bottom: 1px solid {COLORS['border']};
    }}
    
    #markdown-editor {{
        background-color: {COLORS['bg_dark']};
        border: none;
        border-radius: 0;
        padding: {SPACING['sm']}px;
        font-family: Menlo, Monaco, "Fira Code", "JetBrains Mono", monospace;
        font-size: 13px;
        line-height: 1.6;
    }}
    
    /* ========================================
       PREVIEW WIDGET
       ======================================== */
    
    #preview-container {{
        background-color: {COLORS['bg_base']};
    }}
    
    #preview-label {{
        color: {COLORS['text_muted']};
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: {SPACING['sm']}px {SPACING['md']}px;
        background-color: {COLORS['bg_base']};
        border-bottom: 1px solid {COLORS['border']};
    }}
    
    #pdf-view {{
        background-color: {COLORS['bg_dark']};
        border: none;
    }}
    """


# Syntax highlighting colors for editor
SYNTAX_COLORS = {
    'heading': COLORS['syntax_heading'],
    'bold': COLORS['syntax_bold'],
    'italic': COLORS['syntax_italic'],
    'list': COLORS['accent'],
    'code': COLORS['syntax_string'],
    'frontmatter': COLORS['text_muted'],
    'link': COLORS['syntax_number'],
}
