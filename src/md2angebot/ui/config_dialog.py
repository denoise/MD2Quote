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
    QListWidgetItem, QInputDialog, QButtonGroup, QPlainTextEdit, QCheckBox,
    QSlider
)
from PyQt6.QtGui import QColor, QPalette, QFont, QIcon
from PyQt6.QtCore import Qt, pyqtSignal

from .styles import COLORS, SPACING, RADIUS
from .icons import icon, icon_font, icon_char


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


class SectionCard(QFrame):
    """A card container for grouping related settings."""
    
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("section-card")
        
        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(SPACING['sm'])
        self._layout.setContentsMargins(SPACING['md'], SPACING['md'], SPACING['md'], SPACING['md'])
        
        if title:
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
    
    def addWidget(self, widget):
        # Insert before the stretch (which is always the last item)
        self._layout.insertWidget(self._layout.count() - 1, widget)
    
    def addLayout(self, layout):
        # Insert before the stretch (which is always the last item)
        self._layout.insertLayout(self._layout.count() - 1, layout)


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
        lbl.setFixedWidth(100)
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
        self.setMinimumHeight(24)
        if items:
            self.addItems(items)
        self.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['bg_dark']};
                border: 1px solid {COLORS['border']};
                border-radius: 0;
                color: {COLORS['text_primary']};
                padding: 2px 6px;
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
                width: 22px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {COLORS['text_secondary']};
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
            spin.setMinimumWidth(90)
        
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
    
    def __init__(self, config_loader, parent=None):
        super().__init__(parent)
        self.config_loader = config_loader
        # Deep copy config so we can modify freely
        self.config = copy.deepcopy(config_loader.config)
        
        # Track which preset we are currently editing
        self.current_preset_key = self.config.get('active_preset', 'preset_1')
        
        self.setWindowTitle("Configuration Assistant")
        self.setMinimumSize(1000, 620)
        self.resize(1100, 680)
        
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
                color: {COLORS['text_primary']};
                border-bottom: 1px solid {COLORS['bg_dark']};
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
        """)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(SPACING['md'])
        layout.setContentsMargins(SPACING['lg'], SPACING['lg'], SPACING['lg'], SPACING['lg'])
        
        # Title
        title_container = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        
        title = QLabel("Configuration Assistant")
        title.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 600;
            color: {COLORS['text_primary']};
        """)
        title_col.addWidget(title)
        
        subtitle = QLabel("Manage your sender presets and document settings")
        subtitle.setStyleSheet(f"""
            color: {COLORS['text_muted']};
            font-size: 13px;
        """)
        title_col.addWidget(subtitle)
        
        title_container.addLayout(title_col)
        title_container.addStretch()
        layout.addLayout(title_container)
        
        # Preset Selector Bar
        preset_card = SectionCard()
        preset_card.setStyleSheet(f"""
            QFrame#section-card {{
                background-color: {COLORS['bg_dark']};
                border: 1px solid {COLORS['border']};
                border-radius: 0;
                padding: {SPACING['sm']}px;
            }}
        """)
        
        preset_inner_layout = QVBoxLayout()
        preset_inner_layout.setSpacing(SPACING['sm'])
        
        # Preset buttons row
        preset_btn_layout = QHBoxLayout()
        preset_btn_layout.setSpacing(SPACING['xs'])
        
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
            btn.setFixedHeight(28)
            btn.setMinimumWidth(100)
            
            if key == self.current_preset_key:
                btn.setChecked(True)
                
            self.preset_group.addButton(btn)
            preset_btn_layout.addWidget(btn)
        
        preset_card.addLayout(preset_btn_layout)
        
        # Preset name input row
        name_row = QHBoxLayout()
        name_row.setSpacing(SPACING['sm'])
        
        name_label = QLabel("Preset Name:")
        name_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: 500; font-size: 12px;")
        name_row.addWidget(name_label)
        
        self.preset_name_edit = QLineEdit()
        self.preset_name_edit.setPlaceholderText("e.g. Company A, Freelance, Private")
        self.preset_name_edit.setMinimumHeight(24)
        self.preset_name_edit.textChanged.connect(self._update_preset_button_text)
        name_row.addWidget(self.preset_name_edit, 1)
        
        preset_card.addLayout(name_row)
        layout.addWidget(preset_card)
        
        # Tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs, 1)
        
        # Create tabs with Material icons
        self.tabs.addTab(self._create_identity_tab(), icon('badge', 18, COLORS['text_secondary']), "Identity")
        self.tabs.addTab(self._create_document_tab(), icon('article', 18, COLORS['text_secondary']), "Document")
        self.tabs.addTab(self._create_styling_tab(), icon('palette', 18, COLORS['text_secondary']), "Styling")
        self.tabs.addTab(self._create_defaults_tab(), icon('tune', 18, COLORS['text_secondary']), "Defaults")
        
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
        
        # Style for preset buttons
        self.setStyleSheet(self.styleSheet() + f"""
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
        
        self.company_name = QLineEdit()
        self.company_name.setPlaceholderText("Your Company Name")
        self.company_name.setMinimumHeight(24)
        company_card.addWidget(FormRow("Name", self.company_name))
        
        self.company_tagline = QLineEdit()
        self.company_tagline.setPlaceholderText("Your tagline or slogan")
        self.company_tagline.setMinimumHeight(24)
        company_card.addWidget(FormRow("Tagline", self.company_tagline))
        
        self.company_logo = PathSelector("Images (*.svg *.png *.jpg *.jpeg)")
        company_card.addWidget(FormRow("Logo", self.company_logo))
        
        left_col.addWidget(company_card)
        
        # Contact Card
        contact_card = SectionCard("Contact Details")
        
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
        self.contact_postal.setMaximumWidth(100)
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
        
        # Legal Card
        legal_card = SectionCard("Legal Information")
        
        self.legal_tax_id = QLineEdit()
        self.legal_tax_id.setPlaceholderText("VAT / Tax ID")
        self.legal_tax_id.setMinimumHeight(24)
        legal_card.addWidget(FormRow("Tax ID", self.legal_tax_id))
        
        self.legal_kvk = QLineEdit()
        self.legal_kvk.setPlaceholderText("Chamber of Commerce Number")
        self.legal_kvk.setMinimumHeight(24)
        legal_card.addWidget(FormRow("CoC Number", self.legal_kvk))
        
        right_col.addWidget(legal_card)
        
        # Bank Card
        bank_card = SectionCard("Banking Details")
        
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
        
        # Template Selection Card
        template_card = SectionCard("Layout Template")
        
        self.layout_template = QComboBox()
        self.layout_template.setMinimumHeight(24)
        self.layout_template.addItem("Modern Split (Default)", "modern-split")
        self.layout_template.addItem("Elegant Centered (Photography)", "elegant-centered")
        self.layout_template.addItem("Minimal Sidebar (Consulting)", "minimal-sidebar")
        self.layout_template.addItem("Bold Stamp (Creative)", "bold-stamp")
        self.layout_template.addItem("Classic Letterhead (Business)", "classic-letterhead")
        template_card.addWidget(FormRow("Template", self.layout_template))
        
        layout.addWidget(template_card)
        
        # Page Margins Card
        margins_card = SectionCard("Page Margins")
        
        self.margin_control = MarginControl()
        margins_card.addWidget(self.margin_control)
        
        layout.addWidget(margins_card)
        
        # Snippets Card
        snippets_card = SectionCard("Content Snippets")
        
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
        self.defaults_currency = QLineEdit()
        self.defaults_currency.setPlaceholderText("EUR")
        self.defaults_currency.setMinimumHeight(24)
        self.defaults_currency.setMaximumWidth(80)
        currency_col.addWidget(self.defaults_currency)
        row1.addLayout(currency_col)
        
        lang_col = QVBoxLayout()
        lang_col.setSpacing(2)
        lang_label = QLabel("Language")
        lang_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: 500; font-size: 12px;")
        lang_col.addWidget(lang_label)
        self.defaults_language = QComboBox()
        self.defaults_language.addItems(["de", "en", "nl", "fr", "es"])
        self.defaults_language.setMinimumHeight(24)
        self.defaults_language.setMinimumWidth(80)
        lang_col.addWidget(self.defaults_language)
        row1.addLayout(lang_col)
        
        row1.addStretch()
        defaults_card.addLayout(row1)
        
        # Tax + Payment row
        row2 = QHBoxLayout()
        row2.setSpacing(SPACING['md'])
        
        tax_col = QVBoxLayout()
        tax_col.setSpacing(2)
        tax_label = QLabel("Tax Rate")
        tax_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: 500; font-size: 12px;")
        tax_col.addWidget(tax_label)
        self.defaults_tax_rate = StyledSpinBox()
        self.defaults_tax_rate.setRange(0, 100)
        self.defaults_tax_rate.setSuffix(" %")
        self.defaults_tax_rate.setMinimumWidth(80)
        tax_col.addWidget(self.defaults_tax_rate)
        row2.addLayout(tax_col)
        
        payment_col = QVBoxLayout()
        payment_col.setSpacing(2)
        payment_label = QLabel("Payment Terms")
        payment_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: 500; font-size: 12px;")
        payment_col.addWidget(payment_label)
        self.defaults_payment_days = StyledSpinBox()
        self.defaults_payment_days.setRange(1, 365)
        self.defaults_payment_days.setSuffix(" days")
        self.defaults_payment_days.setMinimumWidth(100)
        payment_col.addWidget(self.defaults_payment_days)
        row2.addLayout(payment_col)
        
        row2.addStretch()
        defaults_card.addLayout(row2)
        
        left_col.addWidget(defaults_card)
        
        columns.addLayout(left_col, 1)
        
        # Right column - Quotation Number
        right_col = QVBoxLayout()
        right_col.setSpacing(SPACING['sm'])
        
        qn_card = SectionCard("Quotation Numbering")
        
        self.qn_enabled = QCheckBox("Enable automatic quotation numbering")
        qn_card.addWidget(self.qn_enabled)
        
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
        reset_counter_btn.setMinimumWidth(90)
        reset_counter_btn.clicked.connect(self._reset_qn_counter)
        counter_row.addWidget(reset_counter_btn)
        
        qn_card.addLayout(counter_row)
        
        right_col.addWidget(qn_card)
        
        columns.addLayout(right_col, 1)
        
        layout.addLayout(columns, 1)
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
            'page_margins': self.margin_control.values()
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
        self.margin_control.setValues(margins)
            
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
            dumped = yaml.dump({key: preset}, allow_unicode=True, sort_keys=False)
            lines.append(self._indent_text(dumped, 2))
            lines.append("")
            
        return "\n".join(lines)

    def _indent_text(self, text: str, spaces: int) -> str:
        indent = " " * spaces
        return "\n".join(indent + line if line else line for line in text.splitlines())
