"""
Configuration Assistant Dialog for MD2Angebot.

A visually refined settings dialog with tabs for each configuration category.
"""

import os
import yaml
import copy
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox,
    QPushButton, QFileDialog, QScrollArea, QFrame, QGridLayout,
    QGroupBox, QColorDialog, QMessageBox, QSizePolicy, QListWidget,
    QListWidgetItem, QInputDialog, QButtonGroup, QPlainTextEdit, QCheckBox
)
from PyQt6.QtGui import QColor, QPalette, QFont, QIcon
from PyQt6.QtCore import Qt, pyqtSignal

from .styles import COLORS, SPACING, RADIUS


class ColorButton(QPushButton):
    """A button that displays and allows selection of a color."""
    
    colorChanged = pyqtSignal(str)
    
    def __init__(self, color: str = "#ffffff", parent=None):
        super().__init__(parent)
        self._color = color
        self.setFixedSize(48, 32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(self._pick_color)
        self._update_style()
    
    def _update_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._color};
                border: 2px solid {COLORS['border']};
                border-radius: {RADIUS['sm']}px;
            }}
            QPushButton:hover {{
                border-color: {COLORS['text_secondary']};
            }}
        """)
    
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


class SectionHeader(QLabel):
    """A styled section header label."""
    
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['accent']};
                font-size: 11px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 1px;
                padding: {SPACING['sm']}px 0;
                border-bottom: 1px solid {COLORS['border']};
                margin-bottom: {SPACING['md']}px;
            }}
        """)


class FormRow(QWidget):
    """A horizontal form row with label and input widget."""
    
    def __init__(self, label: str, widget: QWidget, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING['md'])
        
        lbl = QLabel(label)
        self.label_widget = lbl
        lbl.setFixedWidth(140)
        lbl.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-weight: 500;
        """)
        layout.addWidget(lbl)
        
        layout.addWidget(widget, 1)


class ConfigDialog(QDialog):
    """Main configuration dialog with tabbed interface."""
    
    configSaved = pyqtSignal()
    
    def __init__(self, config_loader, parent=None):
        super().__init__(parent)
        self.config_loader = config_loader
        # Deep copy config so we can modify freely
        self.config = copy.deepcopy(config_loader.config)
        
        # Track which preset we are currently editing
        self.current_preset_key = self.config.get('active_preset', 'preset_1')
        
        self.setWindowTitle("Configuration Assistant")
        self.setMinimumSize(800, 700)
        self.resize(900, 800)
        
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
                border-radius: {RADIUS['md']}px;
                background-color: {COLORS['bg_elevated']};
                padding: {SPACING['md']}px;
            }}
            QTabBar::tab {{
                background-color: {COLORS['bg_dark']};
                border: 1px solid {COLORS['border']};
                border-bottom: none;
                border-top-left-radius: {RADIUS['md']}px;
                border-top-right-radius: {RADIUS['md']}px;
                padding: {SPACING['sm']}px {SPACING['lg']}px;
                margin-right: 2px;
                color: {COLORS['text_secondary']};
                font-weight: 500;
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['bg_elevated']};
                color: {COLORS['text_primary']};
                border-bottom: 1px solid {COLORS['bg_elevated']};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {COLORS['bg_hover']};
            }}
            QGroupBox {{
                border: 1px solid {COLORS['border']};
                border-radius: {RADIUS['md']}px;
                margin-top: 16px;
                padding: {SPACING['md']}px;
                padding-top: 24px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                padding: 0 8px;
                color: {COLORS['accent']};
                font-weight: 600;
                font-size: 12px;
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
        title_container = QHBoxLayout()
        title_col = QVBoxLayout()
        
        title = QLabel("Configuration Assistant")
        title.setStyleSheet(f"""
            font-size: 20px;
            font-weight: 600;
            color: {COLORS['text_primary']};
            padding-bottom: {SPACING['sm']}px;
        """)
        title_col.addWidget(title)
        
        subtitle = QLabel("Customize your 5 sender presets")
        subtitle.setStyleSheet(f"""
            color: {COLORS['text_muted']};
            font-size: 13px;
        """)
        title_col.addWidget(subtitle)
        
        title_container.addLayout(title_col)
        title_container.addStretch()
        layout.addLayout(title_container)
        
        # Preset Selector
        preset_layout = QHBoxLayout()
        preset_layout.setSpacing(SPACING['sm'])
        
        self.preset_group = QButtonGroup(self)
        self.preset_group.setExclusive(True)
        self.preset_group.buttonClicked.connect(self._on_preset_changed)
        
        presets = self.config.get('presets', {})
        for i in range(1, 6):
            key = f"preset_{i}"
            preset_data = presets.get(key, {})
            name = preset_data.get('name', f"Preset {i}")
            
            btn = QPushButton(f"{i}. {name}")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setProperty("preset_key", key)
            btn.setFixedHeight(40)
            
            if key == self.current_preset_key:
                btn.setChecked(True)
                
            self.preset_group.addButton(btn)
            preset_layout.addWidget(btn)
            
        layout.addLayout(preset_layout)
        
        # Current Preset Name Editor
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Preset Name:"))
        self.preset_name_edit = QLineEdit()
        self.preset_name_edit.setPlaceholderText("e.g. Company A, Freelance, Private")
        self.preset_name_edit.textChanged.connect(self._update_preset_button_text)
        name_layout.addWidget(self.preset_name_edit)
        layout.addLayout(name_layout)
        
        # Tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Create tabs
        self.tabs.addTab(self._create_company_tab(), "Company")
        self.tabs.addTab(self._create_contact_tab(), "Contact")
        self.tabs.addTab(self._create_legal_tab(), "Legal & Bank")
        self.tabs.addTab(self._create_layout_tab(), "Layout & Snippets")
        self.tabs.addTab(self._create_defaults_tab(), "Defaults")
        self.tabs.addTab(self._create_typography_tab(), "Typography")
        self.tabs.addTab(self._create_colors_tab(), "Colors")
        
        # Bottom buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save Configuration")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._save_config)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        
        # Style for preset buttons
        self.setStyleSheet(self.styleSheet() + f"""
            QPushButton[checkable="true"] {{
                background-color: {COLORS['bg_dark']};
                border: 1px solid {COLORS['border']};
                color: {COLORS['text_secondary']};
                padding: 0 16px;
                border-radius: {RADIUS['md']}px;
                text-align: left;
            }}
            QPushButton[checkable="true"]:checked {{
                background-color: {COLORS['accent']};
                color: white;
                border: 1px solid {COLORS['accent']};
            }}
            QPushButton[checkable="true"]:hover:!checked {{
                background-color: {COLORS['bg_hover']};
            }}
        """)
    
    def _create_scrollable_tab(self) -> tuple[QScrollArea, QVBoxLayout]:
        """Creates a scrollable container for tab content."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(SPACING['md'])
        content_layout.setContentsMargins(SPACING['sm'], SPACING['sm'], SPACING['sm'], SPACING['sm'])
        
        scroll.setWidget(content)
        return scroll, content_layout
    
    def _create_company_tab(self) -> QWidget:
        scroll, layout = self._create_scrollable_tab()
        
        # Company Info
        layout.addWidget(SectionHeader("Company Information"))
        
        self.company_name = QLineEdit()
        self.company_name.setPlaceholderText("Your Company Name")
        layout.addWidget(FormRow("Company Name", self.company_name))
        
        self.company_tagline = QLineEdit()
        self.company_tagline.setPlaceholderText("Your tagline or slogan")
        layout.addWidget(FormRow("Tagline", self.company_tagline))
        
        self.company_logo = PathSelector("Images (*.svg *.png *.jpg *.jpeg)")
        layout.addWidget(FormRow("Logo", self.company_logo))
        
        layout.addStretch()
        return scroll
    
    def _create_contact_tab(self) -> QWidget:
        scroll, layout = self._create_scrollable_tab()
        
        layout.addWidget(SectionHeader("Contact Details"))
        
        self.contact_street = QLineEdit()
        self.contact_street.setPlaceholderText("Street Address")
        layout.addWidget(FormRow("Street", self.contact_street))
        
        self.contact_city = QLineEdit()
        self.contact_city.setPlaceholderText("City")
        layout.addWidget(FormRow("City", self.contact_city))
        
        self.contact_postal = QLineEdit()
        self.contact_postal.setPlaceholderText("Postal Code")
        layout.addWidget(FormRow("Postal Code", self.contact_postal))
        
        self.contact_country = QLineEdit()
        self.contact_country.setPlaceholderText("Country")
        layout.addWidget(FormRow("Country", self.contact_country))
        
        self.contact_phone = QLineEdit()
        self.contact_phone.setPlaceholderText("+31 6 1234 5678")
        layout.addWidget(FormRow("Phone", self.contact_phone))
        
        self.contact_email = QLineEdit()
        self.contact_email.setPlaceholderText("hello@example.com")
        layout.addWidget(FormRow("Email", self.contact_email))
        
        self.contact_website = QLineEdit()
        self.contact_website.setPlaceholderText("www.example.com")
        layout.addWidget(FormRow("Website", self.contact_website))
        
        layout.addStretch()
        return scroll
    
    def _create_legal_tab(self) -> QWidget:
        scroll, layout = self._create_scrollable_tab()
        
        # Legal
        layout.addWidget(SectionHeader("Legal Information"))
        
        self.legal_tax_id = QLineEdit()
        self.legal_tax_id.setPlaceholderText("VAT / Tax ID")
        layout.addWidget(FormRow("Tax ID", self.legal_tax_id))
        
        self.legal_kvk = QLineEdit()
        self.legal_kvk.setPlaceholderText("Chamber of Commerce / Registration")
        layout.addWidget(FormRow("CoC Number", self.legal_kvk))
        
        # Bank
        layout.addWidget(SectionHeader("Banking Details"))
        
        self.bank_holder = QLineEdit()
        self.bank_holder.setPlaceholderText("Account Holder Name")
        layout.addWidget(FormRow("Account Holder", self.bank_holder))
        
        self.bank_iban = QLineEdit()
        self.bank_iban.setPlaceholderText("NL91 ABNA 0417 1643 00")
        layout.addWidget(FormRow("IBAN", self.bank_iban))
        
        self.bank_bic = QLineEdit()
        self.bank_bic.setPlaceholderText("ABNANL2A")
        layout.addWidget(FormRow("BIC / SWIFT", self.bank_bic))
        
        self.bank_name = QLineEdit()
        self.bank_name.setPlaceholderText("Bank Name")
        layout.addWidget(FormRow("Bank Name", self.bank_name))
        
        layout.addStretch()
        return scroll
    
    def _create_layout_tab(self) -> QWidget:
        scroll, layout = self._create_scrollable_tab()
        
        # Template Selection
        layout.addWidget(SectionHeader("Layout Template"))
        
        self.layout_template = QComboBox()
        self.layout_template.addItem("Modern Split (Default)", "modern-split")
        self.layout_template.addItem("Elegant Centered (Photography)", "elegant-centered")
        self.layout_template.addItem("Minimal Sidebar (Consulting)", "minimal-sidebar")
        self.layout_template.addItem("Bold Stamp (Creative)", "bold-stamp")
        self.layout_template.addItem("Classic Letterhead (Business)", "classic-letterhead")
        layout.addWidget(FormRow("Template", self.layout_template))
        
        # Margins
        layout.addWidget(SectionHeader("Page Margins (mm)"))
        
        margins_layout = QHBoxLayout()
        margins_layout.setSpacing(10)
        
        self.margin_top = QSpinBox()
        self.margin_top.setRange(0, 100)
        self.margin_top.setPrefix("T: ")
        margins_layout.addWidget(self.margin_top)
        
        self.margin_right = QSpinBox()
        self.margin_right.setRange(0, 100)
        self.margin_right.setPrefix("R: ")
        margins_layout.addWidget(self.margin_right)
        
        self.margin_bottom = QSpinBox()
        self.margin_bottom.setRange(0, 100)
        self.margin_bottom.setPrefix("B: ")
        margins_layout.addWidget(self.margin_bottom)
        
        self.margin_left = QSpinBox()
        self.margin_left.setRange(0, 100)
        self.margin_left.setPrefix("L: ")
        margins_layout.addWidget(self.margin_left)
        
        layout.addLayout(margins_layout)
        
        # Snippets
        layout.addWidget(SectionHeader("Content Snippets"))
        
        self.snippet_intro = QPlainTextEdit()
        self.snippet_intro.setPlaceholderText("Introductory text before the line items...")
        self.snippet_intro.setFixedHeight(60)
        layout.addWidget(QLabel("Intro Text"))
        layout.addWidget(self.snippet_intro)
        
        self.snippet_terms = QPlainTextEdit()
        self.snippet_terms.setPlaceholderText("Payment terms, conditions, validity...")
        self.snippet_terms.setFixedHeight(60)
        layout.addWidget(QLabel("Terms & Conditions"))
        layout.addWidget(self.snippet_terms)
        
        self.snippet_footer = QLineEdit()
        self.snippet_footer.setPlaceholderText("Extra text for page footer (e.g. page number override or small print)")
        layout.addWidget(FormRow("Custom Footer", self.snippet_footer))
        
        self.snippet_signature = QCheckBox("Show Signature Block")
        layout.addWidget(self.snippet_signature)
        
        layout.addStretch()
        return scroll

    def _create_defaults_tab(self) -> QWidget:
        scroll, layout = self._create_scrollable_tab()
        
        layout.addWidget(SectionHeader("Default Values"))
        
        self.defaults_currency = QLineEdit()
        self.defaults_currency.setPlaceholderText("EUR, USD, etc.")
        layout.addWidget(FormRow("Currency", self.defaults_currency))
        
        self.defaults_tax_rate = QSpinBox()
        self.defaults_tax_rate.setRange(0, 100)
        self.defaults_tax_rate.setSuffix(" %")
        layout.addWidget(FormRow("Tax Rate", self.defaults_tax_rate))
        
        self.defaults_payment_days = QSpinBox()
        self.defaults_payment_days.setRange(1, 365)
        self.defaults_payment_days.setSuffix(" days")
        layout.addWidget(FormRow("Payment Terms", self.defaults_payment_days))
        
        self.defaults_language = QComboBox()
        self.defaults_language.addItems(["de", "en", "nl"])
        layout.addWidget(FormRow("Language", self.defaults_language))
        
        # Quotation Number Settings
        layout.addWidget(SectionHeader("Quotation Number"))
        
        qn_desc = QLabel(
            "Configure automatic quotation numbering. Use placeholders:\n"
            "• {YYYY} = Full year (2025)  • {YY} = Short year (25)\n"
            "• {MM} = Month (01-12)  • {DD} = Day (01-31)\n"
            "• {N}/{NN}/{NNN}/{NNNN} = Counter with padding\n"
            "• {PREFIX} = Company abbreviation"
        )
        qn_desc.setWordWrap(True)
        qn_desc.setStyleSheet(f"color: {COLORS['text_muted']}; margin-bottom: {SPACING['sm']}px; font-size: 11px;")
        layout.addWidget(qn_desc)
        
        from PyQt6.QtWidgets import QCheckBox
        self.qn_enabled = QCheckBox("Enable automatic quotation numbering")
        self.qn_enabled.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(self.qn_enabled)
        
        self.qn_format = QLineEdit()
        self.qn_format.setPlaceholderText("{YYYY}-{NNN}")
        layout.addWidget(FormRow("Number Format", self.qn_format))
        
        # Format examples/presets dropdown
        self.qn_format_presets = QComboBox()
        self.qn_format_presets.addItem("Custom", "")
        self.qn_format_presets.addItem("Year-Number: 2025-001", "{YYYY}-{NNN}")
        self.qn_format_presets.addItem("Invoice Style: INV-2025-0001", "INV-{YYYY}-{NNNN}")
        self.qn_format_presets.addItem("Monthly Reset: 2025-01-001", "{YYYY}-{MM}-{NNN}")
        self.qn_format_presets.addItem("Compact: Q25-001", "Q{YY}-{NNN}")
        self.qn_format_presets.addItem("With Prefix: JDC-2025-01", "{PREFIX}-{YYYY}-{NN}")
        self.qn_format_presets.currentIndexChanged.connect(self._on_qn_preset_selected)
        layout.addWidget(FormRow("Format Presets", self.qn_format_presets))
        
        # Current counter display (read-only info)
        self.qn_counter_label = QLabel("Counter: 0")
        self.qn_counter_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
        layout.addWidget(self.qn_counter_label)
        
        # Reset counter button
        reset_counter_btn = QPushButton("Reset Counter to 0")
        reset_counter_btn.setFixedWidth(150)
        reset_counter_btn.clicked.connect(self._reset_qn_counter)
        layout.addWidget(reset_counter_btn)
        
        layout.addStretch()
        return scroll
    
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
    
    def _create_typography_tab(self) -> QWidget:
        scroll, layout = self._create_scrollable_tab()
        
        layout.addWidget(SectionHeader("Font Families"))
        
        self.typo_heading = QLineEdit()
        self.typo_heading.setPlaceholderText("Montserrat, Arial, etc.")
        layout.addWidget(FormRow("Headings", self.typo_heading))
        
        self.typo_body = QLineEdit()
        self.typo_body.setPlaceholderText("Source Sans Pro, Helvetica, etc.")
        layout.addWidget(FormRow("Body Text", self.typo_body))
        
        self.typo_mono = QLineEdit()
        self.typo_mono.setPlaceholderText("JetBrains Mono, Menlo, etc.")
        layout.addWidget(FormRow("Monospace", self.typo_mono))
        
        layout.addWidget(SectionHeader("Font Sizes (px)"))
        
        self.typo_size_company = QSpinBox()
        self.typo_size_company.setRange(8, 72)
        layout.addWidget(FormRow("Company Name", self.typo_size_company))
        
        self.typo_size_h1 = QSpinBox()
        self.typo_size_h1.setRange(8, 72)
        layout.addWidget(FormRow("Heading 1", self.typo_size_h1))
        
        self.typo_size_h2 = QSpinBox()
        self.typo_size_h2.setRange(8, 72)
        layout.addWidget(FormRow("Heading 2", self.typo_size_h2))
        
        self.typo_size_body = QSpinBox()
        self.typo_size_body.setRange(8, 72)
        layout.addWidget(FormRow("Body", self.typo_size_body))
        
        self.typo_size_small = QSpinBox()
        self.typo_size_small.setRange(6, 72)
        layout.addWidget(FormRow("Small Text", self.typo_size_small))
        
        layout.addStretch()
        return scroll
    
    def _create_colors_tab(self) -> QWidget:
        scroll, layout = self._create_scrollable_tab()
        
        layout.addWidget(SectionHeader("Document Color Scheme"))
        
        desc = QLabel("These colors are used in the PDF output, not the application UI.")
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {COLORS['text_muted']}; margin-bottom: {SPACING['md']}px;")
        layout.addWidget(desc)
        
        self.color_primary = ColorButton()
        layout.addWidget(FormRow("Primary", self.color_primary))
        
        self.color_accent = ColorButton()
        layout.addWidget(FormRow("Accent", self.color_accent))
        
        self.color_background = ColorButton()
        layout.addWidget(FormRow("Background", self.color_background))
        
        self.color_text = ColorButton()
        layout.addWidget(FormRow("Text", self.color_text))
        
        self.color_muted = ColorButton()
        layout.addWidget(FormRow("Muted Text", self.color_muted))
        
        self.color_border = ColorButton()
        layout.addWidget(FormRow("Borders", self.color_border))
        
        self.color_table_alt = ColorButton()
        layout.addWidget(FormRow("Table Alt Row", self.color_table_alt))
        
        layout.addStretch()
        return scroll
    
    def _on_preset_changed(self, button):
        """Handle preset switching. Save current form to memory, load new preset."""
        new_key = button.property("preset_key")
        if new_key == self.current_preset_key:
            return
        
        # Save current values to memory
        self._save_current_preset_to_memory()
        
        # Update current key
        self.current_preset_key = new_key
        
        # Load new values
        self._load_preset_values(new_key)
        
    def _update_preset_button_text(self, text):
        """Update the text of the button for the current preset."""
        button = self.preset_group.checkedButton()
        if button:
            # Extract number prefix
            current_text = button.text()
            prefix = current_text.split('.')[0]
            button.setText(f"{prefix}. {text}")
            
            # Also update in memory config immediately for name
            # Ensure keys exist
            if 'presets' not in self.config:
                self.config['presets'] = {}
            if self.current_preset_key not in self.config['presets']:
                self.config['presets'][self.current_preset_key] = {}
                
            self.config['presets'][self.current_preset_key]['name'] = text
            
    def _save_current_preset_to_memory(self):
        """Saves values from UI fields into self.config for the current preset."""
        presets = self.config.setdefault('presets', {})
        preset = presets.setdefault(self.current_preset_key, {})
        
        preset['name'] = self.preset_name_edit.text()
        
        preset['company'] = {
            'name': self.company_name.text(),
            'tagline': self.company_tagline.text(),
            'logo': self.company_logo.path(),
        }
        
        preset['contact'] = {
            'street': self.contact_street.text(),
            'city': self.contact_city.text(),
            'postal_code': self.contact_postal.text(),
            'country': self.contact_country.text(),
            'phone': self.contact_phone.text(),
            'email': self.contact_email.text(),
            'website': self.contact_website.text(),
        }
        
        preset['legal'] = {
            'tax_id': self.legal_tax_id.text(),
            'chamber_of_commerce': self.legal_kvk.text(),
        }
        
        preset['layout'] = {
            'template': self.layout_template.currentData(),
            'page_margins': [
                self.margin_top.value(),
                self.margin_right.value(),
                self.margin_bottom.value(),
                self.margin_left.value()
            ]
        }
        
        preset['snippets'] = {
            'intro_text': self.snippet_intro.toPlainText(),
            'terms': self.snippet_terms.toPlainText(),
            'custom_footer': self.snippet_footer.text(),
            'signature_block': self.snippet_signature.isChecked()
        }

        preset['bank'] = {
            'holder': self.bank_holder.text(),
            'iban': self.bank_iban.text(),
            'bic': self.bank_bic.text(),
            'bank_name': self.bank_name.text(),
        }
        
        preset['defaults'] = {
            'currency': self.defaults_currency.text(),
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
            'heading': self.typo_heading.text(),
            'body': self.typo_body.text(),
            'mono': self.typo_mono.text(),
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
        # Get preset or defaults from empty preset in loader logic, but we are working on a dict here
        # So if missing, we should probably use the helper from loader or just empty dicts.
        # To be safe, let's get it from self.config
        preset = presets.get(preset_key, {})
        
        # Name
        self.preset_name_edit.blockSignals(True)
        self.preset_name_edit.setText(preset.get('name', ''))
        self.preset_name_edit.blockSignals(False)
        
        # Company
        company = preset.get('company', {})
        self.company_name.setText(company.get('name', ''))
        self.company_tagline.setText(company.get('tagline', ''))
        self.company_logo.setPath(company.get('logo', ''))
        
        # Contact
        contact = preset.get('contact', {})
        self.contact_street.setText(contact.get('street', ''))
        self.contact_city.setText(contact.get('city', ''))
        self.contact_postal.setText(contact.get('postal_code', ''))
        self.contact_country.setText(contact.get('country', ''))
        self.contact_phone.setText(contact.get('phone', ''))
        self.contact_email.setText(contact.get('email', ''))
        self.contact_website.setText(contact.get('website', ''))
        
        # Legal
        legal = preset.get('legal', {})
        self.legal_tax_id.setText(legal.get('tax_id', ''))
        self.legal_kvk.setText(legal.get('chamber_of_commerce', ''))
        
        # Layout
        layout_config = preset.get('layout', {})
        template = layout_config.get('template', 'modern-split')
        idx = self.layout_template.findData(template)
        if idx >= 0:
            self.layout_template.setCurrentIndex(idx)
        
        margins = layout_config.get('page_margins', [20, 20, 20, 20])
        if len(margins) == 4:
            self.margin_top.setValue(margins[0])
            self.margin_right.setValue(margins[1])
            self.margin_bottom.setValue(margins[2])
            self.margin_left.setValue(margins[3])
            
        # Snippets
        snippets = preset.get('snippets', {})
        self.snippet_intro.setPlainText(snippets.get('intro_text', ''))
        self.snippet_terms.setPlainText(snippets.get('terms', ''))
        self.snippet_footer.setText(snippets.get('custom_footer', ''))
        self.snippet_signature.setChecked(snippets.get('signature_block', True))
        
        # Bank
        bank = preset.get('bank', {})
        self.bank_holder.setText(bank.get('holder', ''))
        self.bank_iban.setText(bank.get('iban', ''))
        self.bank_bic.setText(bank.get('bic', ''))
        self.bank_name.setText(bank.get('bank_name', ''))
        
        # Defaults
        defaults = preset.get('defaults', {})
        self.defaults_currency.setText(defaults.get('currency', 'EUR'))
        self.defaults_tax_rate.setValue(defaults.get('tax_rate', 19))
        self.defaults_payment_days.setValue(defaults.get('payment_days', 14))
        lang = defaults.get('language', 'de')
        idx = self.defaults_language.findText(lang)
        if idx >= 0:
            self.defaults_language.setCurrentIndex(idx)
        
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
        self.typo_heading.setText(typography.get('heading', 'Montserrat'))
        self.typo_body.setText(typography.get('body', 'Source Sans Pro'))
        self.typo_mono.setText(typography.get('mono', 'JetBrains Mono'))
        
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

    def _save_config(self):
        """Save the configuration to the YAML file."""
        # Ensure the currently edited preset is saved to the config dict
        self._save_current_preset_to_memory()
        
        # Also update active preset to current one? Yes, likely what user expects.
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
            QMessageBox.information(self, "Success", "Configuration saved successfully!")
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
            # We dump each preset indented
            preset_yaml = yaml.dump({key: preset}, allow_unicode=True, sort_keys=False)
            # Indent is handled by yaml dump if we dump the dict with key, but let's check indentation
            # yaml.dump({key: preset}) will output "key:\n  value..."
            # We want it under "presets:" which we already added.
            # So we can just append indented lines.
            
            dumped = yaml.dump({key: preset}, allow_unicode=True, sort_keys=False)
            lines.append(self._indent_text(dumped, 2))
            lines.append("")
            
        return "\n".join(lines)

    def _indent_text(self, text: str, spaces: int) -> str:
        indent = " " * spaces
        return "\n".join(indent + line if line else line for line in text.splitlines())
