from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QVBoxLayout, QLabel, QFrame, QTextEdit
from PyQt6.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor, QFontDatabase, QPainter, QTextFormat, QTextCursor, QKeySequence
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
    """A styled plain text editor with line numbers and multi-cursor support."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)
        
        # Multi-cursor state for Cmd+D functionality
        self.extra_cursors: list[QTextCursor] = []
        self.multi_select_search_text: str = ""
        
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
            # Highlight current line
            selection = QTextEdit.ExtraSelection()
            line_color = QColor(COLORS['bg_elevated'])
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
            
            # Highlight extra cursor selections (multi-cursor)
            for cursor in self.extra_cursors:
                if cursor.hasSelection():
                    sel = QTextEdit.ExtraSelection()
                    sel.format.setBackground(QColor(COLORS['accent_muted']))
                    sel.format.setForeground(QColor(COLORS['text_primary']))
                    sel.cursor = cursor
                    extra_selections.append(sel)
        
        self.setExtraSelections(extra_selections)

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts for formatting and multi-cursor."""
        modifiers = event.modifiers()
        key = event.key()
        
        # Escape clears extra cursors
        if key == Qt.Key.Key_Escape:
            if self.extra_cursors:
                self.clear_extra_cursors()
                return
        
        # Cmd+D / Ctrl+D - Add selection to next find match
        if (key == Qt.Key.Key_D and 
            (modifiers & Qt.KeyboardModifier.ControlModifier or modifiers & Qt.KeyboardModifier.MetaModifier)):
            self.handle_cmd_d()
            return
        
        # Bold (Cmd+B / Ctrl+B)
        if event.matches(QKeySequence.StandardKey.Bold):
            self.toggle_formatting('**')
            return

        # Italic (Cmd+I / Ctrl+I)
        if event.matches(QKeySequence.StandardKey.Italic):
            self.toggle_formatting('*')
            return

        # Link (Cmd+K / Ctrl+K) - No StandardKey for Link, check manual
        # Check if K is pressed with either Control or Meta (Command) modifier
        if (key == Qt.Key.Key_K and 
            (modifiers & Qt.KeyboardModifier.ControlModifier or modifiers & Qt.KeyboardModifier.MetaModifier)):
            self.insert_link()
            return
        
        # Handle multi-cursor typing
        if self.extra_cursors:
            if key == Qt.Key.Key_Backspace:
                self.handle_multi_cursor_backspace()
                return
            elif key == Qt.Key.Key_Delete:
                self.handle_multi_cursor_delete()
                return
            elif event.text() and event.text().isprintable():
                self.handle_multi_cursor_insert(event.text())
                return
            elif key in (Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down,
                         Qt.Key.Key_Home, Qt.Key.Key_End):
                # Clear extra cursors on navigation
                self.clear_extra_cursors()

        super().keyPressEvent(event)

    def toggle_formatting(self, symbol):
        """Wraps selected text in symbol, or inserts symbol if empty."""
        cursor = self.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            # Check if already wrapped (naive check)
            if text.startswith(symbol) and text.endswith(symbol) and len(text) >= 2 * len(symbol):
                # Unwrap
                new_text = text[len(symbol):-len(symbol)]
            else:
                # Wrap
                new_text = f"{symbol}{text}{symbol}"
            
            cursor.beginEditBlock()
            cursor.insertText(new_text)
            cursor.endEditBlock()
        else:
            # Insert empty wrapper and move cursor inside
            cursor.beginEditBlock()
            cursor.insertText(f"{symbol}{symbol}")
            cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.MoveAnchor, len(symbol))
            cursor.endEditBlock()
            self.setTextCursor(cursor)

    def insert_link(self):
        """Inserts Markdown link syntax."""
        cursor = self.textCursor()
        cursor.beginEditBlock()
        if cursor.hasSelection():
            text = cursor.selectedText()
            cursor.insertText(f"[{text}](url)")
            # Optional: Select 'url' to let user type immediately? 
            # Keeping it simple for now.
        else:
            cursor.insertText("[text](url)")
            # Select 'text'
            cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.MoveAnchor, 6) # '](url)' is 6 chars
            cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor, 4) # 'text' is 4 chars
            self.setTextCursor(cursor)
        cursor.endEditBlock()

    def handle_cmd_d(self):
        """Handle Cmd+D: select word or add next occurrence."""
        cursor = self.textCursor()
        
        # If no selection and no extra cursors, select word at cursor
        if not cursor.hasSelection() and not self.extra_cursors:
            self.select_word_at_cursor()
            return
        
        # Get the search text from current selection
        if cursor.hasSelection():
            self.multi_select_search_text = cursor.selectedText()
        
        if not self.multi_select_search_text:
            return
        
        # Find next occurrence after the last cursor
        last_cursor = self.extra_cursors[-1] if self.extra_cursors else cursor
        next_cursor = self.find_next_occurrence(last_cursor)
        
        if next_cursor:
            # Check if we've wrapped around to an existing selection
            new_start = next_cursor.selectionStart()
            existing_positions = [cursor.selectionStart()]
            existing_positions.extend(c.selectionStart() for c in self.extra_cursors)
            
            if new_start not in existing_positions:
                self.extra_cursors.append(next_cursor)
                self.highlight_current_line()

    def select_word_at_cursor(self):
        """Select the word under the cursor."""
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        if cursor.hasSelection():
            self.multi_select_search_text = cursor.selectedText()
            self.setTextCursor(cursor)
            self.highlight_current_line()

    def find_next_occurrence(self, from_cursor: QTextCursor) -> QTextCursor | None:
        """Find the next occurrence of the search text after the given cursor."""
        if not self.multi_select_search_text:
            return None
        
        doc = self.document()
        search_text = self.multi_select_search_text
        
        # Start searching from the end of the current selection
        start_pos = from_cursor.selectionEnd()
        
        # Search forward from current position
        search_cursor = doc.find(search_text, start_pos)
        
        # If not found, wrap around to the beginning
        if search_cursor.isNull():
            search_cursor = doc.find(search_text, 0)
        
        if not search_cursor.isNull():
            return search_cursor
        
        return None

    def clear_extra_cursors(self):
        """Clear all extra cursors and reset multi-select state."""
        self.extra_cursors.clear()
        self.multi_select_search_text = ""
        self.highlight_current_line()

    def handle_multi_cursor_backspace(self):
        """Handle backspace for all cursors."""
        # Collect all cursors including the primary one
        all_cursors = [self.textCursor()] + self.extra_cursors
        
        # Sort by position in reverse order to preserve positions during edits
        all_cursors.sort(key=lambda c: c.selectionStart(), reverse=True)
        
        # Begin edit block for undo grouping
        primary_cursor = self.textCursor()
        primary_cursor.beginEditBlock()
        
        for cursor in all_cursors:
            if cursor.hasSelection():
                cursor.removeSelectedText()
            else:
                cursor.deletePreviousChar()
        
        primary_cursor.endEditBlock()
        
        # Update primary cursor and extra cursors
        self.setTextCursor(all_cursors[-1])  # Last in sorted order = first in document
        self.extra_cursors = all_cursors[:-1]
        self.highlight_current_line()

    def handle_multi_cursor_delete(self):
        """Handle delete key for all cursors."""
        all_cursors = [self.textCursor()] + self.extra_cursors
        all_cursors.sort(key=lambda c: c.selectionStart(), reverse=True)
        
        primary_cursor = self.textCursor()
        primary_cursor.beginEditBlock()
        
        for cursor in all_cursors:
            if cursor.hasSelection():
                cursor.removeSelectedText()
            else:
                cursor.deleteChar()
        
        primary_cursor.endEditBlock()
        
        self.setTextCursor(all_cursors[-1])
        self.extra_cursors = all_cursors[:-1]
        self.highlight_current_line()

    def handle_multi_cursor_insert(self, text: str):
        """Insert text at all cursor positions."""
        all_cursors = [self.textCursor()] + self.extra_cursors
        all_cursors.sort(key=lambda c: c.selectionStart(), reverse=True)
        
        primary_cursor = self.textCursor()
        primary_cursor.beginEditBlock()
        
        for cursor in all_cursors:
            cursor.insertText(text)
        
        primary_cursor.endEditBlock()
        
        # After insertion, update cursor positions
        # The cursors have already moved due to insertText
        self.setTextCursor(all_cursors[-1])
        self.extra_cursors = all_cursors[:-1]
        self.highlight_current_line()


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

        # Add the page break hint
        page_break_hint = QLabel("+++ -> page break (on its own line)")
        page_break_hint.setObjectName("page-break-hint")
        page_break_hint.setStyleSheet(f"""
            color: {COLORS['text_muted']};
            font-size: 9px; /* Smaller font */
            padding: {SPACING['xs']}px {SPACING['md']}px;
            background-color: {COLORS['bg_base']};
            border-top: 1px solid {COLORS['border']};
        """)
        layout.addWidget(page_break_hint)

    def set_text(self, text):
        self.editor.setPlainText(text)

    def get_text(self):
        return self.editor.toPlainText()

    @property
    def textChanged(self):
        return self.editor.textChanged
