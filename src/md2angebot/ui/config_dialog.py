"""
Configuration Assistant Dialog for MD2Angebot.

A visually refined settings dialog with tabs for each configuration category.
"""

import os
import yaml
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox,
    QPushButton, QFileDialog, QScrollArea, QFrame, QGridLayout,
    QGroupBox, QColorDialog, QMessageBox, QSizePolicy, QListWidget,
    QListWidgetItem, QInputDialog
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
        self.config = config_loader.config.copy()
        
        self.setWindowTitle("Configuration Assistant")
        self.setMinimumSize(700, 600)
        self.resize(800, 700)
        
        self._setup_ui()
        self._load_values()
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
            QListWidget {{
                background-color: {COLORS['bg_dark']};
                border: 1px solid {COLORS['border']};
                border-radius: {RADIUS['md']}px;
                padding: {SPACING['xs']}px;
            }}
            QListWidget::item {{
                padding: {SPACING['sm']}px {SPACING['md']}px;
                border-radius: {RADIUS['sm']}px;
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['accent']};
                color: white;
            }}
            QListWidget::item:hover:!selected {{
                background-color: {COLORS['bg_hover']};
            }}
        """)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(SPACING['md'])
        layout.setContentsMargins(SPACING['lg'], SPACING['lg'], SPACING['lg'], SPACING['lg'])
        
        # Title
        title = QLabel("Configuration Assistant")
        title.setStyleSheet(f"""
            font-size: 20px;
            font-weight: 600;
            color: {COLORS['text_primary']};
            padding-bottom: {SPACING['sm']}px;
        """)
        layout.addWidget(title)
        
        subtitle = QLabel("Customize your company details, styling, and default values")
        subtitle.setStyleSheet(f"""
            color: {COLORS['text_muted']};
            font-size: 13px;
            padding-bottom: {SPACING['md']}px;
        """)
        layout.addWidget(subtitle)
        
        # Tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Create tabs
        self.tabs.addTab(self._create_company_tab(), "Company")
        self.tabs.addTab(self._create_quote_types_tab(), "Quote Types")
        self.tabs.addTab(self._create_contact_tab(), "Contact")
        self.tabs.addTab(self._create_legal_tab(), "Legal & Bank")
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
        layout.addWidget(FormRow("Default Logo", self.company_logo))
        
        layout.addStretch()
        return scroll
    
    def _create_quote_types_tab(self) -> QWidget:
        scroll, layout = self._create_scrollable_tab()
        
        layout.addWidget(SectionHeader("Quote Types"))
        
        desc = QLabel("Define different types of quotations with their own names and logos.")
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {COLORS['text_muted']}; margin-bottom: {SPACING['md']}px;")
        layout.addWidget(desc)
        
        # List and buttons
        list_layout = QHBoxLayout()
        
        self.quote_types_list = QListWidget()
        self.quote_types_list.currentRowChanged.connect(self._on_quote_type_selected)
        list_layout.addWidget(self.quote_types_list, 1)
        
        btn_col = QVBoxLayout()
        btn_col.setSpacing(SPACING['sm'])
        
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self._add_quote_type)
        btn_col.addWidget(add_btn)
        
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self._remove_quote_type)
        btn_col.addWidget(remove_btn)
        
        btn_col.addStretch()
        list_layout.addLayout(btn_col)
        
        layout.addLayout(list_layout)
        
        # Editor for selected type
        self.quote_type_editor = QGroupBox("Selected Quote Type")
        editor_layout = QVBoxLayout(self.quote_type_editor)
        
        self.quote_type_key = QLineEdit()
        self.quote_type_key.setPlaceholderText("e.g., code, photography, design")
        self.quote_type_key.setEnabled(False)
        editor_layout.addWidget(FormRow("Key", self.quote_type_key))
        
        self.quote_type_name = QLineEdit()
        self.quote_type_name.setPlaceholderText("Display name")
        self.quote_type_name.textChanged.connect(self._update_quote_type_name)
        editor_layout.addWidget(FormRow("Name", self.quote_type_name))
        
        self.quote_type_logo = PathSelector("Images (*.svg *.png *.jpg *.jpeg)")
        editor_layout.addWidget(FormRow("Logo", self.quote_type_logo))
        
        layout.addWidget(self.quote_type_editor)
        self.quote_type_editor.setEnabled(False)
        
        # Store quote types data
        self._quote_types_data = {}
        
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
        
        layout.addStretch()
        return scroll
    
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
    
    def _load_values(self):
        """Load current configuration values into the UI."""
        config = self.config
        
        # Company
        company = config.get('company', {})
        self.company_name.setText(company.get('name', ''))
        self.company_tagline.setText(company.get('tagline', ''))
        self.company_logo.setPath(company.get('logo', ''))
        
        # Quote Types
        self._quote_types_data = config.get('quote_types', {}).copy()
        self._refresh_quote_types_list()
        
        # Contact
        contact = config.get('contact', {})
        self.contact_street.setText(contact.get('street', ''))
        self.contact_city.setText(contact.get('city', ''))
        self.contact_postal.setText(contact.get('postal_code', ''))
        self.contact_country.setText(contact.get('country', ''))
        self.contact_phone.setText(contact.get('phone', ''))
        self.contact_email.setText(contact.get('email', ''))
        self.contact_website.setText(contact.get('website', ''))
        
        # Legal
        legal = config.get('legal', {})
        self.legal_tax_id.setText(legal.get('tax_id', ''))
        self.legal_kvk.setText(legal.get('chamber_of_commerce', ''))
        
        # Bank
        bank = config.get('bank', {})
        self.bank_holder.setText(bank.get('holder', ''))
        self.bank_iban.setText(bank.get('iban', ''))
        self.bank_bic.setText(bank.get('bic', ''))
        self.bank_name.setText(bank.get('bank_name', ''))
        
        # Defaults
        defaults = config.get('defaults', {})
        self.defaults_currency.setText(defaults.get('currency', 'EUR'))
        self.defaults_tax_rate.setValue(defaults.get('tax_rate', 19))
        self.defaults_payment_days.setValue(defaults.get('payment_days', 14))
        lang = defaults.get('language', 'de')
        idx = self.defaults_language.findText(lang)
        if idx >= 0:
            self.defaults_language.setCurrentIndex(idx)
        
        # Typography
        typography = config.get('typography', {})
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
        colors = config.get('colors', {})
        self.color_primary.setColor(colors.get('primary', '#1a1a2e'))
        self.color_accent.setColor(colors.get('accent', '#e94560'))
        self.color_background.setColor(colors.get('background', '#ffffff'))
        self.color_text.setColor(colors.get('text', '#2d2d2d'))
        self.color_muted.setColor(colors.get('muted', '#6c757d'))
        self.color_border.setColor(colors.get('border', '#dee2e6'))
        self.color_table_alt.setColor(colors.get('table_alt', '#f8f9fa'))
    
    def _refresh_quote_types_list(self):
        """Refresh the quote types list widget."""
        self.quote_types_list.clear()
        for key, data in self._quote_types_data.items():
            item = QListWidgetItem(f"{data.get('name', key)} ({key})")
            item.setData(Qt.ItemDataRole.UserRole, key)
            self.quote_types_list.addItem(item)
    
    def _on_quote_type_selected(self, row: int):
        """Handle quote type selection."""
        if row < 0:
            self.quote_type_editor.setEnabled(False)
            self.quote_type_key.clear()
            self.quote_type_name.clear()
            self.quote_type_logo.setPath('')
            return
        
        item = self.quote_types_list.item(row)
        if not item:
            return
        
        key = item.data(Qt.ItemDataRole.UserRole)
        data = self._quote_types_data.get(key, {})
        
        self.quote_type_editor.setEnabled(True)
        self.quote_type_key.setText(key)
        self.quote_type_name.blockSignals(True)
        self.quote_type_name.setText(data.get('name', ''))
        self.quote_type_name.blockSignals(False)
        self.quote_type_logo.setPath(data.get('logo', ''))
    
    def _update_quote_type_name(self, name: str):
        """Update the name of the selected quote type."""
        row = self.quote_types_list.currentRow()
        if row < 0:
            return
        
        item = self.quote_types_list.item(row)
        key = item.data(Qt.ItemDataRole.UserRole)
        
        if key in self._quote_types_data:
            self._quote_types_data[key]['name'] = name
            item.setText(f"{name} ({key})")
    
    def _add_quote_type(self):
        """Add a new quote type."""
        key, ok = QInputDialog.getText(
            self, "Add Quote Type", 
            "Enter a unique key (e.g., photography, design):"
        )
        if ok and key:
            key = key.lower().replace(' ', '_')
            if key in self._quote_types_data:
                QMessageBox.warning(self, "Duplicate Key", f"The key '{key}' already exists.")
                return
            
            self._quote_types_data[key] = {'name': key.replace('_', ' ').title(), 'logo': ''}
            self._refresh_quote_types_list()
            
            # Select the new item
            for i in range(self.quote_types_list.count()):
                item = self.quote_types_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == key:
                    self.quote_types_list.setCurrentRow(i)
                    break
    
    def _remove_quote_type(self):
        """Remove the selected quote type."""
        row = self.quote_types_list.currentRow()
        if row < 0:
            return
        
        item = self.quote_types_list.item(row)
        key = item.data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self, "Remove Quote Type",
            f"Are you sure you want to remove '{key}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            del self._quote_types_data[key]
            self._refresh_quote_types_list()
    
    def _gather_values(self) -> dict:
        """Gather all values from the UI into a config dict."""
        # Update quote types with current editor values
        row = self.quote_types_list.currentRow()
        if row >= 0:
            item = self.quote_types_list.item(row)
            key = item.data(Qt.ItemDataRole.UserRole)
            if key in self._quote_types_data:
                self._quote_types_data[key]['name'] = self.quote_type_name.text()
                self._quote_types_data[key]['logo'] = self.quote_type_logo.path()
        
        return {
            'company': {
                'name': self.company_name.text(),
                'tagline': self.company_tagline.text(),
                'logo': self.company_logo.path(),
            },
            'quote_types': self._quote_types_data,
            'contact': {
                'street': self.contact_street.text(),
                'city': self.contact_city.text(),
                'postal_code': self.contact_postal.text(),
                'country': self.contact_country.text(),
                'phone': self.contact_phone.text(),
                'email': self.contact_email.text(),
                'website': self.contact_website.text(),
            },
            'legal': {
                'tax_id': self.legal_tax_id.text(),
                'chamber_of_commerce': self.legal_kvk.text(),
            },
            'bank': {
                'holder': self.bank_holder.text(),
                'iban': self.bank_iban.text(),
                'bic': self.bank_bic.text(),
                'bank_name': self.bank_name.text(),
            },
            'defaults': {
                'currency': self.defaults_currency.text(),
                'tax_rate': self.defaults_tax_rate.value(),
                'payment_days': self.defaults_payment_days.value(),
                'language': self.defaults_language.currentText(),
            },
            'typography': {
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
            },
            'colors': {
                'primary': self.color_primary.color(),
                'accent': self.color_accent.color(),
                'background': self.color_background.color(),
                'text': self.color_text.color(),
                'muted': self.color_muted.color(),
                'border': self.color_border.color(),
                'table_alt': self.color_table_alt.color(),
            }
        }
    
    def _save_config(self):
        """Save the configuration to the YAML file."""
        new_config = self._gather_values()
        
        try:
            # Generate YAML with nice formatting
            yaml_content = self._generate_yaml(new_config)
            
            # Write to file
            with open(self.config_loader.config_path, 'w', encoding='utf-8') as f:
                f.write(yaml_content)
            
            # Update the config loader's config
            self.config_loader.config = new_config
            
            self.configSaved.emit()
            QMessageBox.information(self, "Success", "Configuration saved successfully!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration:\n{e}")
    
    def _generate_yaml(self, config: dict) -> str:
        """Generate formatted YAML with section comments."""
        lines = [
            "# MD2Angebot User Configuration",
            f"# Config path: {self.config_loader.config_path}",
            "",
            "# ==========================================",
            "# COMPANY INFORMATION",
            "# ==========================================",
        ]
        
        lines.append(yaml.dump({'company': config['company']}, allow_unicode=True, sort_keys=False).strip())
        lines.append("")
        lines.append(yaml.dump({'quote_types': config['quote_types']}, allow_unicode=True, sort_keys=False).strip())
        
        lines.extend([
            "",
            "# ==========================================",
            "# CONTACT DETAILS",
            "# ==========================================",
        ])
        lines.append(yaml.dump({'contact': config['contact']}, allow_unicode=True, sort_keys=False).strip())
        
        lines.extend([
            "",
            "# ==========================================",
            "# LEGAL INFORMATION",
            "# ==========================================",
        ])
        lines.append(yaml.dump({'legal': config['legal']}, allow_unicode=True, sort_keys=False).strip())
        
        lines.extend([
            "",
            "# ==========================================",
            "# BANKING DETAILS",
            "# ==========================================",
        ])
        lines.append(yaml.dump({'bank': config['bank']}, allow_unicode=True, sort_keys=False).strip())
        
        lines.extend([
            "",
            "# ==========================================",
            "# DEFAULTS",
            "# ==========================================",
        ])
        lines.append(yaml.dump({'defaults': config['defaults']}, allow_unicode=True, sort_keys=False).strip())
        
        lines.extend([
            "",
            "# ==========================================",
            "# TYPOGRAPHY",
            "# ==========================================",
        ])
        lines.append(yaml.dump({'typography': config['typography']}, allow_unicode=True, sort_keys=False).strip())
        
        lines.extend([
            "",
            "# ==========================================",
            "# COLOR SCHEME",
            "# ==========================================",
        ])
        lines.append(yaml.dump({'colors': config['colors']}, allow_unicode=True, sort_keys=False).strip())
        lines.append("")
        
        return "\n".join(lines)

