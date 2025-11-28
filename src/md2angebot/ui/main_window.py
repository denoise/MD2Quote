import os
import re
import yaml
from PyQt6.QtWidgets import (QMainWindow, QSplitter, QFileDialog, QMessageBox, 
                             QToolBar, QStatusBar, QApplication, QComboBox, QLabel, QWidget, QInputDialog,
                             QVBoxLayout, QHBoxLayout, QToolButton, QFrame)
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QFont
from PyQt6.QtCore import Qt, QTimer, QDir

from .editor import EditorWidget
from .preview import PreviewWidget
from .header import HeaderWidget
from .styles import get_stylesheet, COLORS
from ..core.parser import MarkdownParser
from ..core.renderer import TemplateRenderer
from ..core.pdf import PDFGenerator
from ..core.config import config


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MD2Angebot")
        self.resize(1400, 900)
        
        # Apply modern styling
        self.setStyleSheet(get_stylesheet())

        # Core components
        self.parser = MarkdownParser()
        self.renderer = TemplateRenderer()
        self.pdf_generator = PDFGenerator()
        
        # State
        self.current_file = None
        self.is_modified = False
        self.current_quote_type = "code"  # Default

        # UI Setup
        self._setup_ui()
        self._setup_toolbar()
        
        # Live Preview Timer (Debounce)
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.setInterval(800)  # Slightly faster response
        self.preview_timer.timeout.connect(self.refresh_preview)
        
        # Connect editor
        self.editor.textChanged.connect(self.on_text_changed)

        # Connect Header
        self.header.dataChanged.connect(self.on_header_changed)
        
        # Initial empty state
        self.statusbar.showMessage("Ready — Select a quote type to begin")
        
        # Ask for quote type on startup
        QTimer.singleShot(100, self.ask_quote_type)

    def _setup_ui(self):
        # Main Container
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header Widget (Top)
        self.header = HeaderWidget()
        self.header.setObjectName("header-widget")
        main_layout.addWidget(self.header)

        # Content Area (Editor + Preview)
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Splitter for editor and preview
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        content_layout.addWidget(self.splitter)

        # Editor (Left)
        self.editor = EditorWidget()
        self.splitter.addWidget(self.editor)

        # Preview (Right)
        self.preview = PreviewWidget()
        self.splitter.addWidget(self.preview)

        # Set initial sizes (slightly favor preview)
        self.splitter.setSizes([600, 700])
        
        main_layout.addWidget(content_widget)
        
        # Status bar
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

    def _setup_toolbar(self):
        toolbar = QToolBar("Main")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.addToolBar(toolbar)

        # Open
        open_action = QAction("Open", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.setToolTip("Open Markdown file (⌘O)")
        open_action.triggered.connect(self.open_file_dialog)
        toolbar.addAction(open_action)

        # Save
        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.setToolTip("Save file (⌘S)")
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)

        toolbar.addSeparator()

        # Quote Type Selector with label
        type_label = QLabel("Type")
        type_label.setStyleSheet(f"""
            color: {COLORS['text_muted']};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding-right: 8px;
        """)
        toolbar.addWidget(type_label)
        
        self.type_combo = QComboBox()
        self.type_combo.setMinimumWidth(180)
        self.update_quote_types()
        self.type_combo.currentTextChanged.connect(self.on_quote_type_changed)
        toolbar.addWidget(self.type_combo)

        toolbar.addSeparator()

        # Export PDF
        export_action = QAction("Export PDF", self)
        export_action.setShortcut("Ctrl+E")
        export_action.setToolTip("Export to PDF (⌘E)")
        export_action.triggered.connect(self.export_pdf_dialog)
        # Style the export button differently
        toolbar.addAction(export_action)

    def update_quote_types(self):
        quote_types = config.get('quote_types', {})
        self.type_combo.clear()
        
        if not quote_types:
            self.type_combo.addItem("Code / Development", "code")
        else:
            for key, data in quote_types.items():
                self.type_combo.addItem(data.get('name', key), key)
                
        # Set current selection
        index = self.type_combo.findData(self.current_quote_type)
        if index >= 0:
            self.type_combo.setCurrentIndex(index)

    def ask_quote_type(self):
        """Shows a dialog to select the quote type on startup."""
        quote_types = config.get('quote_types', {})
        if not quote_types:
            return

        items = [data.get('name', key) for key, data in quote_types.items()]
        name_to_key = {data.get('name', key): key for key, data in quote_types.items()}
        
        current_name = quote_types.get(self.current_quote_type, {}).get('name', self.current_quote_type)
        if current_name not in items:
            current_name = items[0] if items else ""
            
        try:
            current_index = items.index(current_name)
        except ValueError:
            current_index = 0

        item, ok = QInputDialog.getItem(
            self, 
            "Select Quote Type", 
            "Choose the type of quotation:",
            items, 
            current_index, 
            False
        )
        
        if ok and item:
            selected_key = name_to_key.get(item)
            if selected_key:
                self.set_quote_type(selected_key)

    def set_quote_type(self, quote_type):
        self.current_quote_type = quote_type
        index = self.type_combo.findData(quote_type)
        if index >= 0:
            self.type_combo.blockSignals(True)
            self.type_combo.setCurrentIndex(index)
            self.type_combo.blockSignals(False)
        
        self.refresh_preview()

    def on_quote_type_changed(self, text):
        quote_type = self.type_combo.currentData()
        if quote_type:
            self.current_quote_type = quote_type
            self.refresh_preview()

    def on_text_changed(self):
        self.is_modified = True
        self.statusbar.showMessage("Modified")
        self.preview_timer.start()

    def on_header_changed(self):
        self.is_modified = True
        self.statusbar.showMessage("Modified")
        self.preview_timer.start()

    def _get_safe_context(self, metadata, html_body):
        """Ensures context has all required fields with defaults to prevent template errors."""
        defaults = {
            "quotation": {
                "number": "DRAFT",
                "date": "YYYY-MM-DD",
                "valid_days": 30
            },
            "client": {
                "name": "Client Name",
                "address": "Client Address",
                "email": "client@example.com"
            }
        }

        context = defaults.copy()
        
        for key in defaults:
            if key in metadata and isinstance(metadata[key], dict):
                context[key] = {**defaults[key], **metadata[key]}
            elif key in metadata:
                context[key] = metadata[key]
        
        for key, value in metadata.items():
            if key not in defaults:
                context[key] = value

        context["content"] = html_body
        
        # Logo Override Logic
        base_company = config.get('company', {}).copy()
        
        if 'company' in metadata:
            if isinstance(metadata['company'], dict):
                base_company.update(metadata['company'])
        
        logo_path = config.get_logo_path(self.current_quote_type)
        if logo_path:
            base_company['logo'] = logo_path
            
        context['company'] = base_company
        
        return context

    def _merge_header_data(self, metadata, header_data):
        """Merges header data into metadata, prioritizing header data."""
        for section in ['quotation', 'client']:
            if section in header_data and header_data[section]:
                if section not in metadata:
                    metadata[section] = {}
                elif not isinstance(metadata[section], dict):
                    metadata[section] = {}
                
                for k, v in header_data[section].items():
                    if v:
                        metadata[section][k] = v

    def refresh_preview(self):
        """Generates PDF in memory and updates preview."""
        content = self.editor.get_text()
        
        try:
            self.statusbar.showMessage("Rendering preview...")
            metadata, html_body = self.parser.parse_text(content)
            self._merge_header_data(metadata, self.header.get_data())
            context = self._get_safe_context(metadata, html_body)
            template_name = metadata.get("template", "base")
            full_html = self.renderer.render(template_name, context)
            pdf_bytes = self.pdf_generator.generate_bytes(full_html)
            
            self.preview.update_preview(pdf_bytes)
            
            # Show current type in status
            type_name = self.type_combo.currentText()
            self.statusbar.showMessage(f"Preview updated — {type_name}")
            
        except Exception as e:
            self.statusbar.showMessage(f"Preview error: {str(e)}")
            print(f"Preview Error: {e}")

    def open_file_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 
            "Open Markdown", 
            QDir.homePath(), 
            "Markdown Files (*.md)"
        )
        if path:
            self.load_file(path)

    def load_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
            self.editor.set_text(text)
            
            metadata, _ = self.parser.parse_text(text)
            self.header.set_data(metadata)

            self.current_file = path
            self.setWindowTitle(f"MD2Angebot — {os.path.basename(path)}")
            self.is_modified = False
            self.refresh_preview()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file: {e}")

    def _merge_header_to_text(self, text, header_data):
        """Updates YAML frontmatter in text with header data."""
        frontmatter_regex = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
        match = frontmatter_regex.match(text)
        
        if match:
            existing_yaml = match.group(1)
            try:
                metadata = yaml.safe_load(existing_yaml) or {}
            except:
                metadata = {}
            body = text[match.end():]
        else:
            metadata = {}
            body = text

        self._merge_header_data(metadata, header_data)
        
        new_yaml = yaml.dump(metadata, allow_unicode=True, sort_keys=False)
        return f"---\n{new_yaml}---\n{body}"

    def save_file(self):
        if not self.current_file:
            path, _ = QFileDialog.getSaveFileName(
                self, 
                "Save Markdown", 
                QDir.homePath(), 
                "Markdown Files (*.md)"
            )
            if not path:
                return
            self.current_file = path

        try:
            current_text = self.editor.get_text()
            header_data = self.header.get_data()
            new_text = self._merge_header_to_text(current_text, header_data)
            
            self.editor.set_text(new_text)
            
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(new_text)
            
            self.is_modified = False
            self.setWindowTitle(f"MD2Angebot — {os.path.basename(self.current_file)}")
            self.statusbar.showMessage("Saved successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file: {e}")

    def export_pdf_dialog(self):
        default_name = "quotation.pdf"
        if self.current_file:
            default_name = os.path.splitext(os.path.basename(self.current_file))[0] + ".pdf"
            
        path, _ = QFileDialog.getSaveFileName(
            self, 
            "Export PDF", 
            os.path.join(QDir.homePath(), default_name), 
            "PDF Files (*.pdf)"
        )
        if path:
            try:
                content = self.editor.get_text()
                header_data = self.header.get_data()
                
                metadata, html_body = self.parser.parse_text(content)
                self._merge_header_data(metadata, header_data)
                context = self._get_safe_context(metadata, html_body)
                full_html = self.renderer.render(metadata.get("template", "base"), context)
                
                self.pdf_generator.generate(full_html, path)
                self.statusbar.showMessage(f"Exported to {path}")
                QMessageBox.information(self, "Success", "PDF exported successfully!")
            except Exception as e:
                self.statusbar.showMessage(f"Export error: {str(e)}")
                QMessageBox.critical(self, "Error", f"Export failed: {e}")
                print(f"Export Error: {e}")
