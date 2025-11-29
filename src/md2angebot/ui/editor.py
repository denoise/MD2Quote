from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QVBoxLayout, QLabel, QFrame, QTextEdit
from PyQt6.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor, QFontDatabase, QPainter, QTextFormat, QTextCursor
from PyQt6.QtCore import Qt, QRegularExpression, QRect, QSize
from .styles import COLORS, SPACING, SYNTAX_COLORS


class LineNumberArea(QWidget):
    """Widget for displaying line numbers alongside the editor."""
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class ModernPlainTextEdit(QPlainTextEdit):
    """A styled plain text editor with line numbers."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)
        
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        
        self.update_line_number_area_width(0)
        self.highlight_current_line()

    def line_number_area_width(self):
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        space = SPACING['md'] + self.fontMetrics().horizontalAdvance('9') * digits + SPACING['sm']
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(COLORS['bg_base']))
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())
        
        current_block = self.textCursor().blockNumber()
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                if block_number == current_block:
                    painter.setPen(QColor(COLORS['text_primary']))
                else:
                    painter.setPen(QColor(COLORS['text_muted']))
                painter.drawText(
                    0, top, 
                    self.line_number_area.width() - SPACING['sm'], 
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight, 
                    number
                )
            
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1

    def highlight_current_line(self):
        extra_selections = []
        
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor(COLORS['bg_elevated'])
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        
        self.setExtraSelections(extra_selections)


class MarkdownHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for Markdown with modern color scheme."""
    def __init__(self, document):
        super().__init__(document)
        self.highlightingRules = []

        def add_rule(pattern, color_name, bold=False, italic=False):
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color_name))
            if bold:
                fmt.setFontWeight(QFont.Weight.Bold)
            if italic:
                fmt.setFontItalic(True)
            self.highlightingRules.append((QRegularExpression(pattern), fmt))

        # Headers (most prominent)
        add_rule(r"^#{1,6}\s+.*$", SYNTAX_COLORS['heading'], bold=True)
        
        # Frontmatter (YAML block)
        add_rule(r"^---[\s\S]*?---", SYNTAX_COLORS['frontmatter'])

        # Bold
        add_rule(r"\*\*[^*]+\*\*", SYNTAX_COLORS['bold'], bold=True)
        add_rule(r"__[^_]+__", SYNTAX_COLORS['bold'], bold=True)

        # Italic
        add_rule(r"(?<!\*)\*[^*]+\*(?!\*)", SYNTAX_COLORS['italic'], italic=True)
        add_rule(r"(?<!_)_[^_]+_(?!_)", SYNTAX_COLORS['italic'], italic=True)

        # Lists
        add_rule(r"^\s*[-*+]\s+", SYNTAX_COLORS['list'])
        add_rule(r"^\s*\d+\.\s+", SYNTAX_COLORS['list'])
        
        # Inline code
        add_rule(r"`[^`]+`", SYNTAX_COLORS['code'])
        
        # Links
        add_rule(r"\[([^\]]+)\]\([^\)]+\)", SYNTAX_COLORS['link'])
        
        # URLs
        add_rule(r"https?://[^\s]+", SYNTAX_COLORS['link'])

    def highlightBlock(self, text):
        for pattern, fmt in self.highlightingRules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)


class EditorWidget(QWidget):
    """Container widget for the Markdown editor."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("editor-container")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Section header
        header = QLabel("Markdown")
        header.setObjectName("editor-label")
        header.setStyleSheet(f"""
            color: {COLORS['text_muted']};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding: {SPACING['sm']}px {SPACING['md']}px;
            background-color: {COLORS['bg_base']};
            border-bottom: 1px solid {COLORS['border']};
        """)
        layout.addWidget(header)

        # Editor
        self.editor = ModernPlainTextEdit()
        self.editor.setObjectName("markdown-editor")
        self.highlighter = MarkdownHighlighter(self.editor.document())
        
        # Set monospace font - use system default first, then try alternatives
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        
        # Try to find a preferred font from available families
        available_families = QFontDatabase.families()
        preferred_fonts = ["Menlo", "Monaco", "Fira Code", "JetBrains Mono", "Consolas", "Source Code Pro"]
        
        for family in preferred_fonts:
            if family in available_families:
                font = QFont(family)
                break
        
        font.setPointSize(13)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.editor.setFont(font)
        
        # Configure editor appearance
        self.editor.setTabStopDistance(self.editor.fontMetrics().horizontalAdvance(' ') * 4)
        self.editor.setStyleSheet(f"""
            ModernPlainTextEdit {{
                background-color: {COLORS['bg_dark']};
                border: none;
                padding: {SPACING['sm']}px;
                selection-background-color: {COLORS['accent_muted']};
                selection-color: {COLORS['text_primary']};
            }}
        """)
        
        layout.addWidget(self.editor)

    def set_text(self, text):
        self.editor.setPlainText(text)

    def get_text(self):
        return self.editor.toPlainText()

    @property
    def textChanged(self):
        return self.editor.textChanged
