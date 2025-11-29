from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QLineEdit, QDateEdit, QTextEdit, QSizePolicy, QFrame, QLabel, QGridLayout)
from PyQt6.QtCore import QDate, pyqtSignal, Qt
from .styles import COLORS, SPACING, RADIUS


class SectionCard(QFrame):
    """A styled card container for form sections."""
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("header-section")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING['sm'], SPACING['sm'], SPACING['sm'], SPACING['sm'])
        layout.setSpacing(SPACING['xs'])
        
        # Section title
        title_label = QLabel(title)
        title_label.setObjectName("header-title")
        title_label.setStyleSheet(f"""
            color: {COLORS['accent']};
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 0;
            margin-bottom: 2px;
        """)
        layout.addWidget(title_label)
        
        # Content area
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(SPACING['xs'])
        layout.addLayout(self.content_layout)
        
        self.setStyleSheet(f"""
            SectionCard {{
                background-color: {COLORS['bg_elevated']};
                border-radius: 0;
                border: 1px solid {COLORS['border']};
            }}
        """)


class ModernLineEdit(QLineEdit):
    """A styled line edit with floating label appearance."""
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(24)


class ModernTextEdit(QTextEdit):
    """A styled multiline text edit."""
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMaximumHeight(48)
        self.setTabChangesFocus(True)


class HeaderWidget(QWidget):
    dataChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self.setObjectName("header-widget")
        self.init_ui()

    def init_ui(self):
        # Main horizontal layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(SPACING['sm'], SPACING['sm'], SPACING['sm'], SPACING['sm'])
        main_layout.setSpacing(SPACING['sm'])

        # === Quotation Section (Left) ===
        quote_card = SectionCard("Quotation")
        quote_grid = QGridLayout()
        quote_grid.setContentsMargins(0, 0, 0, 0)
        quote_grid.setHorizontalSpacing(SPACING['sm'])
        quote_grid.setVerticalSpacing(SPACING['xs'])
        
        # Number field
        number_label = self._create_label("Number")
        quote_grid.addWidget(number_label, 0, 0)
        
        self.quote_number_edit = ModernLineEdit("e.g. 2025-001")
        self.quote_number_edit.setMaximumWidth(140)
        self.quote_number_edit.textChanged.connect(self.on_changed)
        quote_grid.addWidget(self.quote_number_edit, 0, 1)

        # Date field
        date_label = self._create_label("Date")
        quote_grid.addWidget(date_label, 1, 0)
        
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setMaximumWidth(120)
        self.date_edit.setMinimumHeight(24)
        self.date_edit.dateChanged.connect(self.on_changed)
        quote_grid.addWidget(self.date_edit, 1, 1)
        
        quote_card.content_layout.addLayout(quote_grid)
        main_layout.addWidget(quote_card)

        # === Client Section (Right, takes more space) ===
        client_card = SectionCard("Client")
        client_grid = QGridLayout()
        client_grid.setContentsMargins(0, 0, 0, 0)
        client_grid.setHorizontalSpacing(SPACING['sm'])
        client_grid.setVerticalSpacing(SPACING['xs'])

        # Row 0: Name and Email
        name_label = self._create_label("Name")
        client_grid.addWidget(name_label, 0, 0)
        
        self.receiver_name = ModernLineEdit("Company or contact name")
        self.receiver_name.textChanged.connect(self.on_changed)
        client_grid.addWidget(self.receiver_name, 0, 1)

        email_label = self._create_label("Email")
        client_grid.addWidget(email_label, 0, 2)
        
        self.receiver_email = ModernLineEdit("client@example.com")
        self.receiver_email.textChanged.connect(self.on_changed)
        client_grid.addWidget(self.receiver_email, 0, 3)
        
        # Row 1: Address (spanning multiple columns)
        address_label = self._create_label("Address")
        client_grid.addWidget(address_label, 1, 0, Qt.AlignmentFlag.AlignTop)
        
        self.receiver_address = ModernTextEdit("Street, City, Postal Code...")
        self.receiver_address.textChanged.connect(self.on_changed)
        client_grid.addWidget(self.receiver_address, 1, 1, 1, 3)
        
        # Set column stretch
        client_grid.setColumnStretch(1, 1)
        client_grid.setColumnStretch(3, 1)

        client_card.content_layout.addLayout(client_grid)
        main_layout.addWidget(client_card, stretch=2)

    def _create_label(self, text: str) -> QLabel:
        """Creates a styled field label."""
        label = QLabel(text)
        label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 12px;
            font-weight: 500;
            padding: 0;
            min-width: 40px;
        """)
        return label

    def on_changed(self):
        self.dataChanged.emit()

    def get_data(self):
        """Returns a dictionary with the header data."""
        return {
            "quotation": {
                "number": self.quote_number_edit.text(),
                "date": self.date_edit.date().toString("yyyy-MM-dd"),
            },
            "client": {
                "name": self.receiver_name.text(),
                "email": self.receiver_email.text(),
                "address": self.receiver_address.toPlainText()
            }
        }

    def set_data(self, data):
        """Populates fields from a dictionary (e.g. parsed metadata)."""
        self.blockSignals(True)
        
        quotation = data.get("quotation", {})
        client = data.get("client", {})

        # Quotation
        if "number" in quotation:
            self.quote_number_edit.setText(str(quotation["number"]))
        
        if "date" in quotation:
            try:
                qdate = QDate.fromString(str(quotation["date"]), "yyyy-MM-dd")
                if qdate.isValid():
                    self.date_edit.setDate(qdate)
            except:
                pass

        # Client
        if "name" in client:
            self.receiver_name.setText(str(client["name"]))
        if "email" in client:
            self.receiver_email.setText(str(client["email"]))
        if "address" in client:
            self.receiver_address.setPlainText(str(client["address"]))

        self.blockSignals(False)
