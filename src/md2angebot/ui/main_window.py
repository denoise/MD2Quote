import os
from PyQt6.QtWidgets import (QMainWindow, QSplitter, QFileDialog, QMessageBox, 
                             QToolBar, QStatusBar, QApplication)
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from PyQt6.QtCore import Qt, QTimer, QDir

from .editor import EditorWidget
from .preview import PreviewWidget
from ..core.parser import MarkdownParser
from ..core.renderer import TemplateRenderer
from ..core.pdf import PDFGenerator

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MD2Angebot")
        self.resize(1200, 800)

        # Core components
        self.parser = MarkdownParser()
        self.renderer = TemplateRenderer()
        self.pdf_generator = PDFGenerator()
        
        # State
        self.current_file = None
        self.is_modified = False

        # UI Setup
        self._setup_ui()
        self._setup_actions()
        
        # Live Preview Timer (Debounce)
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.setInterval(1000) # 1 second delay
        self.preview_timer.timeout.connect(self.refresh_preview)
        
        # Connect editor
        self.editor.textChanged.connect(self.on_text_changed)
        
        # Initial empty state
        self.statusbar.showMessage("Ready")

    def _setup_ui(self):
        # Splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(self.splitter)

        # Editor (Left)
        self.editor = EditorWidget()
        self.splitter.addWidget(self.editor)

        # Preview (Right)
        self.preview = PreviewWidget()
        self.splitter.addWidget(self.preview)

        # Ratios (50/50)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
        
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

    def _setup_actions(self):
        toolbar = QToolBar("Main")
        self.addToolBar(toolbar)

        # Open
        open_action = QAction("Open", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file_dialog)
        toolbar.addAction(open_action)

        # Save
        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)

        # Export PDF
        export_action = QAction("Export PDF", self)
        # Cmd+E is not a standard key, create manually
        export_action.setShortcut("Ctrl+E") 
        export_action.triggered.connect(self.export_pdf_dialog)
        toolbar.addAction(export_action)

    def on_text_changed(self):
        self.is_modified = True
        self.statusbar.showMessage("Modified")
        self.preview_timer.start() # Restart timer

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
        
        # Merge metadata into context (handling nested dicts for known keys)
        for key in defaults:
            if key in metadata and isinstance(metadata[key], dict):
                context[key] = {**defaults[key], **metadata[key]}
            elif key in metadata:
                context[key] = metadata[key]
        
        # Add remaining metadata
        for key, value in metadata.items():
            if key not in defaults:
                context[key] = value

        context["content"] = html_body
        return context

    def refresh_preview(self):
        """Generates PDF in memory and updates preview."""
        content = self.editor.get_text()
        if not content.strip():
            return

        try:
            self.statusbar.showMessage("Rendering preview...")
            # 1. Parse
            metadata, html_body = self.parser.parse_text(content)
            
            # 2. Render HTML
            context = self._get_safe_context(metadata, html_body)
            template_name = metadata.get("template", "base")
            full_html = self.renderer.render(template_name, context)
            
            # 3. Generate PDF bytes
            # WeasyPrint can write to a file-like object (BytesIO) but it's simpler to just write to a tmp file 
            # OR use write_pdf() which returns bytes if target is None? 
            # Checking WeasyPrint docs: HTML(...).write_pdf() returns bytes if target is None.
            
            # We need the PDF generator to support returning bytes
            from weasyprint import HTML, CSS
            from ..core.config import config
            
            # Re-implementing minimal generation here to get bytes
            # or update PDFGenerator to support bytes return
            
            # Load CSS
            css_files = []
            base_css_path = config.templates_dir.parent / 'templates' / 'quotation.css' # This path logic in config/pdf need syncing
            # Use the logic from pdf.py, but let's just call the generator if we modify it to return bytes
            # For now, inline for simplicity of "in-memory"
            
            from ..core.pdf import PDFGenerator
            # I'll modify PDFGenerator in a moment to support returning bytes
            pdf_bytes = self.pdf_generator.generate_bytes(full_html)
            
            self.preview.update_preview(pdf_bytes)
            self.statusbar.showMessage("Preview updated")
            
        except Exception as e:
            self.statusbar.showMessage(f"Preview error: {str(e)}")
            print(f"Preview Error: {e}")

    def open_file_dialog(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Markdown", QDir.homePath(), "Markdown Files (*.md)")
        if path:
            self.load_file(path)

    def load_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
            self.editor.set_text(text)
            self.current_file = path
            self.setWindowTitle(f"MD2Angebot - {os.path.basename(path)}")
            self.is_modified = False
            self.refresh_preview()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file: {e}")

    def save_file(self):
        if not self.current_file:
            path, _ = QFileDialog.getSaveFileName(self, "Save Markdown", QDir.homePath(), "Markdown Files (*.md)")
            if not path:
                return
            self.current_file = path

        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(self.editor.get_text())
            self.is_modified = False
            self.setWindowTitle(f"MD2Angebot - {os.path.basename(self.current_file)}")
            self.statusbar.showMessage("Saved")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file: {e}")

    def export_pdf_dialog(self):
        default_name = "quotation.pdf"
        if self.current_file:
            default_name = os.path.splitext(os.path.basename(self.current_file))[0] + ".pdf"
            
        path, _ = QFileDialog.getSaveFileName(self, "Export PDF", os.path.join(QDir.homePath(), default_name), "PDF Files (*.pdf)")
        if path:
            try:
                # Force a refresh/generation to ensure latest state
                content = self.editor.get_text()
                metadata, html_body = self.parser.parse_text(content)
                context = self._get_safe_context(metadata, html_body)
                
                full_html = self.renderer.render(metadata.get("template", "base"), context)
                
                self.pdf_generator.generate(full_html, path)
                self.statusbar.showMessage(f"Exported to {path}")
                QMessageBox.information(self, "Success", "PDF Exported successfully!")
            except Exception as e:
                self.statusbar.showMessage(f"Export error: {str(e)}")
                QMessageBox.critical(self, "Error", f"Export failed: {e}")
                print(f"Export Error: {e}")

