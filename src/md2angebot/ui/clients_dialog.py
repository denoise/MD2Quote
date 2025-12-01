"""
Clients Manager Dialog for MD2Angebot.

A dialog for managing saved client information (CRUD operations).
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget,
    QLabel, QLineEdit, QPushButton, QListWidget,
    QListWidgetItem, QMessageBox, QSplitter, QFrame,
    QGridLayout, QTextEdit, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from .styles import COLORS, SPACING
from .icons import icon


class ClientsManagerDialog(QDialog):
    """Dialog for managing saved clients."""
    
    clientSelected = pyqtSignal(dict)  # Emits selected client data
    clientsChanged = pyqtSignal()  # Emits when clients list is modified
    
    def __init__(self, config_loader, parent=None):
        super().__init__(parent)
        self.config = config_loader
        self._current_client_key = None
        self._is_modified = False
        
        self.setWindowTitle("Manage Clients")
        self.resize(900, 500)
        self.setModal(True)
        
        self._setup_ui()
        self._load_clients()
        self._update_button_states()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(SPACING['md'])
        layout.setContentsMargins(SPACING['md'], SPACING['md'], SPACING['md'], SPACING['md'])
        
        # Main content with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel: Client list
        left_panel = QFrame()
        left_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_elevated']};
                border: 1px solid {COLORS['border']};
            }}
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(SPACING['sm'], SPACING['sm'], SPACING['sm'], SPACING['sm'])
        left_layout.setSpacing(SPACING['sm'])
        
        list_label = QLabel("Saved Clients")
        list_label.setStyleSheet(f"""
            color: {COLORS['accent']};
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
        """)
        left_layout.addWidget(list_label)
        
        self.clients_list = QListWidget()
        self.clients_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {COLORS['bg_dark']};
                border: 1px solid {COLORS['border']};
                color: {COLORS['text_primary']};
                font-size: 13px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {COLORS['border']};
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['accent']};
                color: {COLORS['bg_dark']};
            }}
            QListWidget::item:hover:!selected {{
                background-color: {COLORS['bg_hover']};
            }}
        """)
        self.clients_list.currentItemChanged.connect(self._on_client_selected)
        self.clients_list.itemDoubleClicked.connect(self._on_client_double_clicked)
        left_layout.addWidget(self.clients_list)
        
        # List action buttons
        list_buttons = QHBoxLayout()
        list_buttons.setSpacing(SPACING['xs'])
        
        self.new_btn = QPushButton("New")
        self.new_btn.setIcon(icon('add_circle', 14, COLORS['text_secondary']))
        self.new_btn.clicked.connect(self._on_new_client)
        self._style_button(self.new_btn)
        list_buttons.addWidget(self.new_btn)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setIcon(icon('delete', 14, COLORS['text_secondary']))
        self.delete_btn.clicked.connect(self._on_delete_client)
        self._style_button(self.delete_btn)
        list_buttons.addWidget(self.delete_btn)
        
        list_buttons.addStretch()
        left_layout.addLayout(list_buttons)
        
        splitter.addWidget(left_panel)
        
        # Right panel: Client form
        right_panel = QFrame()
        right_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_elevated']};
                border: 1px solid {COLORS['border']};
            }}
        """)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(SPACING['sm'], SPACING['sm'], SPACING['sm'], SPACING['sm'])
        right_layout.setSpacing(SPACING['sm'])
        
        form_label = QLabel("Client Details")
        form_label.setStyleSheet(f"""
            color: {COLORS['accent']};
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
        """)
        right_layout.addWidget(form_label)
        
        # Form fields
        form_grid = QGridLayout()
        form_grid.setHorizontalSpacing(SPACING['sm'])
        form_grid.setVerticalSpacing(SPACING['sm'])
        
        # Contact field
        contact_label = self._create_label("Contact")
        form_grid.addWidget(contact_label, 0, 0, Qt.AlignmentFlag.AlignTop)
        
        self.contact_edit = QTextEdit()
        self.contact_edit.setPlaceholderText("Name, title, department (1-3 lines)")
        self.contact_edit.setMaximumHeight(60)
        self.contact_edit.setTabChangesFocus(True)
        self.contact_edit.textChanged.connect(self._on_form_changed)
        self._style_text_edit(self.contact_edit)
        form_grid.addWidget(self.contact_edit, 0, 1)
        
        # Institution field
        institution_label = self._create_label("Institution")
        form_grid.addWidget(institution_label, 1, 0)
        
        self.institution_edit = QLineEdit()
        self.institution_edit.setPlaceholderText("Company or institution name (required)")
        self.institution_edit.textChanged.connect(self._on_form_changed)
        self._style_line_edit(self.institution_edit)
        form_grid.addWidget(self.institution_edit, 1, 1)
        
        # Email field
        email_label = self._create_label("Email")
        form_grid.addWidget(email_label, 2, 0)
        
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("client@example.com")
        self.email_edit.textChanged.connect(self._on_form_changed)
        self._style_line_edit(self.email_edit)
        form_grid.addWidget(self.email_edit, 2, 1)
        
        # Address field
        address_label = self._create_label("Address")
        form_grid.addWidget(address_label, 3, 0, Qt.AlignmentFlag.AlignTop)
        
        self.address_edit = QTextEdit()
        self.address_edit.setPlaceholderText("Street, City, Postal Code...")
        self.address_edit.setMaximumHeight(80)
        self.address_edit.setTabChangesFocus(True)
        self.address_edit.textChanged.connect(self._on_form_changed)
        self._style_text_edit(self.address_edit)
        form_grid.addWidget(self.address_edit, 3, 1)
        
        form_grid.setColumnStretch(1, 1)
        right_layout.addLayout(form_grid)
        
        # Form action buttons
        form_buttons = QHBoxLayout()
        form_buttons.setSpacing(SPACING['sm'])
        
        self.save_btn = QPushButton("Save")
        self.save_btn.setIcon(icon('save', 14, COLORS['bg_dark']))
        self.save_btn.clicked.connect(self._on_save_client)
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: {COLORS['bg_dark']};
                border: none;
                padding: 6px 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent_hover']};
            }}
            QPushButton:disabled {{
                background-color: {COLORS['bg_hover']};
                color: {COLORS['text_muted']};
            }}
        """)
        form_buttons.addWidget(self.save_btn)
        
        form_buttons.addStretch()
        
        self.use_btn = QPushButton("Use Client")
        self.use_btn.setIcon(icon('check_circle', 14, COLORS['text_secondary']))
        self.use_btn.clicked.connect(self._on_use_client)
        self._style_button(self.use_btn)
        form_buttons.addWidget(self.use_btn)
        
        right_layout.addLayout(form_buttons)
        right_layout.addStretch()
        
        splitter.addWidget(right_panel)
        
        # Set splitter sizes
        splitter.setSizes([300, 450])
        layout.addWidget(splitter)
        
        # Bottom buttons
        bottom_buttons = QHBoxLayout()
        bottom_buttons.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        self._style_button(close_btn)
        bottom_buttons.addWidget(close_btn)
        
        layout.addLayout(bottom_buttons)
        
        # Apply dialog styling
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_base']};
            }}
        """)
    
    def _create_label(self, text: str) -> QLabel:
        """Creates a styled field label."""
        label = QLabel(text)
        label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 12px;
            font-weight: 500;
            min-width: 60px;
        """)
        return label
    
    def _style_button(self, button: QPushButton):
        """Apply standard button styling."""
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_elevated']};
                border: 1px solid {COLORS['border']};
                color: {COLORS['text_primary']};
                padding: 6px 12px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_hover']};
                border-color: {COLORS['text_muted']};
            }}
            QPushButton:disabled {{
                color: {COLORS['text_muted']};
            }}
        """)
    
    def _style_line_edit(self, edit: QLineEdit):
        """Apply standard line edit styling."""
        edit.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['bg_dark']};
                border: 1px solid {COLORS['border']};
                color: {COLORS['text_primary']};
                padding: 6px 8px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['accent']};
            }}
        """)
    
    def _style_text_edit(self, edit: QTextEdit):
        """Apply standard text edit styling."""
        edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['bg_dark']};
                border: 1px solid {COLORS['border']};
                color: {COLORS['text_primary']};
                padding: 4px 6px;
                font-size: 13px;
            }}
            QTextEdit:focus {{
                border-color: {COLORS['accent']};
            }}
        """)
    
    def _load_clients(self):
        """Load clients from config into the list."""
        self.clients_list.clear()
        clients = self.config.get_clients_list()
        for client_key, institution in clients:
            item = QListWidgetItem(institution or "(No institution)")
            item.setData(Qt.ItemDataRole.UserRole, client_key)
            self.clients_list.addItem(item)
    
    def _clear_form(self):
        """Clear all form fields."""
        self.contact_edit.blockSignals(True)
        self.institution_edit.blockSignals(True)
        self.email_edit.blockSignals(True)
        self.address_edit.blockSignals(True)
        
        self.contact_edit.clear()
        self.institution_edit.clear()
        self.email_edit.clear()
        self.address_edit.clear()
        
        self.contact_edit.blockSignals(False)
        self.institution_edit.blockSignals(False)
        self.email_edit.blockSignals(False)
        self.address_edit.blockSignals(False)
        
        self._current_client_key = None
        self._is_modified = False
    
    def _load_client_to_form(self, client_key: str):
        """Load a client's data into the form."""
        client = self.config.get_client(client_key)
        if not client:
            return
        
        self.contact_edit.blockSignals(True)
        self.institution_edit.blockSignals(True)
        self.email_edit.blockSignals(True)
        self.address_edit.blockSignals(True)
        
        self.contact_edit.setPlainText(client.get('contact', ''))
        self.institution_edit.setText(client.get('institution', ''))
        self.email_edit.setText(client.get('email', ''))
        self.address_edit.setPlainText(client.get('address', ''))
        
        self.contact_edit.blockSignals(False)
        self.institution_edit.blockSignals(False)
        self.email_edit.blockSignals(False)
        self.address_edit.blockSignals(False)
        
        self._current_client_key = client_key
        self._is_modified = False
    
    def _get_form_data(self) -> dict:
        """Get current form data as a dictionary."""
        return {
            'contact': self.contact_edit.toPlainText(),
            'institution': self.institution_edit.text(),
            'email': self.email_edit.text(),
            'address': self.address_edit.toPlainText()
        }
    
    def _update_button_states(self):
        """Update enabled state of buttons based on current selection."""
        has_selection = self._current_client_key is not None
        has_institution = bool(self.institution_edit.text().strip())
        
        self.delete_btn.setEnabled(has_selection)
        self.save_btn.setEnabled(has_institution and self._is_modified)
        self.use_btn.setEnabled(has_selection or has_institution)
    
    def _on_client_selected(self, current: QListWidgetItem, previous: QListWidgetItem):
        """Handle client selection in list."""
        if self._is_modified:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Discard them?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                self.clients_list.blockSignals(True)
                self.clients_list.setCurrentItem(previous)
                self.clients_list.blockSignals(False)
                return
        
        if current:
            client_key = current.data(Qt.ItemDataRole.UserRole)
            self._load_client_to_form(client_key)
        else:
            self._clear_form()
        
        self._update_button_states()
    
    def _on_client_double_clicked(self, item: QListWidgetItem):
        """Handle double-click on client (use client)."""
        self._on_use_client()
    
    def _on_form_changed(self):
        """Handle form field changes."""
        self._is_modified = True
        self._update_button_states()
    
    def _on_new_client(self):
        """Create a new client entry."""
        if self._is_modified:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Discard them?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        self.clients_list.clearSelection()
        self._clear_form()
        self.institution_edit.setFocus()
        self._update_button_states()
    
    def _on_save_client(self):
        """Save the current client."""
        data = self._get_form_data()
        
        if not data['institution'].strip():
            QMessageBox.warning(
                self,
                "Validation Error",
                "Institution is required."
            )
            self.institution_edit.setFocus()
            return
        
        if self._current_client_key:
            # Update existing client
            success, error = self.config.update_client(self._current_client_key, data)
            if not success:
                QMessageBox.critical(self, "Error", f"Failed to update client: {error}")
                return
        else:
            # Add new client
            new_key, error = self.config.add_client(data)
            if not new_key:
                QMessageBox.critical(self, "Error", f"Failed to add client: {error}")
                return
            self._current_client_key = new_key
        
        self._is_modified = False
        self._load_clients()
        
        # Re-select the current client
        for i in range(self.clients_list.count()):
            item = self.clients_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == self._current_client_key:
                self.clients_list.setCurrentItem(item)
                break
        
        self._update_button_states()
        self.clientsChanged.emit()
    
    def _on_delete_client(self):
        """Delete the selected client."""
        if not self._current_client_key:
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete client '{self.institution_edit.text()}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        success, error = self.config.delete_client(self._current_client_key)
        if not success:
            QMessageBox.critical(self, "Error", f"Failed to delete client: {error}")
            return
        
        self._clear_form()
        self._load_clients()
        self._update_button_states()
        self.clientsChanged.emit()
    
    def _on_use_client(self):
        """Use the current client data (emit and close)."""
        data = self._get_form_data()
        
        if not data['institution'].strip():
            QMessageBox.warning(
                self,
                "Validation Error",
                "Institution is required to use this client."
            )
            return
        
        # If modified, offer to save first
        if self._is_modified:
            reply = QMessageBox.question(
                self,
                "Save Changes?",
                "Save changes before using this client?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Cancel:
                return
            if reply == QMessageBox.StandardButton.Yes:
                self._on_save_client()
        
        self.clientSelected.emit(data)
        self.accept()

