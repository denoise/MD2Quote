"""
Configuration Assistant Dialog for MD2Angebot.

A visually refined settings dialog with tabs for each configuration category.
"""

import os
import yaml
import copy
import shutil
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox,
    QPushButton, QFileDialog, QScrollArea, QFrame, QGridLayout,
    QGroupBox, QColorDialog, QMessageBox, QSizePolicy, QListWidget,
    QListWidgetItem, QInputDialog, QButtonGroup, QPlainTextEdit, QCheckBox,
    QSlider, QMenu, QToolButton
)
from PyQt6.QtGui import QColor, QPalette, QFont, QIcon, QPixmap, QPainter
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtSvg import QSvgRenderer

from .styles import COLORS, SPACING, RADIUS
from .icons import icon, icon_font, icon_char
from ..utils import get_templates_path
from ..core.llm import OPENROUTER_MODELS, OPENAI_MODELS, DEFAULT_SYSTEM_PROMPT


class TemplateEditorDialog(QDialog):
    """Dialog for editing raw HTML templates."""
    
    def __init__(self, template_name: str, config_loader, parent=None):
        super().__init__(parent)
        self.template_name = template_name
        self.config_loader = config_loader
        self.file_path = self._find_template_path()
        
        self.setWindowTitle(f"Edit Template: {template_name}.html")
        self.resize(900, 700)
        
        self._setup_ui()
        self._load_content()
        
    def _find_template_path(self) -> Path:
        """Find the template file path, prioritizing user config then app templates."""
        filename = f"{self.template_name}.html"
        
        # 1. Check user config templates dir
        user_path = self.config_loader.templates_dir / filename
        if user_path.exists():
            return user_path
            
        # 2. Check app templates dir
        app_path = get_templates_path() / filename
        if app_path.exists():
            return app_path
            
        return None

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(SPACING['md'])
        
        # Header
        header = QHBoxLayout()
        
        path_label = QLabel(f"Editing: {self.file_path}")
        path_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px; font-family: monospace;")
        header.addWidget(path_label)
        
        layout.addLayout(header)
        
        # Editor
        self.editor = QPlainTextEdit()
        self.editor.setStyleSheet(f"""
            QPlainTextEdit {{
                font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
                font-size: 13px;
                background-color: {COLORS['bg_dark']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
            }}
        """)
        layout.addWidget(self.editor)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save Changes")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._save_changes)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                font-weight: 600;
                padding: 6px 16px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #d63650;
            }}
        """)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)

    def _load_content(self):
        if not self.file_path:
            QMessageBox.warning(self, "Error", f"Template file '{self.template_name}.html' not found.")
            self.reject()
            return
            
        try:
            content = self.file_path.read_text(encoding='utf-8')
            self.editor.setPlainText(content)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load template:\n{e}")
            self.reject()

    def _save_changes(self):
        if not self.file_path:
            return
            
        try:
            content = self.editor.toPlainText()
            
            # Confirmation
            reply = QMessageBox.question(
                self,
                "Confirm Save",
                f"Are you sure you want to overwrite the template file?\n{self.file_path}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.file_path.write_text(content, encoding='utf-8')
                QMessageBox.information(self, "Success", "Template saved successfully.")
                self.accept()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save template:\n{e}")


class CSSEditorDialog(QDialog):
    """Dialog for editing raw CSS used by templates."""

    def __init__(self, template_name: str, config_loader, parent=None):
        super().__init__(parent)
        self.template_name = template_name
        self.config_loader = config_loader
        self.file_path = self._find_css_path()

        self.setWindowTitle(f"Edit Template CSS: {template_name}.css")
        self.resize(900, 700)

        self._setup_ui()
        self._load_content()

    def _find_css_path(self) -> Path:
        """Find the CSS file path, prioritizing user config then app templates."""
        filename = f"{self.template_name}.css"

        user_path = self.config_loader.templates_dir / filename
        if user_path.exists():
            return user_path

        app_path = get_templates_path() / filename
        if app_path.exists():
            return app_path

        return None

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(SPACING['md'])

        header = QHBoxLayout()

        path_label = QLabel(f"Editing: {self.file_path}")
        path_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px; font-family: monospace;")
        header.addWidget(path_label)

        layout.addLayout(header)

        self.editor = QPlainTextEdit()
        self.editor.setStyleSheet(f"""
            QPlainTextEdit {{
                font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
                font-size: 13px;
                background-color: {COLORS['bg_dark']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
            }}
        """)
        layout.addWidget(self.editor)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save Changes")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._save_changes)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                font-weight: 600;
                padding: 6px 16px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #d63650;
            }}
        """)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _load_content(self):
        if not self.file_path:
            QMessageBox.warning(self, "Error", f"CSS file '{self.template_name}.css' not found.")
            self.reject()
            return

        try:
            content = self.file_path.read_text(encoding="utf-8")
            self.editor.setPlainText(content)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load CSS:\n{e}")
            self.reject()

    def _save_changes(self):
        if not self.file_path:
            return

        try:
            content = self.editor.toPlainText()

            reply = QMessageBox.question(
                self,
                "Confirm Save",
                f"Are you sure you want to overwrite the CSS file?\n{self.file_path}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.file_path.write_text(content, encoding="utf-8")
                QMessageBox.information(self, "Success", "CSS file saved successfully.")
                self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save CSS:\n{e}")


# Common font families for dropdowns
FONT_FAMILIES = {
    'heading': [
        'Montserrat',
        'Poppins',
        'Raleway',
        'Playfair Display',
        'Merriweather',
        'Oswald',
        'Bebas Neue',
        'Lato',
        'Roboto',
        'Open Sans',
        'Arial',
        'Helvetica Neue',
        'Georgia',
        'Times New Roman',
    ],
    'body': [
        'Source Sans Pro',
        'Open Sans',
        'Lato',
        'Roboto',
        'Inter',
        'Nunito',
        'PT Sans',
        'Work Sans',
        'IBM Plex Sans',
        'Noto Sans',
        'Arial',
        'Helvetica',
        'Georgia',
        'Times New Roman',
    ],
    'mono': [
        'JetBrains Mono',
        'Fira Code',
        'Source Code Pro',
        'IBM Plex Mono',
        'Roboto Mono',
        'SF Mono',
        'Monaco',
        'Menlo',
        'Consolas',
        'Courier New',
    ]
}


class ColorButton(QPushButton):
    """A button that displays and allows selection of a color."""
    
    colorChanged = pyqtSignal(str)
    
    def __init__(self, color: str = "#ffffff", parent=None):
        super().__init__(parent)
        self._color = color
        self.setFixedSize(50, 28)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(self._pick_color)
        self._update_style()
    
    def _update_style(self):
        # Calculate text color based on background brightness
        r, g, b = int(self._color[1:3], 16), int(self._color[3:5], 16), int(self._color[5:7], 16)
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        text_color = "#000000" if brightness > 128 else "#ffffff"
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._color};
                border: 1px solid {COLORS['border']};
                border-radius: 0;
                color: {text_color};
                font-size: 10px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                border-color: {COLORS['accent']};
            }}
        """)
        # Show hex value on button
        self.setText(self._color.upper())
    
    def _pick_color(self):
        color = QColorDialog.getColor(QColor(self._color), self, "Select Color")
        if color.isValid():
            self._color = color.name()
            self._update_style()
            self.colorChanged.emit(self._color)
    
    def color(self) -> str:
        return self._color
    
    def setColor(self, color: str):
        self._color = color
        self._update_style()


class PathSelector(QWidget):
    """A line edit with a browse button for selecting file paths."""
    
    pathChanged = pyqtSignal(str)
    
    def __init__(self, filter_str: str = "All Files (*)", parent=None):
        super().__init__(parent)
        self._filter = filter_str
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING['sm'])
        
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Select a file...")
        self.line_edit.textChanged.connect(self.pathChanged.emit)
        layout.addWidget(self.line_edit)
        
        browse_btn = QPushButton("Browse")
        browse_btn.setFixedWidth(80)
        browse_btn.clicked.connect(self._browse)
        layout.addWidget(browse_btn)
    
    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select File", "", self._filter)
        if path:
            self.line_edit.setText(path)
    
    def path(self) -> str:
        return self.line_edit.text()
    
    def setPath(self, path: str):
        self.line_edit.setText(path or "")


class LogoPreview(QFrame):
    """A preview widget for displaying logo images (supports SVG, PNG, JPG)."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._path = ""
        self._setup_ui()
    
    def _setup_ui(self):
        self.setFixedSize(120, 80)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #ffffff;
                border: 1px dashed {COLORS['border']};
                border-radius: 0;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Image label for the preview
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(self.image_label)
        
        # Placeholder text
        self.placeholder_label = QLabel("No logo")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setStyleSheet(f"""
            color: #999999;
            font-size: 11px;
            background: transparent;
            border: none;
        """)
        layout.addWidget(self.placeholder_label)
        
        # Initially show placeholder
        self._show_placeholder()
    
    def _show_placeholder(self):
        """Show the placeholder text, hide the image."""
        self.image_label.hide()
        self.placeholder_label.show()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #ffffff;
                border: 1px dashed {COLORS['border']};
                border-radius: 0;
            }}
        """)
    
    def _show_image(self, pixmap: QPixmap):
        """Show the image, hide the placeholder."""
        self.placeholder_label.hide()
        self.image_label.show()
        
        # Scale the pixmap to fit within the preview area
        max_size = QSize(104, 64)  # Account for margins
        scaled = pixmap.scaled(
            max_size, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(scaled)
        
        # Update border style to solid when image is present
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #ffffff;
                border: 1px solid {COLORS['border']};
                border-radius: 0;
            }}
        """)
    
    def setPath(self, path: str):
        """Set the logo path and update the preview."""
        self._path = path
        
        if not path:
            self._show_placeholder()
            return
        
        # Check if file exists
        file_path = Path(path)
        if not file_path.exists():
            # Try to expand user path
            file_path = Path(os.path.expanduser(path))
            if not file_path.exists():
                self._show_placeholder()
                return
        
        # Load the image based on file type
        suffix = file_path.suffix.lower()
        
        if suffix == '.svg':
            pixmap = self._load_svg(file_path)
        else:
            pixmap = QPixmap(str(file_path))
        
        if pixmap and not pixmap.isNull():
            self._show_image(pixmap)
        else:
            self._show_placeholder()
    
    def _load_svg(self, file_path: Path) -> QPixmap:
        """Load an SVG file and convert it to a QPixmap."""
        renderer = QSvgRenderer(str(file_path))
        if not renderer.isValid():
            return QPixmap()
        
        # Get the default size and scale it to fit
        default_size = renderer.defaultSize()
        if default_size.isEmpty():
            default_size = QSize(100, 60)
        
        # Scale to fit within max preview size while maintaining aspect ratio
        max_size = QSize(104, 64)
        scale = min(
            max_size.width() / default_size.width(),
            max_size.height() / default_size.height()
        )
        target_size = QSize(
            int(default_size.width() * scale),
            int(default_size.height() * scale)
        )
        
        # Create a pixmap and render the SVG
        pixmap = QPixmap(target_size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        return pixmap


class SectionCard(QFrame):
    """A card container for grouping related settings."""
    
    def __init__(self, title: str = "", with_enable_checkbox: bool = False, parent=None):
        super().__init__(parent)
        self.setObjectName("section-card")
        self._content_widgets = []  # Track widgets to enable/disable
        self._enable_checkbox = None
        
        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(SPACING['sm'])
        self._layout.setContentsMargins(SPACING['md'], SPACING['md'], SPACING['md'], SPACING['md'])
        
        if title:
            if with_enable_checkbox:
                # Create a header row with checkbox
                header_row = QHBoxLayout()
                header_row.setSpacing(SPACING['sm'])
                
                self._enable_checkbox = QCheckBox(title)
                self._enable_checkbox.setObjectName("section-enable-checkbox")
                self._enable_checkbox.setStyleSheet(f"""
                    QCheckBox {{
                        color: {COLORS['accent']};
                        font-size: 12px;
                        font-weight: 700;
                        text-transform: uppercase;
                        letter-spacing: 1px;
                    }}
                    QCheckBox::indicator {{
                        width: 14px;
                        height: 14px;
                        border: 1px solid {COLORS['border']};
                        border-radius: 0;
                        background-color: {COLORS['bg_dark']};
                    }}
                    QCheckBox::indicator:checked {{
                        background-color: {COLORS['accent']};
                        border-color: {COLORS['accent']};
                    }}
                    QCheckBox::indicator:hover {{
                        border-color: {COLORS['accent']};
                    }}
                """)
                self._enable_checkbox.setChecked(True)
                self._enable_checkbox.toggled.connect(self._on_enable_toggled)
                header_row.addWidget(self._enable_checkbox)
                header_row.addStretch()
                
                self._layout.addLayout(header_row)
            else:
                title_label = QLabel(title)
                title_label.setObjectName("section-title")
                title_label.setStyleSheet(f"""
                    QLabel {{
                        color: {COLORS['accent']};
                        font-size: 12px;
                        font-weight: 700;
                        text-transform: uppercase;
                        letter-spacing: 1px;
                        padding-bottom: {SPACING['xs']}px;
                        margin-bottom: 0;
                    }}
                """)
                self._layout.addWidget(title_label)
        
        # Add stretch at the end to push content to the top
        self._layout.addStretch(1)
        
        self.setStyleSheet(f"""
            QFrame#section-card {{
                background-color: {COLORS['bg_elevated']};
                border: 1px solid {COLORS['border']};
                border-radius: 0;
            }}
        """)
    
    def _on_enable_toggled(self, checked: bool):
        """Enable/disable all content widgets based on checkbox state."""
        for widget in self._content_widgets:
            widget.setEnabled(checked)
    
    def enableCheckbox(self) -> QCheckBox:
        """Returns the enable checkbox if one exists."""
        return self._enable_checkbox
    
    def setEnabled_content(self, enabled: bool):
        """Set enabled state via checkbox if available."""
        if self._enable_checkbox:
            self._enable_checkbox.setChecked(enabled)
    
    def addWidget(self, widget):
        # Insert before the stretch (which is always the last item)
        self._layout.insertWidget(self._layout.count() - 1, widget)
        # Track widget for enable/disable functionality
        if self._enable_checkbox:
            self._content_widgets.append(widget)
    
    def addLayout(self, layout):
        # Insert before the stretch (which is always the last item)
        self._layout.insertLayout(self._layout.count() - 1, layout)
        # Create a container widget to track for enable/disable
        if self._enable_checkbox:
            # We need to track all widgets in the layout
            self._track_layout_widgets(layout)
    
    def _track_layout_widgets(self, layout):
        """Recursively track all widgets in a layout."""
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.widget():
                self._content_widgets.append(item.widget())
            elif item.layout():
                self._track_layout_widgets(item.layout())


class PresetListWidget(QFrame):
    """
    A widget displaying a list of presets with add/delete/duplicate buttons.
    Used in the left column of the Profiles dialog.
    """
    
    presetSelected = pyqtSignal(str)  # Emits preset_key when selection changes
    presetCreated = pyqtSignal(str)   # Emits new preset_key when created
    presetDeleted = pyqtSignal(str)   # Emits deleted preset_key
    presetDuplicated = pyqtSignal(str)  # Emits new preset_key when duplicated
    
    def __init__(self, config_loader, parent=None):
        super().__init__(parent)
        self.config_loader = config_loader
        self._setup_ui()
        self._apply_style()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING['sm'])
        
        # Header
        header = QLabel("PROFILES")
        header.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['accent']};
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 1px;
                padding: {SPACING['sm']}px;
                padding-bottom: {SPACING['xs']}px;
            }}
        """)
        layout.addWidget(header)
        
        # List widget
        self.list_widget = QListWidget()
        self.list_widget.setSpacing(1)
        self.list_widget.currentItemChanged.connect(self._on_selection_changed)
        layout.addWidget(self.list_widget, 1)
        
        # Action buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(SPACING['xs'])
        btn_row.setContentsMargins(SPACING['sm'], 0, SPACING['sm'], SPACING['sm'])
        
        self.add_btn = QPushButton()
        self.add_btn.setIcon(icon('add', 16, COLORS['text_primary']))
        self.add_btn.setToolTip("Add new profile")
        self.add_btn.setFixedSize(32, 28)
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.clicked.connect(self._on_add_clicked)
        btn_row.addWidget(self.add_btn)
        
        self.delete_btn = QPushButton()
        self.delete_btn.setIcon(icon('delete', 16, COLORS['text_primary']))
        self.delete_btn.setToolTip("Delete selected profile")
        self.delete_btn.setFixedSize(32, 28)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.clicked.connect(self._on_delete_clicked)
        btn_row.addWidget(self.delete_btn)
        
        self.duplicate_btn = QPushButton()
        self.duplicate_btn.setIcon(icon('content_copy', 16, COLORS['text_primary']))
        self.duplicate_btn.setToolTip("Duplicate selected profile")
        self.duplicate_btn.setFixedSize(32, 28)
        self.duplicate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.duplicate_btn.clicked.connect(self._on_duplicate_clicked)
        btn_row.addWidget(self.duplicate_btn)
        
        btn_row.addStretch()
        layout.addLayout(btn_row)
    
    def _apply_style(self):
        self.setStyleSheet(f"""
            PresetListWidget {{
                background-color: {COLORS['bg_elevated']};
                border: 1px solid {COLORS['border']};
                border-radius: 0;
            }}
            QListWidget {{
                background-color: transparent;
                border: none;
                outline: none;
                padding: 0 {SPACING['xs']}px;
            }}
            QListWidget::item {{
                background-color: transparent;
                color: {COLORS['text_secondary']};
                padding: 8px 12px;
                border-radius: 0;
                margin: 1px 0;
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['accent']};
                color: white;
            }}
            QListWidget::item:hover:!selected {{
                background-color: {COLORS['bg_hover']};
                color: {COLORS['text_primary']};
            }}
            QPushButton {{
                background-color: {COLORS['bg_dark']};
                border: 1px solid {COLORS['border']};
                border-radius: 0;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_hover']};
                border-color: {COLORS['text_muted']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['accent']};
                border-color: {COLORS['accent']};
            }}
        """)
    
    def load_presets(self, config: dict, current_key: str = None):
        """Load presets from config dict and select current_key if provided."""
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        
        presets = config.get('presets', {})
        # Sort by name
        sorted_items = sorted(presets.items(), key=lambda x: x[1].get('name', x[0]).lower())
        
        for preset_key, preset_data in sorted_items:
            name = preset_data.get('name', preset_key)
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, preset_key)
            self.list_widget.addItem(item)
            
            if preset_key == current_key:
                self.list_widget.setCurrentItem(item)
        
        self.list_widget.blockSignals(False)
        self._update_button_states()
    
    def get_selected_key(self) -> str:
        """Returns the preset key of the currently selected item."""
        item = self.list_widget.currentItem()
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
        return None
    
    def select_preset(self, preset_key: str):
        """Select a preset by its key."""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == preset_key:
                self.list_widget.setCurrentItem(item)
                break
    
    def update_item_name(self, preset_key: str, new_name: str):
        """Update the display name for a preset in the list."""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == preset_key:
                item.setText(new_name)
                break
    
    def _update_button_states(self):
        """Update button enabled states based on current selection."""
        has_selection = self.list_widget.currentItem() is not None
        can_delete = has_selection and self.list_widget.count() > 1
        
        self.delete_btn.setEnabled(can_delete)
        self.duplicate_btn.setEnabled(has_selection)
    
    def _on_selection_changed(self, current, previous):
        """Handle selection change in the list."""
        self._update_button_states()
        if current:
            preset_key = current.data(Qt.ItemDataRole.UserRole)
            self.presetSelected.emit(preset_key)
    
    def _on_add_clicked(self):
        """Handle add button click - create new profile."""
        name, ok = QInputDialog.getText(
            self,
            "New Profile",
            "Enter name for the new profile:",
            QLineEdit.EchoMode.Normal,
            "New Profile"
        )
        if ok and name.strip():
            self.presetCreated.emit(name.strip())
    
    def _on_delete_clicked(self):
        """Handle delete button click."""
        current = self.list_widget.currentItem()
        if not current:
            return
        
        preset_key = current.data(Qt.ItemDataRole.UserRole)
        preset_name = current.text()
        
        if self.list_widget.count() <= 1:
            QMessageBox.warning(
                self,
                "Cannot Delete",
                "You cannot delete the last remaining profile."
            )
            return
        
        reply = QMessageBox.question(
            self,
            "Delete Profile",
            f"Are you sure you want to delete '{preset_name}'?\n\n"
            "This will also delete the associated template files.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.presetDeleted.emit(preset_key)
    
    def _on_duplicate_clicked(self):
        """Handle duplicate button click."""
        current = self.list_widget.currentItem()
        if not current:
            return
        
        preset_key = current.data(Qt.ItemDataRole.UserRole)
        preset_name = current.text()
        
        new_name, ok = QInputDialog.getText(
            self,
            "Duplicate Profile",
            "Enter name for the duplicated profile:",
            QLineEdit.EchoMode.Normal,
            f"{preset_name} (Copy)"
        )
        
        if ok and new_name.strip():
            # Emit signal with the source key - parent will handle the duplication
            self.presetDuplicated.emit(new_name.strip())


class FormField(QWidget):
    """A form field with label on top and input below."""
    
    def __init__(self, label: str, widget: QWidget, hint: str = "", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Label row
        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-weight: 500;
            font-size: 12px;
        """)
        layout.addWidget(label_widget)
        
        # Input widget
        layout.addWidget(widget)
        
        # Optional hint
        if hint:
            hint_label = QLabel(hint)
            hint_label.setStyleSheet(f"""
                color: {COLORS['text_muted']};
                font-size: 11px;
            """)
            hint_label.setWordWrap(True)
            layout.addWidget(hint_label)


class FormRow(QWidget):
    """A horizontal form row with label and input widget."""
    
    def __init__(self, label: str, widget: QWidget, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING['sm'])
        
        lbl = QLabel(label)
        self.label_widget = lbl
        lbl.setFixedWidth(75)  # Reduced from 100 (25% narrower)
        lbl.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-weight: 500;
            font-size: 12px;
        """)
        layout.addWidget(lbl)
        
        layout.addWidget(widget, 1)


class StyledSpinBox(QSpinBox):
    """An improved styled spin box with better visual appearance."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(80)
        self.setMinimumHeight(24)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"""
            QSpinBox {{
                background-color: {COLORS['bg_dark']};
                border: 1px solid {COLORS['border']};
                border-radius: 0;
                color: {COLORS['text_primary']};
                padding: 2px 4px;
                font-size: 13px;
                font-weight: 500;
            }}
            QSpinBox:hover {{
                border-color: {COLORS['text_muted']};
            }}
            QSpinBox:focus {{
                border-color: {COLORS['accent']};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 18px;
                border: none;
                background-color: {COLORS['bg_hover']};
            }}
            QSpinBox::up-button {{
                border-radius: 0;
                subcontrol-position: top right;
            }}
            QSpinBox::down-button {{
                border-radius: 0;
                subcontrol-position: bottom right;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: {COLORS['accent']};
            }}
            QSpinBox::up-arrow {{
                image: none;
                border-left: 3px solid transparent;
                border-right: 3px solid transparent;
                border-bottom: 4px solid {COLORS['text_secondary']};
                width: 0; height: 0;
            }}
            QSpinBox::down-arrow {{
                image: none;
                border-left: 3px solid transparent;
                border-right: 3px solid transparent;
                border-top: 4px solid {COLORS['text_secondary']};
                width: 0; height: 0;
            }}
        """)


class StyledComboBox(QComboBox):
    """An editable combo box for font selection."""
    
    def __init__(self, items: list = None, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.setMinimumHeight(26)
        if items:
            self.addItems(items)
        self.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['bg_dark']};
                border: 1px solid {COLORS['border']};
                border-radius: 0;
                color: {COLORS['text_primary']};
                padding: 2px 6px;
                padding-right: 24px;
                font-size: 13px;
            }}
            QComboBox:hover {{
                border-color: {COLORS['text_muted']};
            }}
            QComboBox:focus {{
                border-color: {COLORS['accent']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
                subcontrol-origin: padding;
                subcontrol-position: center right;
            }}
            QComboBox::down-arrow {{
                image: none;
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {COLORS['text_secondary']};
                margin-right: 6px;
            }}
            QComboBox:hover::down-arrow {{
                border-top-color: {COLORS['text_primary']};
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['bg_elevated']};
                border: 1px solid {COLORS['border']};
                border-radius: 0;
                selection-background-color: {COLORS['bg_hover']};
                outline: none;
            }}
        """)


class MarginControl(QWidget):
    """A compact margin control with 4 values arranged visually."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QGridLayout(self)
        layout.setSpacing(SPACING['sm'])
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create spin boxes
        self.top = StyledSpinBox()
        self.right = StyledSpinBox()
        self.bottom = StyledSpinBox()
        self.left = StyledSpinBox()
        
        for spin in [self.top, self.right, self.bottom, self.left]:
            spin.setRange(0, 100)
            spin.setSuffix(" mm")
            spin.setMinimumWidth(70)  # Reduced from 90 (25% narrower)
        
        # Labels
        top_lbl = QLabel("↑ Top")
        right_lbl = QLabel("→ Right")
        bottom_lbl = QLabel("↓ Bottom")
        left_lbl = QLabel("← Left")
        
        for lbl in [top_lbl, right_lbl, bottom_lbl, left_lbl]:
            lbl.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
        
        # Arrange in 2x4 grid
        layout.addWidget(top_lbl, 0, 0)
        layout.addWidget(self.top, 0, 1)
        layout.addWidget(right_lbl, 0, 2)
        layout.addWidget(self.right, 0, 3)
        
        layout.addWidget(left_lbl, 1, 0)
        layout.addWidget(self.left, 1, 1)
        layout.addWidget(bottom_lbl, 1, 2)
        layout.addWidget(self.bottom, 1, 3)
    
    def values(self) -> list:
        return [self.top.value(), self.right.value(), self.bottom.value(), self.left.value()]
    
    def setValues(self, margins: list):
        if len(margins) >= 4:
            self.top.setValue(margins[0])
            self.right.setValue(margins[1])
            self.bottom.setValue(margins[2])
            self.left.setValue(margins[3])


class ConfigDialog(QDialog):
    """Main configuration dialog with tabbed interface."""
    
    configSaved = pyqtSignal()
    
    def __init__(self, config_loader, initial_preset_key=None, parent=None):
        super().__init__(parent)
        self.config_loader = config_loader
        # Deep copy config so we can modify freely
        self.config = copy.deepcopy(config_loader.config)
        
        # Track which preset we are currently editing
        if initial_preset_key:
            self.current_preset_key = initial_preset_key
        else:
            self.current_preset_key = self.config.get('active_preset', 'preset_1')
        
        self.setWindowTitle("Profiles")
        self.setMinimumSize(1100, 620)
        self.resize(1200, 720)
        
        self._setup_ui()
        self._load_preset_values(self.current_preset_key)
        self._apply_dialog_style()
    
    def _apply_dialog_style(self):
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_base']};
            }}
            QTabWidget::pane {{
                border: 1px solid {COLORS['border']};
                border-radius: 0;
                background-color: {COLORS['bg_dark']};
                padding: {SPACING['sm']}px;
            }}
            QTabBar::tab {{
                background-color: {COLORS['bg_elevated']};
                border: 1px solid {COLORS['border']};
                border-bottom: none;
                border-radius: 0;
                padding: {SPACING['sm']}px {SPACING['lg']}px;
                margin-right: 1px;
                color: {COLORS['text_secondary']};
                font-weight: 500;
                font-size: 13px;
                min-width: 90px;
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['bg_dark']};
                color: {COLORS['accent']};
                border-bottom: 1px solid {COLORS['bg_dark']};
                border-top: 2px solid {COLORS['accent']};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {COLORS['bg_hover']};
                color: {COLORS['text_primary']};
            }}
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollArea > QWidget > QWidget {{
                background-color: transparent;
            }}
            QCheckBox {{
                color: {COLORS['text_primary']};
                font-size: 13px;
                spacing: 4px;
            }}
            QCheckBox::indicator {{
                width: 14px;
                height: 14px;
                border: 1px solid {COLORS['border']};
                border-radius: 0;
                background-color: {COLORS['bg_dark']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS['accent']};
                border-color: {COLORS['accent']};
            }}
            QCheckBox::indicator:hover {{
                border-color: {COLORS['accent']};
            }}
            /* Preset Buttons (Checkable) */
            QPushButton[checkable="true"] {{
                background-color: {COLORS['bg_elevated']};
                border: 1px solid {COLORS['border']};
                color: {COLORS['text_secondary']};
                padding: 0 8px;
                border-radius: 0;
                font-weight: 500;
                font-size: 12px;
            }}
            QPushButton[checkable="true"]:checked {{
                background-color: {COLORS['accent']};
                color: white;
                border: 1px solid {COLORS['accent']};
            }}
            QPushButton[checkable="true"]:hover:!checked {{
                background-color: {COLORS['bg_hover']};
                color: {COLORS['text_primary']};
            }}
        """)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(SPACING['md'])
        layout.setContentsMargins(SPACING['lg'], SPACING['lg'], SPACING['lg'], SPACING['lg'])
        
        # Title
        title_container = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        
        title = QLabel("Profiles")
        title.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 600;
            color: {COLORS['text_primary']};
        """)
        title_col.addWidget(title)
        
        subtitle = QLabel("Manage your sender profiles and document settings")
        subtitle.setStyleSheet(f"""
            color: {COLORS['text_muted']};
            font-size: 13px;
        """)
        title_col.addWidget(subtitle)
        
        title_container.addLayout(title_col)
        title_container.addStretch()
        layout.addLayout(title_container)
        
        # Main content: two-column layout
        main_content = QHBoxLayout()
        main_content.setSpacing(SPACING['md'])
        
        # Left column: Preset list (240px fixed width)
        self.preset_list = PresetListWidget(self.config_loader)
        self.preset_list.setFixedWidth(240)
        self.preset_list.load_presets(self.config, self.current_preset_key)
        self.preset_list.presetSelected.connect(self._on_preset_selected)
        self.preset_list.presetCreated.connect(self._on_preset_created)
        self.preset_list.presetDeleted.connect(self._on_preset_deleted)
        self.preset_list.presetDuplicated.connect(self._on_preset_duplicated)
        main_content.addWidget(self.preset_list)
        
        # Right column: Settings panel
        right_column = QVBoxLayout()
        right_column.setSpacing(SPACING['sm'])
        
        # Preset name row at top of right column
        name_row = QHBoxLayout()
        name_row.setSpacing(SPACING['sm'])
        
        name_label = QLabel("Profile Name:")
        name_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: 500; font-size: 12px;")
        name_row.addWidget(name_label)
        
        self.preset_name_edit = QLineEdit()
        self.preset_name_edit.setPlaceholderText("e.g. Company A, Freelance, Private")
        self.preset_name_edit.setMinimumHeight(28)
        self.preset_name_edit.textChanged.connect(self._on_preset_name_changed)
        name_row.addWidget(self.preset_name_edit, 1)
        
        right_column.addLayout(name_row)
        
        # Tab widget
        self.tabs = QTabWidget()
        right_column.addWidget(self.tabs, 1)
        
        # Create tabs with Material icons (preset-specific settings)
        self.tabs.addTab(self._create_identity_tab(), icon('badge', 18, COLORS['text_secondary']), "Identity")
        self.tabs.addTab(self._create_document_tab(), icon('article', 18, COLORS['text_secondary']), "Document")
        self.tabs.addTab(self._create_styling_tab(), icon('palette', 18, COLORS['text_secondary']), "Styling")
        self.tabs.addTab(self._create_defaults_tab(), icon('tune', 18, COLORS['text_secondary']), "Defaults")
        
        main_content.addLayout(right_column, 1)
        layout.addLayout(main_content, 1)
        
        # Bottom buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(SPACING['sm'])
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumWidth(70)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save Configuration")
        save_btn.setMinimumWidth(120)
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._save_config)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def _create_scrollable_tab(self) -> tuple[QScrollArea, QVBoxLayout]:
        """Creates a scrollable container for tab content."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(SPACING['sm'])
        content_layout.setContentsMargins(SPACING['xs'], SPACING['xs'], SPACING['xs'], SPACING['xs'])
        
        scroll.setWidget(content)
        return scroll, content_layout
    
    def _create_identity_tab(self) -> QWidget:
        """Combined tab for Company, Contact, and Legal/Bank info."""
        scroll, layout = self._create_scrollable_tab()
        
        # Two-column layout for this tab
        columns = QHBoxLayout()
        columns.setSpacing(SPACING['sm'])
        
        # Left column
        left_col = QVBoxLayout()
        left_col.setSpacing(SPACING['sm'])
        
        # Company Card
        company_card = SectionCard("Company")
        
        # Name with checkbox
        name_container = QWidget()
        name_layout = QHBoxLayout(name_container)
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_layout.setSpacing(SPACING['sm'])
        
        self.company_name = QLineEdit()
        self.company_name.setPlaceholderText("Your Company Name")
        self.company_name.setMinimumHeight(24)
        name_layout.addWidget(self.company_name, 1)
        
        self.company_show_name = QCheckBox("Show")
        self.company_show_name.setToolTip("Show company name in PDF")
        name_layout.addWidget(self.company_show_name)
        
        company_card.addWidget(FormRow("Name", name_container))
        
        # Tagline with checkbox
        tagline_container = QWidget()
        tagline_layout = QHBoxLayout(tagline_container)
        tagline_layout.setContentsMargins(0, 0, 0, 0)
        tagline_layout.setSpacing(SPACING['sm'])
        
        self.company_tagline = QLineEdit()
        self.company_tagline.setPlaceholderText("Your tagline or slogan")
        self.company_tagline.setMinimumHeight(24)
        tagline_layout.addWidget(self.company_tagline, 1)
        
        self.company_show_tagline = QCheckBox("Show")
        self.company_show_tagline.setToolTip("Show tagline in PDF")
        tagline_layout.addWidget(self.company_show_tagline)
        
        company_card.addWidget(FormRow("Tagline", tagline_container))
        
        # Logo with checkbox
        logo_container = QWidget()
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(SPACING['sm'])
        
        self.company_logo = PathSelector("Images (*.svg *.png *.jpg *.jpeg)")
        logo_layout.addWidget(self.company_logo, 1)
        
        self.company_show_logo = QCheckBox("Show")
        self.company_show_logo.setToolTip("Show logo in PDF")
        logo_layout.addWidget(self.company_show_logo)
        
        company_card.addWidget(FormRow("Logo", logo_container))
        
        # Logo preview with label
        logo_preview_row = QHBoxLayout()
        logo_preview_row.setSpacing(SPACING['sm'])
        
        # Empty label to align with form row
        logo_spacer = QLabel("")
        logo_spacer.setFixedWidth(75)  # Reduced to match FormRow label width
        logo_preview_row.addWidget(logo_spacer)
        
        self.logo_preview = LogoPreview()
        logo_preview_row.addWidget(self.logo_preview)
        logo_preview_row.addStretch()
        
        company_card.addLayout(logo_preview_row)
        
        # Connect path changes to update preview
        self.company_logo.pathChanged.connect(self.logo_preview.setPath)
        
        left_col.addWidget(company_card)
        
        # Contact Card (with enable checkbox)
        contact_card = SectionCard("Contact Details", with_enable_checkbox=True)
        self.contact_enabled_checkbox = contact_card.enableCheckbox()
        
        self.contact_street = QLineEdit()
        self.contact_street.setPlaceholderText("Street Address")
        self.contact_street.setMinimumHeight(24)
        contact_card.addWidget(FormRow("Street", self.contact_street))
        
        # City + Postal in one row
        city_row = QHBoxLayout()
        city_row.setSpacing(SPACING['sm'])
        
        self.contact_postal = QLineEdit()
        self.contact_postal.setPlaceholderText("Postal Code")
        self.contact_postal.setMinimumHeight(24)
        self.contact_postal.setMaximumWidth(80)  # Reduced from 100
        city_row.addWidget(self.contact_postal)
        
        self.contact_city = QLineEdit()
        self.contact_city.setPlaceholderText("City")
        self.contact_city.setMinimumHeight(24)
        city_row.addWidget(self.contact_city, 1)
        
        contact_card.addWidget(FormRow("Location", QWidget()))
        contact_card.addLayout(city_row)
        
        self.contact_country = QLineEdit()
        self.contact_country.setPlaceholderText("Country")
        self.contact_country.setMinimumHeight(24)
        contact_card.addWidget(FormRow("Country", self.contact_country))
        
        self.contact_phone = QLineEdit()
        self.contact_phone.setPlaceholderText("+31 6 1234 5678")
        self.contact_phone.setMinimumHeight(24)
        contact_card.addWidget(FormRow("Phone", self.contact_phone))
        
        self.contact_email = QLineEdit()
        self.contact_email.setPlaceholderText("hello@example.com")
        self.contact_email.setMinimumHeight(24)
        contact_card.addWidget(FormRow("Email", self.contact_email))
        
        self.contact_website = QLineEdit()
        self.contact_website.setPlaceholderText("www.example.com")
        self.contact_website.setMinimumHeight(24)
        contact_card.addWidget(FormRow("Website", self.contact_website))
        
        left_col.addWidget(contact_card)
        
        columns.addLayout(left_col, 1)
        
        # Right column
        right_col = QVBoxLayout()
        right_col.setSpacing(SPACING['sm'])
        
        # Legal Card (with enable checkbox)
        legal_card = SectionCard("Legal Information", with_enable_checkbox=True)
        self.legal_enabled_checkbox = legal_card.enableCheckbox()
        
        self.legal_tax_id = QLineEdit()
        self.legal_tax_id.setPlaceholderText("VAT / Tax ID")
        self.legal_tax_id.setMinimumHeight(24)
        legal_card.addWidget(FormRow("Tax ID", self.legal_tax_id))
        
        right_col.addWidget(legal_card)
        
        # Bank Card (with enable checkbox)
        bank_card = SectionCard("Banking Details", with_enable_checkbox=True)
        self.bank_enabled_checkbox = bank_card.enableCheckbox()
        
        self.bank_holder = QLineEdit()
        self.bank_holder.setPlaceholderText("Account Holder Name")
        self.bank_holder.setMinimumHeight(24)
        bank_card.addWidget(FormRow("Holder", self.bank_holder))
        
        self.bank_name = QLineEdit()
        self.bank_name.setPlaceholderText("Bank Name")
        self.bank_name.setMinimumHeight(24)
        bank_card.addWidget(FormRow("Bank", self.bank_name))
        
        self.bank_iban = QLineEdit()
        self.bank_iban.setPlaceholderText("NL91 ABNA 0417 1643 00")
        self.bank_iban.setMinimumHeight(24)
        bank_card.addWidget(FormRow("IBAN", self.bank_iban))
        
        self.bank_bic = QLineEdit()
        self.bank_bic.setPlaceholderText("ABNANL2A")
        self.bank_bic.setMinimumHeight(24)
        bank_card.addWidget(FormRow("BIC / SWIFT", self.bank_bic))
        
        right_col.addWidget(bank_card)
        
        # Add spacer to right column to align with left column height
        right_col.addStretch(1)
        
        columns.addLayout(right_col, 1)
        
        layout.addLayout(columns, 1)
        return scroll
    
    def _create_document_tab(self) -> QWidget:
        """Tab for Layout, Margins, and Content Snippets."""
        scroll, layout = self._create_scrollable_tab()
        
        # Page Margins Card
        margins_card = SectionCard("Page Margins")
        
        self.margin_control = MarginControl()
        margins_card.addWidget(self.margin_control)
        
        layout.addWidget(margins_card)
        
        # Advanced Card (Template Editing)
        advanced_card = SectionCard("Advanced")

        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(SPACING['sm'])

        edit_html_btn = QPushButton("Edit Template HTML")
        edit_html_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_html_btn.clicked.connect(self._edit_template)

        edit_css_btn = QPushButton("Edit Template CSS")
        edit_css_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_css_btn.clicked.connect(self._edit_css)

        # Place buttons on the same row, each taking 50% width
        buttons_row.addWidget(edit_html_btn, 1)
        buttons_row.addWidget(edit_css_btn, 1)

        advanced_card.addLayout(buttons_row)
        layout.addWidget(advanced_card)
        
        # Snippets Card (with enable checkbox)
        snippets_card = SectionCard("Content Snippets", with_enable_checkbox=True)
        self.snippets_enabled_checkbox = snippets_card.enableCheckbox()
        
        intro_label = QLabel("Intro Text")
        intro_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: 500; font-size: 12px;")
        snippets_card.addWidget(intro_label)
        
        self.snippet_intro = QPlainTextEdit()
        self.snippet_intro.setPlaceholderText("Introductory text before the line items...")
        self.snippet_intro.setFixedHeight(60)
        snippets_card.addWidget(self.snippet_intro)
        
        terms_label = QLabel("Terms & Conditions")
        terms_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: 500; font-size: 12px;")
        snippets_card.addWidget(terms_label)
        
        self.snippet_terms = QPlainTextEdit()
        self.snippet_terms.setPlaceholderText("Payment terms, conditions, validity...")
        self.snippet_terms.setFixedHeight(60)
        snippets_card.addWidget(self.snippet_terms)
        
        self.snippet_footer = QLineEdit()
        self.snippet_footer.setPlaceholderText("Extra text for page footer (e.g. page number override)")
        self.snippet_footer.setMinimumHeight(24)
        snippets_card.addWidget(FormRow("Custom Footer", self.snippet_footer))
        
        self.snippet_signature = QCheckBox("Show Signature Block")
        snippets_card.addWidget(self.snippet_signature)
        
        layout.addWidget(snippets_card)
        
        layout.addStretch(1)
        return scroll
    
    def _create_styling_tab(self) -> QWidget:
        """Combined tab for Typography and Colors."""
        scroll, layout = self._create_scrollable_tab()
        
        # Two-column layout
        columns = QHBoxLayout()
        columns.setSpacing(SPACING['sm'])
        
        # Left column - Typography
        left_col = QVBoxLayout()
        left_col.setSpacing(SPACING['sm'])
        
        # Font Families Card
        fonts_card = SectionCard("Font Families")
        
        self.typo_heading = StyledComboBox(FONT_FAMILIES['heading'])
        fonts_card.addWidget(FormRow("Headings", self.typo_heading))
        
        self.typo_body = StyledComboBox(FONT_FAMILIES['body'])
        fonts_card.addWidget(FormRow("Body Text", self.typo_body))
        
        self.typo_mono = StyledComboBox(FONT_FAMILIES['mono'])
        fonts_card.addWidget(FormRow("Monospace", self.typo_mono))
        
        left_col.addWidget(fonts_card)
        
        # Font Sizes Card
        sizes_card = SectionCard("Font Sizes (px)")
        
        sizes_grid = QGridLayout()
        sizes_grid.setSpacing(SPACING['sm'])
        
        self.typo_size_company = StyledSpinBox()
        self.typo_size_company.setRange(8, 72)
        sizes_grid.addWidget(QLabel("Company Name"), 0, 0)
        sizes_grid.addWidget(self.typo_size_company, 0, 1)
        
        self.typo_size_h1 = StyledSpinBox()
        self.typo_size_h1.setRange(8, 72)
        sizes_grid.addWidget(QLabel("Heading 1"), 0, 2)
        sizes_grid.addWidget(self.typo_size_h1, 0, 3)
        
        self.typo_size_h2 = StyledSpinBox()
        self.typo_size_h2.setRange(8, 72)
        sizes_grid.addWidget(QLabel("Heading 2"), 1, 0)
        sizes_grid.addWidget(self.typo_size_h2, 1, 1)
        
        self.typo_size_body = StyledSpinBox()
        self.typo_size_body.setRange(8, 72)
        sizes_grid.addWidget(QLabel("Body"), 1, 2)
        sizes_grid.addWidget(self.typo_size_body, 1, 3)
        
        self.typo_size_small = StyledSpinBox()
        self.typo_size_small.setRange(6, 72)
        sizes_grid.addWidget(QLabel("Small Text"), 2, 0)
        sizes_grid.addWidget(self.typo_size_small, 2, 1)
        
        # Style labels
        for i in range(sizes_grid.count()):
            widget = sizes_grid.itemAt(i).widget()
            if isinstance(widget, QLabel):
                widget.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        
        sizes_card.addLayout(sizes_grid)
        left_col.addWidget(sizes_card)
        
        columns.addLayout(left_col, 1)
        
        # Right column - Colors
        right_col = QVBoxLayout()
        right_col.setSpacing(SPACING['sm'])
        
        colors_card = SectionCard("Document Colors")
        
        hint = QLabel("These colors are used in the PDF output, not the application UI.")
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 10px; margin-bottom: {SPACING['xs']}px;")
        colors_card.addWidget(hint)
        
        # Colors grid - 2 columns
        colors_grid = QGridLayout()
        colors_grid.setSpacing(SPACING['sm'])
        colors_grid.setColumnStretch(1, 1)
        colors_grid.setColumnStretch(3, 1)
        
        self.color_primary = ColorButton()
        colors_grid.addWidget(QLabel("Primary"), 0, 0)
        colors_grid.addWidget(self.color_primary, 0, 1)
        
        self.color_accent = ColorButton()
        colors_grid.addWidget(QLabel("Accent"), 0, 2)
        colors_grid.addWidget(self.color_accent, 0, 3)
        
        self.color_text = ColorButton()
        colors_grid.addWidget(QLabel("Text"), 1, 0)
        colors_grid.addWidget(self.color_text, 1, 1)
        
        self.color_muted = ColorButton()
        colors_grid.addWidget(QLabel("Muted"), 1, 2)
        colors_grid.addWidget(self.color_muted, 1, 3)
        
        self.color_background = ColorButton()
        colors_grid.addWidget(QLabel("Background"), 2, 0)
        colors_grid.addWidget(self.color_background, 2, 1)
        
        self.color_border = ColorButton()
        colors_grid.addWidget(QLabel("Borders"), 2, 2)
        colors_grid.addWidget(self.color_border, 2, 3)
        
        self.color_table_alt = ColorButton()
        colors_grid.addWidget(QLabel("Table Alt"), 3, 0)
        colors_grid.addWidget(self.color_table_alt, 3, 1)
        
        # Style color labels
        for i in range(colors_grid.count()):
            widget = colors_grid.itemAt(i).widget()
            if isinstance(widget, QLabel):
                widget.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
                widget.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        colors_card.addLayout(colors_grid)
        right_col.addWidget(colors_card)
        
        columns.addLayout(right_col, 1)
        
        layout.addLayout(columns, 1)
        return scroll
    
    def _create_defaults_tab(self) -> QWidget:
        """Tab for Default Values and Quotation Numbering."""
        scroll, layout = self._create_scrollable_tab()
        
        # Two-column layout
        columns = QHBoxLayout()
        columns.setSpacing(SPACING['sm'])
        
        # Left column - Defaults
        left_col = QVBoxLayout()
        left_col.setSpacing(SPACING['sm'])
        
        defaults_card = SectionCard("Default Values")
        
        # Currency + Language row
        row1 = QHBoxLayout()
        row1.setSpacing(SPACING['md'])
        
        currency_col = QVBoxLayout()
        currency_col.setSpacing(2)
        currency_label = QLabel("Currency")
        currency_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: 500; font-size: 12px;")
        currency_col.addWidget(currency_label)
        self.defaults_currency = QComboBox()
        self.defaults_currency.addItems(["EUR", "USD", "GBP", "CHF", "JPY", "CAD", "AUD"])
        self.defaults_currency.setEditable(True)  # Allow custom currencies
        self.defaults_currency.setMinimumHeight(26)
        self.defaults_currency.setMinimumWidth(70)  # Reduced from 90
        currency_col.addWidget(self.defaults_currency)
        row1.addLayout(currency_col)
        
        lang_col = QVBoxLayout()
        lang_col.setSpacing(2)
        lang_label = QLabel("Language")
        lang_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: 500; font-size: 12px;")
        lang_col.addWidget(lang_label)
        self.defaults_language = QComboBox()
        self.defaults_language.addItems(["de", "en"])
        self.defaults_language.setMinimumHeight(24)
        self.defaults_language.setMinimumWidth(60)  # Reduced from 80
        lang_col.addWidget(self.defaults_language)
        row1.addLayout(lang_col)
        
        row1.addStretch()
        defaults_card.addLayout(row1)
        
        # VAT Type row
        row2 = QHBoxLayout()
        row2.setSpacing(SPACING['md'])
        
        vat_type_col = QVBoxLayout()
        vat_type_col.setSpacing(2)
        vat_type_label = QLabel("VAT / Steuer Type")
        vat_type_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: 500; font-size: 12px;")
        vat_type_col.addWidget(vat_type_label)
        self.defaults_vat_type = QComboBox()
        self.defaults_vat_type.addItem("No VAT / Keine Steuer", "none")
        self.defaults_vat_type.addItem("Kleinunternehmer (§19 UStG)", "kleinunternehmer")
        self.defaults_vat_type.addItem("German VAT / Deutsche USt", "german_vat")
        self.defaults_vat_type.setMinimumHeight(24)
        self.defaults_vat_type.setMinimumWidth(150)  # Reduced from 200
        self.defaults_vat_type.currentIndexChanged.connect(self._on_vat_type_changed)
        vat_type_col.addWidget(self.defaults_vat_type)
        row2.addLayout(vat_type_col)
        
        row2.addStretch()
        defaults_card.addLayout(row2)
        
        # Tax Rate + Payment row
        row3 = QHBoxLayout()
        row3.setSpacing(SPACING['md'])
        
        tax_col = QVBoxLayout()
        tax_col.setSpacing(2)
        self.tax_rate_label = QLabel("Tax Rate")
        self.tax_rate_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: 500; font-size: 12px;")
        tax_col.addWidget(self.tax_rate_label)
        self.defaults_tax_rate = StyledSpinBox()
        self.defaults_tax_rate.setRange(0, 100)
        self.defaults_tax_rate.setSuffix(" %")
        self.defaults_tax_rate.setMinimumWidth(60)  # Reduced from 80
        tax_col.addWidget(self.defaults_tax_rate)
        row3.addLayout(tax_col)
        
        payment_col = QVBoxLayout()
        payment_col.setSpacing(2)
        payment_label = QLabel("Payment Terms")
        payment_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: 500; font-size: 12px;")
        payment_col.addWidget(payment_label)
        self.defaults_payment_days = StyledSpinBox()
        self.defaults_payment_days.setRange(1, 365)
        self.defaults_payment_days.setSuffix(" days")
        self.defaults_payment_days.setMinimumWidth(75)  # Reduced from 100
        payment_col.addWidget(self.defaults_payment_days)
        row3.addLayout(payment_col)
        
        row3.addStretch()
        defaults_card.addLayout(row3)
        
        # VAT Type info hint
        self.vat_hint_label = QLabel()
        self.vat_hint_label.setWordWrap(True)
        self.vat_hint_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px; padding: 4px 0;")
        defaults_card.addWidget(self.vat_hint_label)
        self._update_vat_hint()
        
        left_col.addWidget(defaults_card)
        
        columns.addLayout(left_col, 1)
        
        # Right column - Quotation Number (with enable checkbox)
        right_col = QVBoxLayout()
        right_col.setSpacing(SPACING['sm'])
        
        qn_card = SectionCard("Quotation Numbering", with_enable_checkbox=True)
        self.qn_enabled = qn_card.enableCheckbox()
        
        hint = QLabel(
            "Use placeholders:\n"
            "• {YYYY} = Full year (2025)  • {YY} = Short year (25)\n"
            "• {MM} = Month (01-12)  • {DD} = Day (01-31)\n"
            "• {N}/{NN}/{NNN}/{NNNN} = Counter with padding\n"
            "• {PREFIX} = Company abbreviation"
        )
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 10px; line-height: 1.3;")
        qn_card.addWidget(hint)
        
        # Format presets
        preset_label = QLabel("Format Presets")
        preset_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: 500; font-size: 12px;")
        qn_card.addWidget(preset_label)
        
        self.qn_format_presets = QComboBox()
        self.qn_format_presets.setMinimumHeight(24)
        self.qn_format_presets.addItem("Custom", "")
        self.qn_format_presets.addItem("Year-Number: 2025-001", "{YYYY}-{NNN}")
        self.qn_format_presets.addItem("Invoice Style: INV-2025-0001", "INV-{YYYY}-{NNNN}")
        self.qn_format_presets.addItem("Monthly Reset: 2025-01-001", "{YYYY}-{MM}-{NNN}")
        self.qn_format_presets.addItem("Compact: Q25-001", "Q{YY}-{NNN}")
        self.qn_format_presets.addItem("With Prefix: JDC-2025-01", "{PREFIX}-{YYYY}-{NN}")
        self.qn_format_presets.currentIndexChanged.connect(self._on_qn_preset_selected)
        qn_card.addWidget(self.qn_format_presets)
        
        # Custom format input
        format_label = QLabel("Custom Format")
        format_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: 500; font-size: 12px;")
        qn_card.addWidget(format_label)
        
        self.qn_format = QLineEdit()
        self.qn_format.setPlaceholderText("{YYYY}-{NNN}")
        self.qn_format.setMinimumHeight(24)
        qn_card.addWidget(self.qn_format)
        
        # Counter display and reset
        counter_row = QHBoxLayout()
        counter_row.setSpacing(SPACING['sm'])
        
        self.qn_counter_label = QLabel("Counter: 0")
        self.qn_counter_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px;")
        counter_row.addWidget(self.qn_counter_label)
        
        counter_row.addStretch()
        
        reset_counter_btn = QPushButton("Reset Counter")
        reset_counter_btn.setMinimumWidth(70)  # Reduced from 90
        reset_counter_btn.clicked.connect(self._reset_qn_counter)
        counter_row.addWidget(reset_counter_btn)
        
        qn_card.addLayout(counter_row)
        
        right_col.addWidget(qn_card)
        
        columns.addLayout(right_col, 1)
        
        layout.addLayout(columns, 1)
        return scroll
    
    def _on_vat_type_changed(self, index):
        """Handle VAT type selection changes."""
        vat_type = self.defaults_vat_type.currentData()
        # Enable/disable tax rate based on VAT type
        tax_enabled = (vat_type == 'german_vat')
        self.defaults_tax_rate.setEnabled(tax_enabled)
        self.tax_rate_label.setEnabled(tax_enabled)
        self._update_vat_hint()
    
    def _update_vat_hint(self):
        """Update the VAT hint label based on current selection."""
        vat_type = self.defaults_vat_type.currentData()
        hints = {
            'none': 'No VAT will be shown on the quotation.',
            'kleinunternehmer': 'Quotation will include: "Kein Ausweis von Umsatzsteuer, da Kleinunternehmer gemäß §19 UStG."',
            'german_vat': f'VAT at {self.defaults_tax_rate.value()}% will be shown on the quotation.'
        }
        self.vat_hint_label.setText(hints.get(vat_type, ''))
    
    def _on_qn_preset_selected(self, index):
        """Apply selected format preset to the format field."""
        format_value = self.qn_format_presets.currentData()
        if format_value:
            self.qn_format.setText(format_value)
    
    def _reset_qn_counter(self):
        """Reset the counter for the current preset to 0."""
        reply = QMessageBox.question(
            self,
            "Reset Counter",
            "Are you sure you want to reset the quotation counter to 0?\n"
            "The next quotation will start from 1.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            # Reset in memory
            presets = self.config.setdefault('presets', {})
            preset = presets.setdefault(self.current_preset_key, {})
            qn = preset.setdefault('quotation_number', {})
            qn['counter'] = 0
            qn['last_reset_year'] = None
            qn['last_reset_month'] = None
            
            self.qn_counter_label.setText("Counter: 0")
            QMessageBox.information(self, "Counter Reset", "Quotation counter has been reset to 0.")

    def _preset_display_name(self, preset_key: str) -> str:
        """Return stored preset name or the key as fallback."""
        presets = self.config.get('presets', {})
        preset = presets.get(preset_key, {})
        name = preset.get('name')
        return name if name else preset_key

    # -------------------------------------------------------------------------
    # Preset List Event Handlers
    # -------------------------------------------------------------------------

    def _on_preset_selected(self, preset_key: str):
        """Handle preset selection from the list widget."""
        if preset_key == self.current_preset_key:
            return
        
        # Save current values to memory
        self._save_current_preset_to_memory()
        
        # Update current key
        self.current_preset_key = preset_key
        
        # Load new values
        self._load_preset_values(preset_key)

    def _on_preset_name_changed(self, text: str):
        """Handle preset name change from the name input field."""
        # Update in memory config
        if 'presets' not in self.config:
            self.config['presets'] = {}
        if self.current_preset_key not in self.config['presets']:
            self.config['presets'][self.current_preset_key] = {}
            
        self.config['presets'][self.current_preset_key]['name'] = text
        
        # Update the list widget
        self.preset_list.update_item_name(self.current_preset_key, text)

    def _on_preset_created(self, name: str):
        """Handle new preset creation from the list widget."""
        # Save current preset first
        self._save_current_preset_to_memory()
        
        # Create new preset using config_loader
        new_key, error = self.config_loader.create_preset(name, self.current_preset_key)
        
        if error:
            QMessageBox.warning(self, "Error", f"Could not create profile:\n{error}")
            return
        
        # Copy the new preset data to our working config
        self.config['presets'][new_key] = copy.deepcopy(
            self.config_loader.config['presets'][new_key]
        )
        
        # Switch to the new preset
        self.current_preset_key = new_key
        self.config['active_preset'] = new_key
        
        # Reload the list and select the new preset
        self.preset_list.load_presets(self.config, new_key)
        self._load_preset_values(new_key)

    def _on_preset_deleted(self, preset_key: str):
        """Handle preset deletion from the list widget."""
        # Save current state first
        self._save_current_preset_to_memory()
        
        # Delete from our working config
        if preset_key in self.config.get('presets', {}):
            del self.config['presets'][preset_key]
        
        # Delete template files via config_loader
        self.config_loader._delete_template_files(preset_key)
        
        # If we deleted the current preset, switch to another one
        if self.current_preset_key == preset_key:
            remaining_keys = list(self.config.get('presets', {}).keys())
            if remaining_keys:
                self.current_preset_key = remaining_keys[0]
                self.config['active_preset'] = self.current_preset_key
        
        # Reload the list
        self.preset_list.load_presets(self.config, self.current_preset_key)
        self._load_preset_values(self.current_preset_key)

    def _on_preset_duplicated(self, new_name: str):
        """Handle preset duplication from the list widget."""
        # This is essentially the same as creating a new preset from the current one
        self._on_preset_created(new_name)
            
    def _save_current_preset_to_memory(self):
        """Saves values from UI fields into self.config for the current preset."""
        presets = self.config.setdefault('presets', {})
        preset = presets.setdefault(self.current_preset_key, {})
        
        preset['name'] = self.preset_name_edit.text()
        
        preset['company'] = {
            'name': self.company_name.text(),
            'tagline': self.company_tagline.text(),
            'logo': self.company_logo.path(),
            'show_name': self.company_show_name.isChecked(),
            'show_tagline': self.company_show_tagline.isChecked(),
            'show_logo': self.company_show_logo.isChecked(),
        }
        
        preset['contact'] = {
            'enabled': self.contact_enabled_checkbox.isChecked(),
            'street': self.contact_street.text(),
            'city': self.contact_city.text(),
            'postal_code': self.contact_postal.text(),
            'country': self.contact_country.text(),
            'phone': self.contact_phone.text(),
            'email': self.contact_email.text(),
            'website': self.contact_website.text(),
        }
        
        preset['legal'] = {
            'enabled': self.legal_enabled_checkbox.isChecked(),
            'tax_id': self.legal_tax_id.text(),
        }
        
        # Template name matches preset key directly
        preset['layout'] = {
            'template': self.current_preset_key,
            'page_margins': self.margin_control.values()
        }
        
        preset['snippets'] = {
            'enabled': self.snippets_enabled_checkbox.isChecked(),
            'intro_text': self.snippet_intro.toPlainText(),
            'terms': self.snippet_terms.toPlainText(),
            'custom_footer': self.snippet_footer.text(),
            'signature_block': self.snippet_signature.isChecked()
        }

        preset['bank'] = {
            'enabled': self.bank_enabled_checkbox.isChecked(),
            'holder': self.bank_holder.text(),
            'iban': self.bank_iban.text(),
            'bic': self.bank_bic.text(),
            'bank_name': self.bank_name.text(),
        }
        
        preset['defaults'] = {
            'currency': self.defaults_currency.currentText(),
            'vat_type': self.defaults_vat_type.currentData() or 'german_vat',
            'tax_rate': self.defaults_tax_rate.value(),
            'payment_days': self.defaults_payment_days.value(),
            'language': self.defaults_language.currentText(),
        }
        
        # Preserve existing counter values when saving
        existing_qn = preset.get('quotation_number', {})
        preset['quotation_number'] = {
            'enabled': self.qn_enabled.isChecked(),
            'format': self.qn_format.text() or '{YYYY}-{NNN}',
            'counter': existing_qn.get('counter', 0),
            'last_reset_year': existing_qn.get('last_reset_year'),
            'last_reset_month': existing_qn.get('last_reset_month'),
        }
        
        preset['typography'] = {
            'heading': self.typo_heading.currentText(),
            'body': self.typo_body.currentText(),
            'mono': self.typo_mono.currentText(),
            'sizes': {
                'company_name': self.typo_size_company.value(),
                'heading1': self.typo_size_h1.value(),
                'heading2': self.typo_size_h2.value(),
                'body': self.typo_size_body.value(),
                'small': self.typo_size_small.value(),
            }
        }
        
        preset['colors'] = {
            'primary': self.color_primary.color(),
            'accent': self.color_accent.color(),
            'background': self.color_background.color(),
            'text': self.color_text.color(),
            'muted': self.color_muted.color(),
            'border': self.color_border.color(),
            'table_alt': self.color_table_alt.color(),
        }
        
    def _load_preset_values(self, preset_key: str):
        """Load configuration values for the given preset into the UI."""
        presets = self.config.get('presets', {})
        preset = presets.get(preset_key, {})
        display_name = self._preset_display_name(preset_key)
        
        # Name
        self.preset_name_edit.blockSignals(True)
        self.preset_name_edit.setText(display_name)
        self.preset_name_edit.blockSignals(False)
        
        # Company
        company = preset.get('company', {})
        self.company_name.setText(company.get('name', ''))
        self.company_tagline.setText(company.get('tagline', ''))
        logo_path = company.get('logo', '')
        self.company_logo.setPath(logo_path)
        self.logo_preview.setPath(logo_path)
        
        self.company_show_name.setChecked(company.get('show_name', True))
        self.company_show_tagline.setChecked(company.get('show_tagline', True))
        self.company_show_logo.setChecked(company.get('show_logo', True))
        
        # Contact
        contact = preset.get('contact', {})
        self.contact_enabled_checkbox.setChecked(contact.get('enabled', True))
        self.contact_street.setText(contact.get('street', ''))
        self.contact_city.setText(contact.get('city', ''))
        self.contact_postal.setText(contact.get('postal_code', ''))
        self.contact_country.setText(contact.get('country', ''))
        self.contact_phone.setText(contact.get('phone', ''))
        self.contact_email.setText(contact.get('email', ''))
        self.contact_website.setText(contact.get('website', ''))
        
        # Legal
        legal = preset.get('legal', {})
        self.legal_enabled_checkbox.setChecked(legal.get('enabled', True))
        self.legal_tax_id.setText(legal.get('tax_id', ''))
        
        layout_config = preset.get('layout', {})
        margins = layout_config.get('page_margins', [20, 20, 20, 20])
        self.margin_control.setValues(margins)
            
        # Snippets
        snippets = preset.get('snippets', {})
        self.snippets_enabled_checkbox.setChecked(snippets.get('enabled', True))
        self.snippet_intro.setPlainText(snippets.get('intro_text', ''))
        self.snippet_terms.setPlainText(snippets.get('terms', ''))
        self.snippet_footer.setText(snippets.get('custom_footer', ''))
        self.snippet_signature.setChecked(snippets.get('signature_block', True))
        
        # Bank
        bank = preset.get('bank', {})
        self.bank_enabled_checkbox.setChecked(bank.get('enabled', True))
        self.bank_holder.setText(bank.get('holder', ''))
        self.bank_iban.setText(bank.get('iban', ''))
        self.bank_bic.setText(bank.get('bic', ''))
        self.bank_name.setText(bank.get('bank_name', ''))
        
        # Defaults
        defaults = preset.get('defaults', {})
        currency = defaults.get('currency', 'EUR')
        idx = self.defaults_currency.findText(currency)
        if idx >= 0:
            self.defaults_currency.setCurrentIndex(idx)
        else:
            self.defaults_currency.setCurrentText(currency)
        
        # VAT Type
        vat_type = defaults.get('vat_type', 'german_vat')
        vat_idx = self.defaults_vat_type.findData(vat_type)
        if vat_idx >= 0:
            self.defaults_vat_type.setCurrentIndex(vat_idx)
        else:
            # Default to german_vat if unknown value
            self.defaults_vat_type.setCurrentIndex(2)
        
        self.defaults_tax_rate.setValue(defaults.get('tax_rate', 19))
        self.defaults_payment_days.setValue(defaults.get('payment_days', 14))
        lang = defaults.get('language', 'de')
        idx = self.defaults_language.findText(lang)
        if idx >= 0:
            self.defaults_language.setCurrentIndex(idx)
        
        # Update VAT controls state based on loaded type
        self._on_vat_type_changed(0)
        
        # Quotation Number
        qn = preset.get('quotation_number', {})
        self.qn_enabled.setChecked(qn.get('enabled', True))
        self.qn_format.setText(qn.get('format', '{YYYY}-{NNN}'))
        
        # Update counter label
        counter = qn.get('counter', 0)
        self.qn_counter_label.setText(f"Counter: {counter}")
        
        # Set format preset dropdown to "Custom" if format doesn't match a preset
        current_format = qn.get('format', '{YYYY}-{NNN}')
        preset_idx = self.qn_format_presets.findData(current_format)
        if preset_idx >= 0:
            self.qn_format_presets.blockSignals(True)
            self.qn_format_presets.setCurrentIndex(preset_idx)
            self.qn_format_presets.blockSignals(False)
        else:
            self.qn_format_presets.blockSignals(True)
            self.qn_format_presets.setCurrentIndex(0)  # Custom
            self.qn_format_presets.blockSignals(False)
        
        # Typography
        typography = preset.get('typography', {})
        
        # Set font dropdowns (handle both existing values and new ones)
        heading_font = typography.get('heading', 'Montserrat')
        idx = self.typo_heading.findText(heading_font)
        if idx >= 0:
            self.typo_heading.setCurrentIndex(idx)
        else:
            self.typo_heading.setCurrentText(heading_font)
        
        body_font = typography.get('body', 'Source Sans Pro')
        idx = self.typo_body.findText(body_font)
        if idx >= 0:
            self.typo_body.setCurrentIndex(idx)
        else:
            self.typo_body.setCurrentText(body_font)
        
        mono_font = typography.get('mono', 'JetBrains Mono')
        idx = self.typo_mono.findText(mono_font)
        if idx >= 0:
            self.typo_mono.setCurrentIndex(idx)
        else:
            self.typo_mono.setCurrentText(mono_font)
        
        sizes = typography.get('sizes', {})
        self.typo_size_company.setValue(sizes.get('company_name', 24))
        self.typo_size_h1.setValue(sizes.get('heading1', 18))
        self.typo_size_h2.setValue(sizes.get('heading2', 14))
        self.typo_size_body.setValue(sizes.get('body', 10))
        self.typo_size_small.setValue(sizes.get('small', 8))
        
        # Colors
        colors = preset.get('colors', {})
        self.color_primary.setColor(colors.get('primary', '#1a1a2e'))
        self.color_accent.setColor(colors.get('accent', '#e94560'))
        self.color_background.setColor(colors.get('background', '#ffffff'))
        self.color_text.setColor(colors.get('text', '#2d2d2d'))
        self.color_muted.setColor(colors.get('muted', '#6c757d'))
        self.color_border.setColor(colors.get('border', '#dee2e6'))
        self.color_table_alt.setColor(colors.get('table_alt', '#f8f9fa'))

    def _edit_template(self):
        """Open the template editor for the current preset's template."""
        # Template name matches preset key directly
        dialog = TemplateEditorDialog(self.current_preset_key, self.config_loader, self)
        dialog.exec()

    def _edit_css(self):
        """Open the CSS editor for the current preset's stylesheet."""
        # Template name matches preset key directly
        dialog = CSSEditorDialog(self.current_preset_key, self.config_loader, self)
        dialog.exec()

    def _save_config(self):
        """Save the configuration to the YAML file."""
        # Ensure the currently edited preset is saved to the config dict
        self._save_current_preset_to_memory()
        
        # Also update active preset to current one
        self.config['active_preset'] = self.current_preset_key
        
        try:
            # Generate YAML
            yaml_content = self._generate_yaml(self.config)
            
            # Write to file
            with open(self.config_loader.config_path, 'w', encoding='utf-8') as f:
                f.write(yaml_content)
            
            # Update the config loader's config
            self.config_loader.config = self.config
            
            self.configSaved.emit()
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration:\n{e}")
    
    def _generate_yaml(self, config: dict) -> str:
        """Generate formatted YAML."""
        lines = [
            "# MD2Angebot User Configuration",
            f"# Config path: {self.config_loader.config_path}",
            "",
            f"active_preset: {config.get('active_preset', 'preset_1')}",
            "",
            "presets:"
        ]
        
        presets = config.get('presets', {})
        for key in sorted(presets.keys()):
            preset = presets[key]
            dumped = yaml.dump({key: preset}, allow_unicode=True, sort_keys=False)
            lines.append(self._indent_text(dumped, 2))
            lines.append("")
        
        # Add LLM configuration (global, not per-preset)
        llm_config = config.get('llm', {})
        if llm_config:
            lines.append("# LLM Configuration")
            lines.append("llm:")
            dumped = yaml.dump(llm_config, allow_unicode=True, sort_keys=False, default_flow_style=False)
            lines.append(self._indent_text(dumped, 2))
            lines.append("")
            
        return "\n".join(lines)

    def _indent_text(self, text: str, spaces: int) -> str:
        indent = " " * spaces
        return "\n".join(indent + line if line else line for line in text.splitlines())


class SettingsDialog(QDialog):
    """Global settings dialog for LLM configuration."""
    
    configSaved = pyqtSignal()
    
    def __init__(self, config_loader, parent=None):
        super().__init__(parent)
        self.config_loader = config_loader
        self.config = copy.deepcopy(config_loader.config)
        
        self.setWindowTitle("Settings")
        self.setMinimumSize(650, 550)
        self.resize(720, 600)
        
        self._setup_ui()
        self._load_llm_values()
        self._apply_dialog_style()
    
    def _apply_dialog_style(self):
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_base']};
            }}
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollArea > QWidget > QWidget {{
                background-color: transparent;
            }}
        """)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(SPACING['md'])
        layout.setContentsMargins(SPACING['lg'], SPACING['lg'], SPACING['lg'], SPACING['lg'])
        
        # Title
        title_container = QVBoxLayout()
        title_container.setSpacing(2)
        
        title = QLabel("Settings")
        title.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 600;
            color: {COLORS['text_primary']};
        """)
        title_container.addWidget(title)
        
        subtitle = QLabel("Configure global application settings")
        subtitle.setStyleSheet(f"""
            color: {COLORS['text_muted']};
            font-size: 13px;
        """)
        title_container.addWidget(subtitle)
        
        layout.addLayout(title_container)
        
        # LLM Settings Card
        llm_card = SectionCard("LLM Configuration")
        
        # Main content layout - use grid for proper alignment
        content_grid = QGridLayout()
        content_grid.setSpacing(SPACING['sm'])
        content_grid.setColumnMinimumWidth(0, 80)  # Label column
        content_grid.setColumnStretch(1, 1)  # Input column stretches
        
        # Provider row
        provider_label = QLabel("Provider")
        provider_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: 500; font-size: 12px;")
        content_grid.addWidget(provider_label, 0, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        self.llm_provider = QComboBox()
        self.llm_provider.addItem("OpenRouter", "openrouter")
        self.llm_provider.addItem("OpenAI", "openai")
        self.llm_provider.setMinimumHeight(30)
        self.llm_provider.currentIndexChanged.connect(self._on_llm_provider_changed)
        content_grid.addWidget(self.llm_provider, 0, 1)
        
        # Model row
        model_label = QLabel("Model")
        model_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: 500; font-size: 12px;")
        content_grid.addWidget(model_label, 1, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        self.llm_model = QComboBox()
        self.llm_model.setMinimumHeight(30)
        self._populate_model_dropdown()
        content_grid.addWidget(self.llm_model, 1, 1)
        
        # API Key row (with visibility toggle button)
        api_key_label = QLabel("API Key")
        api_key_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: 500; font-size: 12px;")
        content_grid.addWidget(api_key_label, 2, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        api_key_container = QWidget()
        api_key_layout = QHBoxLayout(api_key_container)
        api_key_layout.setContentsMargins(0, 0, 0, 0)
        api_key_layout.setSpacing(0)
        
        self.llm_api_key = QLineEdit()
        self.llm_api_key.setPlaceholderText("sk-... or your OpenRouter key")
        self.llm_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.llm_api_key.setMinimumHeight(30)
        api_key_layout.addWidget(self.llm_api_key)
        
        self.llm_api_key_toggle = QPushButton()
        self.llm_api_key_toggle.setIcon(icon('visibility', 16, COLORS['text_secondary']))
        self.llm_api_key_toggle.setFixedSize(34, 30)
        self.llm_api_key_toggle.setCheckable(True)
        self.llm_api_key_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.llm_api_key_toggle.setToolTip("Show/hide API key")
        self.llm_api_key_toggle.toggled.connect(self._toggle_api_key_visibility)
        self.llm_api_key_toggle.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_elevated']};
                border: 1px solid {COLORS['border']};
                border-left: none;
                border-radius: 0;
                padding: 0;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_hover']};
            }}
            QPushButton:checked {{
                background-color: {COLORS['accent']};
                border-color: {COLORS['accent']};
            }}
        """)
        api_key_layout.addWidget(self.llm_api_key_toggle)
        
        content_grid.addWidget(api_key_container, 2, 1)
        
        llm_card.addLayout(content_grid)
        layout.addWidget(llm_card)
        
        # System Prompt Card
        prompt_card = SectionCard("System Prompt")
        
        prompt_header = QHBoxLayout()
        prompt_header.setSpacing(SPACING['sm'])
        
        prompt_hint = QLabel("The system prompt instructs the LLM how to generate quotation content")
        prompt_hint.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
        prompt_header.addWidget(prompt_hint)
        prompt_header.addStretch()
        
        reset_prompt_btn = QPushButton("Reset to Default")
        reset_prompt_btn.setMinimumWidth(100)
        reset_prompt_btn.clicked.connect(self._reset_system_prompt)
        prompt_header.addWidget(reset_prompt_btn)
        
        prompt_card.addLayout(prompt_header)
        
        self.llm_system_prompt = QPlainTextEdit()
        self.llm_system_prompt.setPlaceholderText("Enter your system prompt here...")
        self.llm_system_prompt.setMinimumHeight(180)
        self.llm_system_prompt.setStyleSheet(f"""
            QPlainTextEdit {{
                font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
                font-size: 12px;
                background-color: {COLORS['bg_elevated']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                padding: {SPACING['sm']}px;
            }}
        """)
        prompt_card.addWidget(self.llm_system_prompt)
        
        layout.addWidget(prompt_card)
        
        layout.addStretch()
        
        # Bottom buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(SPACING['sm'])
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumWidth(80)
        cancel_btn.setFixedHeight(32)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save Settings")
        save_btn.setMinimumWidth(120)
        save_btn.setFixedHeight(32)
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._save_config)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                font-weight: 600;
                padding: 0 20px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #d63650;
            }}
        """)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def _populate_model_dropdown(self):
        """Populate the model dropdown based on the selected provider."""
        self.llm_model.clear()
        provider = self.llm_provider.currentData()
        
        if provider == 'openai':
            models = OPENAI_MODELS
        else:
            models = OPENROUTER_MODELS
        
        for model_id, display_name in models.items():
            self.llm_model.addItem(display_name, model_id)
    
    def _on_llm_provider_changed(self, index):
        """Handle provider selection change."""
        current_model = self.llm_model.currentData()
        self._populate_model_dropdown()
        
        idx = self.llm_model.findData(current_model)
        if idx >= 0:
            self.llm_model.setCurrentIndex(idx)
    
    def _toggle_api_key_visibility(self, checked: bool):
        """Toggle API key visibility."""
        if checked:
            self.llm_api_key.setEchoMode(QLineEdit.EchoMode.Normal)
            self.llm_api_key_toggle.setIcon(icon('visibility_off', 16, COLORS['text_primary']))
        else:
            self.llm_api_key.setEchoMode(QLineEdit.EchoMode.Password)
            self.llm_api_key_toggle.setIcon(icon('visibility', 16, COLORS['text_secondary']))
    
    def _reset_system_prompt(self):
        """Reset system prompt to default."""
        reply = QMessageBox.question(
            self,
            "Reset System Prompt",
            "Are you sure you want to reset the system prompt to the default value?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.llm_system_prompt.setPlainText(DEFAULT_SYSTEM_PROMPT)
    
    def _load_llm_values(self):
        """Load LLM configuration values into the UI."""
        llm_config = self.config.get('llm', {})
        
        # Provider
        provider = llm_config.get('provider', 'openrouter')
        idx = self.llm_provider.findData(provider)
        if idx >= 0:
            self.llm_provider.setCurrentIndex(idx)
        
        self._populate_model_dropdown()
        
        # Model
        model = llm_config.get('model', 'anthropic/claude-sonnet-4')
        idx = self.llm_model.findData(model)
        if idx >= 0:
            self.llm_model.setCurrentIndex(idx)
        
        # API Key
        self.llm_api_key.setText(llm_config.get('api_key', ''))
        
        # System Prompt
        self.llm_system_prompt.setPlainText(
            llm_config.get('system_prompt', DEFAULT_SYSTEM_PROMPT)
        )
    
    def _save_config(self):
        """Save the LLM configuration to the YAML file."""
        self.config['llm'] = {
            'provider': self.llm_provider.currentData() or 'openrouter',
            'api_key': self.llm_api_key.text(),
            'model': self.llm_model.currentData() or 'anthropic/claude-sonnet-4',
            'system_prompt': self.llm_system_prompt.toPlainText() or DEFAULT_SYSTEM_PROMPT
        }
        
        try:
            # Generate YAML
            yaml_content = self._generate_yaml(self.config)
            
            # Write to file
            with open(self.config_loader.config_path, 'w', encoding='utf-8') as f:
                f.write(yaml_content)
            
            # Update the config loader's config
            self.config_loader.config = self.config
            
            self.configSaved.emit()
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration:\n{e}")
    
    def _generate_yaml(self, config: dict) -> str:
        """Generate formatted YAML."""
        lines = [
            "# MD2Angebot User Configuration",
            f"# Config path: {self.config_loader.config_path}",
            "",
            f"active_preset: {config.get('active_preset', 'preset_1')}",
            "",
            "presets:"
        ]
        
        presets = config.get('presets', {})
        for key in sorted(presets.keys()):
            preset = presets[key]
            dumped = yaml.dump({key: preset}, allow_unicode=True, sort_keys=False)
            lines.append(self._indent_text(dumped, 2))
            lines.append("")
        
        # Add LLM configuration
        llm_config = config.get('llm', {})
        if llm_config:
            lines.append("# LLM Configuration")
            lines.append("llm:")
            dumped = yaml.dump(llm_config, allow_unicode=True, sort_keys=False, default_flow_style=False)
            lines.append(self._indent_text(dumped, 2))
            lines.append("")
            
        return "\n".join(lines)
    
    def _indent_text(self, text: str, spaces: int) -> str:
        indent = " " * spaces
        return "\n".join(indent + line if line else line for line in text.splitlines())
