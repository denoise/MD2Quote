from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QVBoxLayout
from PyQt6.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor, QFontDatabase
from PyQt6.QtCore import Qt, QRegularExpression

class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlightingRules = []

        # Helper to create rules
        def add_rule(pattern, color_name, bold=False, italic=False):
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color_name))
            if bold: fmt.setFontWeight(QFont.Weight.Bold)
            if italic: fmt.setFontItalic(True)
            self.highlightingRules.append((QRegularExpression(pattern), fmt))

        # Headers
        add_rule(r"^#+[^\n]*", "#e94560", bold=True)  # Accent color
        
        # Frontmatter (YAML)
        add_rule(r"^---[\s\S]*?---", "#6c757d") # Muted

        # Bold
        add_rule(r"\*\*.*?\*\*", "#1a1a2e", bold=True)
        add_rule(r"__.*?__", "#1a1a2e", bold=True)

        # Italic
        add_rule(r"\*.*?\*", "#1a1a2e", italic=True)
        add_rule(r"_.*?_", "#1a1a2e", italic=True)

        # Lists
        add_rule(r"^\s*[\-\*]\s+", "#e94560")
        
        # Code
        add_rule(r"`.*?`", "#d63384")

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

class EditorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.editor = QPlainTextEdit()
        self.highlighter = MarkdownHighlighter(self.editor.document())
        
        # Set monospace font
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(12)
        self.editor.setFont(font)
        
        # Line height / Tab width
        self.editor.setTabStopDistance(40) # approx 4 spaces
        
        self.layout.addWidget(self.editor)

    def set_text(self, text):
        self.editor.setPlainText(text)

    def get_text(self):
        return self.editor.toPlainText()

    @property
    def textChanged(self):
        return self.editor.textChanged

