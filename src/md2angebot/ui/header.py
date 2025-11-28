from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QLineEdit, QDateEdit, QTextEdit, QSizePolicy, QFrame, QLabel, QGridLayout)
from PyQt6.QtCore import QDate, pyqtSignal, Qt

class HeaderWidget(QWidget):
    dataChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self.init_ui()

    def init_ui(self):
        # Use a horizontal layout to split Quote Info and Client Info
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(15)

        # --- Quote Info Section (Left) ---
        quote_layout = QFormLayout()
        quote_layout.setContentsMargins(0, 0, 0, 0)
        quote_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.FieldsStayAtSizeHint)
        
        self.quote_number_edit = QLineEdit()
        self.quote_number_edit.setPlaceholderText("e.g. 2023-001")
        self.quote_number_edit.setFixedWidth(120)
        self.quote_number_edit.textChanged.connect(self.on_changed)
        quote_layout.addRow("Quotation #:", self.quote_number_edit)

        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setFixedWidth(120)
        self.date_edit.dateChanged.connect(self.on_changed)
        quote_layout.addRow("Date:", self.date_edit)

        main_layout.addLayout(quote_layout)
        
        # Vertical divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line)

        # --- Client Info Section (Right) ---
        client_layout = QGridLayout()
        client_layout.setContentsMargins(0, 0, 0, 0)
        client_layout.setVerticalSpacing(5)
        client_layout.setHorizontalSpacing(10)

        # Row 0: Name | Email
        client_layout.addWidget(QLabel("Client Name:"), 0, 0)
        self.receiver_name = QLineEdit()
        self.receiver_name.setPlaceholderText("Client Name")
        self.receiver_name.textChanged.connect(self.on_changed)
        client_layout.addWidget(self.receiver_name, 0, 1)

        client_layout.addWidget(QLabel("Email:"), 0, 2)
        self.receiver_email = QLineEdit()
        self.receiver_email.setPlaceholderText("client@example.com")
        self.receiver_email.textChanged.connect(self.on_changed)
        client_layout.addWidget(self.receiver_email, 0, 3)
        
        # Row 1: Address (Label | TextEdit)
        client_layout.addWidget(QLabel("Address:"), 1, 0)
        self.receiver_address = QTextEdit()
        self.receiver_address.setPlaceholderText("Street, City, Zip...")
        self.receiver_address.setMaximumHeight(45) # Compact height ~2 lines
        self.receiver_address.setTabChangesFocus(True)
        self.receiver_address.textChanged.connect(self.on_changed)
        # Span columns 1-3
        client_layout.addWidget(self.receiver_address, 1, 1, 1, 3) 

        # Add client layout with stretch
        main_layout.addLayout(client_layout)
        main_layout.setStretchFactor(client_layout, 1)

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
                pass # Keep default or existing if parse fails

        # Client
        if "name" in client:
            self.receiver_name.setText(str(client["name"]))
        if "email" in client:
            self.receiver_email.setText(str(client["email"]))
        if "address" in client:
            self.receiver_address.setPlainText(str(client["address"]))

        self.blockSignals(False)
