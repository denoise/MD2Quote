import copy
import json
import os
import re
import yaml
from PyQt6.QtWidgets import (QMainWindow, QSplitter, QFileDialog, QMessageBox, 
                             QToolBar, QStatusBar, QApplication, QComboBox, QLabel, QWidget, QInputDialog,
                             QVBoxLayout, QHBoxLayout, QToolButton, QFrame, QSizePolicy, QListView, QAbstractItemView)
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QFont
from PyQt6.QtCore import Qt, QTimer, QDir, QSettings, QThread, pyqtSignal, QObject

from .editor import EditorWidget
from .preview import PreviewWidget
from .header import HeaderWidget
from .config_dialog import ConfigDialog, SettingsDialog
from .styles import get_stylesheet, COLORS
from .icons import icon, icon_font, icon_char
from ..core.parser import MarkdownParser
from ..core.renderer import TemplateRenderer
from ..core.pdf import PDFGenerator
from ..core.config import config
from ..core.llm import LLMService, LLMError


class ProfileComboBox(QComboBox):
    """Custom QComboBox that correctly highlights the current item when dropdown opens."""
    
    def showPopup(self):
        """Override to sync the view's selection with the combobox's current index."""
        view = self.view()
        if view:
            # Set the view's current index to match the combobox's current index
            model_index = self.model().index(self.currentIndex(), 0)
            view.setCurrentIndex(model_index)
            # Scroll to make sure the current item is visible
            view.scrollTo(model_index, QAbstractItemView.ScrollHint.PositionAtCenter)
        super().showPopup()
        
        # Offset the popup position to avoid collision with first option
        popup = self.findChild(QFrame)
        if popup:
            pos = popup.pos()
            popup.move(pos.x() + 8, pos.y() + 8)


class LLMWorker(QObject):
    """Worker for running LLM requests in a background thread."""
    
    finished = pyqtSignal(str)  # Emits the generated content
    error = pyqtSignal(str)     # Emits error message
    
    def __init__(self, llm_service: LLMService, instruction: str, context: str):
        super().__init__()
        self.llm_service = llm_service
        self.instruction = instruction
        self.context = context
    
    def run(self):
        """Execute the LLM request."""
        try:
            result = self.llm_service.generate(self.instruction, self.context)
            self.finished.emit(result)
        except LLMError as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(f"Unexpected error: {e}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MD2Angebot")
        self.resize(1400, 900)
        
        # Apply modern styling
        self.setStyleSheet(get_stylesheet())

        # Settings for remembering user preferences
        self.settings = QSettings("MD2Angebot", "MD2Angebot")

        # Core components
        self.parser = MarkdownParser()
        self.renderer = TemplateRenderer()
        self.pdf_generator = PDFGenerator()
        self.llm_service = LLMService(config)
        
        # LLM thread management
        self.llm_thread = None
        self.llm_worker = None
        
        # State
        self.current_file = None
        self.is_modified = False
        # Default to active preset from config
        self.current_preset = config.get_active_preset_name()

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
        self.header.llmRequestSubmitted.connect(self.on_llm_request)

        # Restore last client info if available
        self._restore_last_client_data()
        
        # Initial empty state
        self.statusbar.showMessage("Ready — Select a preset to begin")
        
        # Ask for preset on startup if not set (or just sync UI)
        # Actually, let's just sync UI since we have a default from config now
        QTimer.singleShot(100, self.sync_preset_ui)
        
        # Update LLM button state on startup
        QTimer.singleShot(100, self._update_llm_button_state)

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
        self.header.generateQuotationRequested.connect(self._generate_new_quotation_number)
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
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        toolbar.setIconSize(toolbar.iconSize().__class__(20, 20))
        self.addToolBar(toolbar)

        # New
        new_action = QAction(icon('add_circle', 20, COLORS['text_secondary']), "New", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.setToolTip("New Quotation (⌘N)")
        new_action.triggered.connect(self.new_file)
        toolbar.addAction(new_action)

        # Open
        open_action = QAction(icon('folder_open', 20, COLORS['text_secondary']), "Open", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.setToolTip("Open Markdown file (⌘O)")
        open_action.triggered.connect(self.open_file_dialog)
        toolbar.addAction(open_action)

        # Save
        save_action = QAction(icon('save', 20, COLORS['text_secondary']), "Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.setToolTip("Save file (⌘S)")
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)

        toolbar.addSeparator()

        # Preset Selector with label
        type_label = QLabel("Profile")
        type_label.setStyleSheet(f"""
            color: {COLORS['text_muted']};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding-right: 8px;
        """)
        toolbar.addWidget(type_label)
        
        self.preset_combo = ProfileComboBox()
        self.preset_combo.setView(QListView())
        self.preset_combo.setMinimumWidth(200)
        self.update_preset_selector()
        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)
        toolbar.addWidget(self.preset_combo)

        toolbar.addSeparator()

        # Export PDF
        export_action = QAction(icon('picture_as_pdf', 20, COLORS['text_secondary']), "Export", self)
        export_action.setShortcut("Ctrl+E")
        export_action.setToolTip("Export to PDF (⌘E)")
        export_action.triggered.connect(self.export_pdf_dialog)
        toolbar.addAction(export_action)

        # Spacer to push Profiles and Settings to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        # Profiles
        profiles_action = QAction(icon('badge', 20, COLORS['text_secondary']), "Profiles", self)
        profiles_action.setShortcut("Ctrl+P")
        profiles_action.setToolTip("Manage Profiles (⌘P)")
        profiles_action.triggered.connect(self.open_profiles)
        toolbar.addAction(profiles_action)

        # Settings
        settings_action = QAction(icon('settings', 20, COLORS['text_secondary']), "Settings", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.setToolTip("Open Settings (⌘,)")
        settings_action.triggered.connect(self.open_settings)
        toolbar.addAction(settings_action)

        # --- Invisible Global Actions ---
        
        # Save As
        save_as_action = QAction("Save As", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.save_file_as)
        self.addAction(save_as_action)

        # Print (Alias to Export)
        print_action = QAction("Print", self)
        print_action.setShortcut(QKeySequence.StandardKey.Print)
        print_action.triggered.connect(self.export_pdf_dialog)
        self.addAction(print_action)

        # Refresh
        refresh_action = QAction("Refresh", self)
        refresh_action.setShortcut(QKeySequence.StandardKey.Refresh)
        refresh_action.triggered.connect(self.refresh_preview)
        self.addAction(refresh_action)

    def update_preset_selector(self):
        """Updates the preset combo box from config."""
        presets = config.get('presets', {})
        self.preset_combo.blockSignals(True)
        self.preset_combo.clear()
        
        # Sort by key to ensure order 1-5
        for key in sorted(presets.keys()):
            data = presets[key]
            # Extract number from key e.g. preset_1 -> 1
            num = key.split('_')[-1]
            name = data.get('name', f"Preset {num}")
            self.preset_combo.addItem(f"{num}. {name}", key)
                
        # Set current selection
        index = self.preset_combo.findData(self.current_preset)
        if index >= 0:
            self.preset_combo.setCurrentIndex(index)
        self.preset_combo.blockSignals(False)

    def sync_preset_ui(self):
        """Syncs the UI to the current preset state."""
        self.current_preset = config.get_active_preset_name()
        index = self.preset_combo.findData(self.current_preset)
        if index >= 0:
            self.preset_combo.setCurrentIndex(index)
        else:
            # Fallback to first if active not found
            if self.preset_combo.count() > 0:
                self.preset_combo.setCurrentIndex(0)
                self.current_preset = self.preset_combo.currentData()
        
        # Populate quotation number field with the last used value for this preset
        last_number = config.get_last_quotation_number(self.current_preset)
        if last_number:
            self.header.quote_number_edit.setText(last_number)
        else:
            self.header.quote_number_edit.clear()
            self.header.quote_number_edit.setPlaceholderText("e.g. 2025-001")

        self.refresh_preview()

    def on_preset_changed(self, text):
        preset_key = self.preset_combo.currentData()
        if preset_key:
            self.current_preset = preset_key
            config.set_active_preset(preset_key)
            
            # Show the last used quotation number for this preset
            last_number = config.get_last_quotation_number(self.current_preset)
            if last_number:
                self.header.quote_number_edit.setText(last_number)
            else:
                self.header.quote_number_edit.clear()
                self.header.quote_number_edit.setPlaceholderText("e.g. 2025-001")
            
            self.refresh_preview()
    
    def _generate_new_quotation_number(self):
        """Generates a new quotation number based on the current preset's format."""
        quotation_number = config.generate_quotation_number(self.current_preset)
        
        if quotation_number:
            self.header.quote_number_edit.setText(quotation_number)
            self.statusbar.showMessage(f"New quotation: {quotation_number}")
        else:
            # Quotation numbering is disabled for this preset
            self.header.quote_number_edit.clear()
            self.header.quote_number_edit.setPlaceholderText("(numbering disabled)")

    def on_text_changed(self):
        self.is_modified = True
        self.statusbar.showMessage("Modified")
        self.preview_timer.start()

    def on_header_changed(self):
        self.is_modified = True
        self.statusbar.showMessage("Modified")
        self._persist_last_client_data()
        self.preview_timer.start()

    def on_llm_request(self, instruction: str):
        """Handle LLM request from the header panel."""
        # Check if instruction is empty
        if not instruction:
            QMessageBox.information(
                self,
                "No Instruction",
                "Please enter an instruction in the LLM text field."
            )
            return
        
        # Check if LLM is configured
        if not self.llm_service.is_configured():
            reply = QMessageBox.question(
                self,
                "LLM Not Configured",
                "No API key configured. Would you like to open Settings to configure it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.open_settings()
            return
        
        # Get current editor content as context
        context = self.editor.get_text()
        
        # Show loading state
        self.header.set_llm_loading(True)
        self.statusbar.showMessage("Generating content with LLM...")
        
        # Create worker and thread
        self.llm_thread = QThread()
        self.llm_worker = LLMWorker(self.llm_service, instruction, context)
        self.llm_worker.moveToThread(self.llm_thread)
        
        # Connect signals
        self.llm_thread.started.connect(self.llm_worker.run)
        self.llm_worker.finished.connect(self._on_llm_success)
        self.llm_worker.error.connect(self._on_llm_error)
        self.llm_worker.finished.connect(self.llm_thread.quit)
        self.llm_worker.error.connect(self.llm_thread.quit)
        self.llm_thread.finished.connect(self._cleanup_llm_thread)
        
        # Start the thread
        self.llm_thread.start()

    def _on_llm_success(self, content: str):
        """Handle successful LLM response."""
        # Insert content into editor
        self.editor.set_text(content)
        
        # Reset UI state
        self.header.set_llm_loading(False)
        self.header.clear_llm_instruction()
        self.statusbar.showMessage("Content generated successfully")
        
        # Mark as modified and refresh preview
        self.is_modified = True
        self.preview_timer.start()

    def _on_llm_error(self, error_message: str):
        """Handle LLM error."""
        self.header.set_llm_loading(False)
        self.statusbar.showMessage("LLM request failed")
        
        QMessageBox.critical(
            self,
            "LLM Error",
            f"Failed to generate content:\n\n{error_message}"
        )

    def _cleanup_llm_thread(self):
        """Clean up the LLM thread after it finishes."""
        if self.llm_thread:
            self.llm_thread.deleteLater()
            self.llm_thread = None
        if self.llm_worker:
            self.llm_worker.deleteLater()
            self.llm_worker = None

    def _update_llm_button_state(self):
        """Update LLM send button enabled state based on configuration."""
        # Always enable the button - we'll show a helpful message if not configured
        if self.llm_service.is_configured():
            self.header.set_llm_enabled(True, "Send instruction to LLM")
        else:
            self.header.set_llm_enabled(True, "Click to configure LLM (no API key set)")

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
        
        # --- PRESET CONFIG INTEGRATION ---
        # Load full config from the selected preset (deep copy to avoid modifying original)
        preset_config = copy.deepcopy(config.get_preset(self.current_preset))
        
        # Allow metadata overrides if specified in markdown (optional feature)
        if 'company' in metadata and isinstance(metadata['company'], dict):
            # We deep merge or just update top level? 
            # Let's do a simple update for now to allow overrides
            if 'company' not in preset_config:
                preset_config['company'] = {}
            preset_config['company'].update(metadata['company'])
        
        # Resolve logo path to absolute file:// URL for WeasyPrint
        if 'company' in preset_config and preset_config['company'].get('logo'):
            logo_str = preset_config['company']['logo']
            # Skip if already a file:// URL
            if not logo_str.startswith('file://'):
                logo_path = config.resolve_path(logo_str)
                if logo_path and logo_path.exists():
                    # Use Path.as_uri() for proper URL encoding (handles spaces, special chars)
                    preset_config['company']['logo'] = logo_path.as_uri()
                else:
                    # Clear invalid logo path to prevent broken image
                    preset_config['company']['logo'] = ''
            
        # Add the preset config to the context
        # We need to ensure company, contact, bank, legal, etc. are in context root
        # ConfigLoader returns { company: ..., contact: ... } so we update context with it
        context.update(preset_config)
        
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
            
            # Get context which includes preset data
            context = self._get_safe_context(metadata, html_body)
            
            template_name = metadata.get("template", "base")
            
            # Pass preset key to renderer if needed, but actually we passed full context
            # The renderer might need to know where to look for templates?
            # Current renderer takes (template_name, context).
            # And inside context we have all the config.
            # But `renderer.render` also merges `config.config` in the original code.
            # We should update the renderer to NOT merge the global config blindly,
            # or we should ensure `context` overrides it. 
            # Actually, `renderer.render` logic was: `full_context = {**config.config, **context}`.
            # `config.config` is now the root dict with `presets`.
            # So the old renderer logic of accessing `{{ company.name }}` from `config.config` will fail
            # because `company` is no longer at root of `config.config`.
            # We need to fix the renderer to accept the PRESET config.
            
            full_html = self.renderer.render(template_name, context, preset_config=context) # Passing context as config too
            pdf_bytes = self.pdf_generator.generate_bytes(full_html)
            
            self.preview.update_preview(pdf_bytes)
            
            # Show current type in status
            preset_name = self.preset_combo.currentText()
            self.statusbar.showMessage(f"Preview updated — {preset_name}")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.statusbar.showMessage(f"Preview error: {str(e)}")
            print(f"Preview Error: {e}")

    def _get_last_folder(self) -> str:
        """Returns the last opened folder, or home directory if not set."""
        return self.settings.value("last_folder", QDir.homePath())
    
    def _set_last_folder(self, path: str):
        """Saves the folder of the given file path as the last opened folder."""
        folder = os.path.dirname(path)
        if folder:
            self.settings.setValue("last_folder", folder)

    def _persist_last_client_data(self, client_data=None):
        """Save last client data so new sessions can reuse it."""
        if client_data is None:
            client_data = self.header.get_data().get("client", {})
        try:
            self.settings.setValue("last_client", json.dumps(client_data))
        except TypeError:
            # Ignore values that cannot be serialized
            pass

    def _load_last_client_data(self):
        """Load last client data if present."""
        raw = self.settings.value("last_client")
        if not raw:
            return None
        if isinstance(raw, dict):
            return raw
        try:
            return json.loads(raw)
        except Exception:
            return None

    def _restore_last_client_data(self):
        """Populate header with last client info if available."""
        client_data = self._load_last_client_data()
        if client_data:
            self.header.set_data({"client": client_data})

    def open_file_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 
            "Open Markdown", 
            self._get_last_folder(), 
            "Markdown Files (*.md)"
        )
        if path:
            self._set_last_folder(path)
            self.load_file(path)

    def load_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
            self.editor.set_text(text)
            
            metadata, _ = self.parser.parse_text(text)
            self.header.set_data(metadata)
            self._persist_last_client_data(metadata.get("client", {}))

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
                self._get_last_folder(), 
                "Markdown Files (*.md)"
            )
            if not path:
                return
            self._set_last_folder(path)
            self.current_file = path

        try:
            current_text = self.editor.get_text()
            header_data = self.header.get_data()
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(current_text)
            
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
            os.path.join(self._get_last_folder(), default_name), 
            "PDF Files (*.pdf)"
        )
        if path:
            self._set_last_folder(path)
            try:
                content = self.editor.get_text()
                header_data = self.header.get_data()
                
                metadata, html_body = self.parser.parse_text(content)
                self._merge_header_data(metadata, header_data)
                
                # Use safe context which uses preset
                context = self._get_safe_context(metadata, html_body)
                
                # Use current preset for rendering
                # Note: context already contains the preset data
                full_html = self.renderer.render(metadata.get("template", "base"), context, preset_config=context)
                
                self.pdf_generator.generate(full_html, path)
                self.statusbar.showMessage(f"Exported to {path}")
                QMessageBox.information(self, "Success", "PDF exported successfully!")
            except Exception as e:
                self.statusbar.showMessage(f"Export error: {str(e)}")
                QMessageBox.critical(self, "Error", f"Export failed: {e}")
                print(f"Export Error: {e}")

    def new_file(self):
        if self.is_modified:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Create new file anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        self.editor.set_text("")
        if hasattr(self.header, 'clear_data'):
            self.header.clear_data()
            self._restore_last_client_data()
        self.current_file = None
        self.setWindowTitle("MD2Angebot")
        self.is_modified = False
        self.statusbar.showMessage("New file created")

    def save_file_as(self):
        old_file = self.current_file
        self.current_file = None # Force dialog
        self.save_file()
        if not self.current_file: # User cancelled
            self.current_file = old_file

    def open_profiles(self):
        """Opens the profiles configuration dialog."""
        dialog = ConfigDialog(config, initial_preset_key=self.current_preset, parent=self)
        dialog.configSaved.connect(self.on_config_saved)
        dialog.exec()

    def open_settings(self):
        """Opens the settings dialog for LLM configuration."""
        dialog = SettingsDialog(config, parent=self)
        dialog.configSaved.connect(self.on_config_saved)
        dialog.exec()

    def on_config_saved(self):
        """Called when configuration is saved."""
        # Reload the config
        config._ensure_config_exists()
        config.config = config._load_config()
        
        # Re-initialize renderer to pick up any template changes
        self.renderer = TemplateRenderer()
        
        # Update preset selector
        self.update_preset_selector()
        self.sync_preset_ui()
        
        # Update LLM button state based on API key configuration
        self._update_llm_button_state()
        
        self.statusbar.showMessage("Configuration updated")
