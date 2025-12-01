from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QTextEdit, QSizePolicy, QFrame, QLabel, QGridLayout,
                             QPushButton, QCalendarWidget, QMenu, QWidgetAction,
                             QPlainTextEdit)
from PyQt6.QtCore import QDate, pyqtSignal, Qt, QPoint
from PyQt6.QtGui import QTextCharFormat, QColor, QKeyEvent
from .styles import COLORS, SPACING
from .icons import icon


class ModernDatePicker(QWidget):
    """A modern, styled date picker that fits the dark theme aesthetic."""
    
    dateChanged = pyqtSignal(QDate)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._date = QDate.currentDate()
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Date display button
        self.date_button = QPushButton()
        self.date_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.date_button.clicked.connect(self._show_calendar)
        self.date_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_elevated']};
                border: 1px solid {COLORS['border']};
                border-radius: 0;
                color: {COLORS['text_primary']};
                padding: 4px 8px;
                min-height: 24px;
                font-size: 13px;
                font-weight: 500;
                text-align: left;
            }}
            QPushButton:hover {{
                border-color: {COLORS['text_muted']};
                background-color: {COLORS['bg_hover']};
            }}
            QPushButton:focus {{
                border-color: {COLORS['accent']};
            }}
        """)
        layout.addWidget(self.date_button)
        
        # Calendar icon button
        self.cal_icon_btn = QPushButton()
        self.cal_icon_btn.setIcon(icon('calendar_today', 16, COLORS['text_secondary']))
        self.cal_icon_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cal_icon_btn.clicked.connect(self._show_calendar)
        self.cal_icon_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_elevated']};
                border: 1px solid {COLORS['border']};
                border-left: none;
                border-radius: 0;
                padding: 4px 6px;
                min-height: 24px;
                min-width: 24px;
            }}
            QPushButton:hover {{
                border-color: {COLORS['text_muted']};
                background-color: {COLORS['bg_hover']};
            }}
        """)
        layout.addWidget(self.cal_icon_btn)
        
        # Create the calendar popup
        self._create_calendar_popup()
        self._update_display()
        
    def _create_calendar_popup(self):
        """Create the styled calendar popup menu."""
        self.calendar_menu = QMenu(self)
        self.calendar_menu.setStyleSheet(f"""
            QMenu {{
                background-color: {COLORS['bg_elevated']};
                border: 1px solid {COLORS['border']};
                padding: 0;
            }}
        """)
        
        # Calendar widget
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(False)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.calendar.setHorizontalHeaderFormat(QCalendarWidget.HorizontalHeaderFormat.ShortDayNames)
        self.calendar.setFirstDayOfWeek(Qt.DayOfWeek.Monday)
        self.calendar.clicked.connect(self._on_date_selected)
        self.calendar.activated.connect(self._on_date_selected)
        
        # Style the calendar to match the app theme
        self.calendar.setStyleSheet(f"""
            QCalendarWidget {{
                background-color: {COLORS['bg_elevated']};
                border: none;
            }}
            
            QCalendarWidget QWidget {{
                alternate-background-color: {COLORS['bg_base']};
            }}
            
            /* Navigation bar */
            QCalendarWidget QWidget#qt_calendar_navigationbar {{
                background-color: {COLORS['bg_base']};
                padding: 4px;
            }}
            
            /* Month/Year buttons */
            QCalendarWidget QToolButton {{
                color: {COLORS['text_primary']};
                background-color: transparent;
                border: none;
                border-radius: 0;
                padding: 4px 8px;
                font-size: 13px;
                font-weight: 600;
            }}
            
            QCalendarWidget QToolButton:hover {{
                background-color: {COLORS['bg_hover']};
                color: {COLORS['accent']};
            }}
            
            QCalendarWidget QToolButton:pressed {{
                background-color: {COLORS['bg_base']};
            }}
            
            /* Navigation arrows */
            QCalendarWidget QToolButton#qt_calendar_prevmonth {{
                qproperty-icon: none;
                min-width: 24px;
            }}
            
            QCalendarWidget QToolButton#qt_calendar_nextmonth {{
                qproperty-icon: none;
                min-width: 24px;
            }}
            
            QCalendarWidget QToolButton#qt_calendar_prevmonth::after {{
                content: "◀";
            }}
            
            /* Month/Year dropdown menu */
            QCalendarWidget QMenu {{
                background-color: {COLORS['bg_elevated']};
                border: 1px solid {COLORS['border']};
                color: {COLORS['text_primary']};
            }}
            
            QCalendarWidget QMenu::item {{
                padding: 4px 16px;
            }}
            
            QCalendarWidget QMenu::item:selected {{
                background-color: {COLORS['accent']};
                color: {COLORS['bg_dark']};
            }}
            
            /* Spinbox for year */
            QCalendarWidget QSpinBox {{
                background-color: {COLORS['bg_elevated']};
                border: 1px solid {COLORS['border']};
                border-radius: 0;
                color: {COLORS['text_primary']};
                padding: 2px 4px;
                selection-background-color: {COLORS['accent']};
            }}
            
            QCalendarWidget QSpinBox::up-button,
            QCalendarWidget QSpinBox::down-button {{
                width: 16px;
                background-color: {COLORS['bg_hover']};
                border: none;
            }}
            
            /* Day names header */
            QCalendarWidget QWidget#qt_calendar_calendarview {{
                background-color: {COLORS['bg_elevated']};
            }}
            
            /* Table view for days */
            QCalendarWidget QTableView {{
                background-color: {COLORS['bg_elevated']};
                selection-background-color: {COLORS['accent']};
                selection-color: {COLORS['bg_dark']};
                border: none;
                outline: none;
            }}
            
            QCalendarWidget QTableView::item {{
                padding: 0;
            }}
            
            QCalendarWidget QTableView::item:hover {{
                background-color: {COLORS['bg_hover']};
            }}
            
            QCalendarWidget QTableView::item:selected {{
                background-color: {COLORS['accent']};
                color: {COLORS['bg_dark']};
            }}
            
            /* Header row (day names) */
            QCalendarWidget QHeaderView {{
                background-color: {COLORS['bg_base']};
            }}
            
            QCalendarWidget QHeaderView::section {{
                background-color: {COLORS['bg_base']};
                color: {COLORS['text_muted']};
                font-size: 11px;
                font-weight: 600;
                padding: 4px;
                border: none;
            }}
        """)
        
        # Style for different day types
        today_format = QTextCharFormat()
        today_format.setBackground(QColor(COLORS['accent_muted']))
        today_format.setForeground(QColor(COLORS['text_primary']))
        
        weekday_format = QTextCharFormat()
        weekday_format.setForeground(QColor(COLORS['text_primary']))
        
        weekend_format = QTextCharFormat()
        weekend_format.setForeground(QColor(COLORS['text_secondary']))
        
        self.calendar.setHeaderTextFormat(weekday_format)
        self.calendar.setWeekdayTextFormat(Qt.DayOfWeek.Saturday, weekend_format)
        self.calendar.setWeekdayTextFormat(Qt.DayOfWeek.Sunday, weekend_format)
        
        # Wrap calendar in a widget action
        calendar_action = QWidgetAction(self.calendar_menu)
        calendar_action.setDefaultWidget(self.calendar)
        self.calendar_menu.addAction(calendar_action)
        
        # Add "Today" button
        today_btn = QPushButton("Today")
        today_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        today_btn.clicked.connect(self._go_to_today)
        today_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_base']};
                border: none;
                border-top: 1px solid {COLORS['border']};
                border-radius: 0;
                color: {COLORS['accent']};
                padding: 8px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_hover']};
            }}
        """)
        
        today_action = QWidgetAction(self.calendar_menu)
        today_action.setDefaultWidget(today_btn)
        self.calendar_menu.addAction(today_action)
    
    def _show_calendar(self):
        """Show the calendar popup below the date button."""
        self.calendar.setSelectedDate(self._date)
        
        # Position the menu below the widget
        pos = self.mapToGlobal(QPoint(0, self.height()))
        self.calendar_menu.exec(pos)
    
    def _on_date_selected(self, date: QDate):
        """Handle date selection from calendar."""
        self._date = date
        self._update_display()
        self.calendar_menu.close()
        self.dateChanged.emit(date)
    
    def _go_to_today(self):
        """Set the date to today."""
        today = QDate.currentDate()
        self._date = today
        self.calendar.setSelectedDate(today)
        self._update_display()
        self.calendar_menu.close()
        self.dateChanged.emit(today)
    
    def _update_display(self):
        """Update the button text with the current date."""
        self.date_button.setText(self._date.toString("yyyy-MM-dd"))
    
    def date(self) -> QDate:
        """Get the currently selected date."""
        return self._date
    
    def setDate(self, date: QDate):
        """Set the date."""
        if date.isValid():
            self._date = date
            self._update_display()
    
    def setMaximumWidth(self, width: int):
        """Override to set width on the date button."""
        self.date_button.setMaximumWidth(width - 28)  # Account for icon button
        super().setMaximumWidth(width)
    
    def setMinimumHeight(self, height: int):
        """Override to set height on child widgets."""
        self.date_button.setMinimumHeight(height)
        self.cal_icon_btn.setMinimumHeight(height)
        super().setMinimumHeight(height)


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
        layout.addStretch()
        
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


class LLMTextEdit(QPlainTextEdit):
    """Custom text edit that emits a signal on Cmd+Enter."""
    
    submitRequested = pyqtSignal()
    
    def keyPressEvent(self, event: QKeyEvent):
        # Check for Cmd+Enter (Mac) or Ctrl+Enter (Windows/Linux)
        if event.key() == Qt.Key.Key_Return and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            self.submitRequested.emit()
            return
        super().keyPressEvent(event)


class HeaderWidget(QWidget):
    dataChanged = pyqtSignal()
    generateQuotationRequested = pyqtSignal()
    llmRequestSubmitted = pyqtSignal(str)  # Emits the instruction text

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self.setObjectName("header-widget")
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(SPACING['sm'], SPACING['sm'], SPACING['sm'], SPACING['sm'])
        main_layout.setSpacing(SPACING['sm'])

        quote_card = SectionCard("Quotation")
        quote_grid = QGridLayout()
        quote_grid.setContentsMargins(0, 0, 0, 0)
        quote_grid.setHorizontalSpacing(SPACING['sm'])
        quote_grid.setVerticalSpacing(SPACING['xs'])
        
        number_label = self._create_label("Number")
        quote_grid.addWidget(number_label, 0, 0)
        
        number_container = QWidget()
        number_layout = QHBoxLayout(number_container)
        number_layout.setContentsMargins(0, 0, 0, 0)
        number_layout.setSpacing(0)

        self.quote_number_edit = ModernLineEdit("e.g. 2025-001")
        self.quote_number_edit.setMaximumWidth(140)
        self.quote_number_edit.textChanged.connect(self.on_changed)
        number_layout.addWidget(self.quote_number_edit)

        self.generate_quote_button = QPushButton("++")
        self.generate_quote_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.generate_quote_button.setToolTip("Generate new quotation number")
        self.generate_quote_button.clicked.connect(self._on_generate_quotation_clicked)
        self.generate_quote_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_elevated']};
                border: 1px solid {COLORS['border']};
                border-left: none;
                border-radius: 0;
                padding: {SPACING['xs']}px {SPACING['sm']}px;
                min-height: 0;
                min-width: 28px;
            }}
            QPushButton:hover {{
                border-color: {COLORS['text_muted']};
                background-color: {COLORS['bg_hover']};
            }}
        """)
        self.generate_quote_button.setFixedHeight(self.quote_number_edit.sizeHint().height() + 2)
        number_layout.addWidget(self.generate_quote_button)

        quote_grid.addWidget(number_container, 0, 1)

        date_label = self._create_label("Date")
        quote_grid.addWidget(date_label, 1, 0)
        
        self.date_edit = ModernDatePicker()
        self.date_edit.setMaximumWidth(148)
        self.date_edit.setMinimumHeight(24)
        self.date_edit.dateChanged.connect(self.on_changed)
        quote_grid.addWidget(self.date_edit, 1, 1)
        
        quote_card.content_layout.addLayout(quote_grid)
        main_layout.addWidget(quote_card, 0)

        client_card = SectionCard("Client")
        client_grid = QGridLayout()
        client_grid.setContentsMargins(0, 0, 0, 0)
        client_grid.setHorizontalSpacing(SPACING['sm'])
        client_grid.setVerticalSpacing(SPACING['xs'])

        name_label = self._create_label("Name")
        client_grid.addWidget(name_label, 0, 0)
        
        self.receiver_name = ModernLineEdit("Company or contact name")
        self.receiver_name.textChanged.connect(self.on_changed)
        client_grid.addWidget(self.receiver_name, 0, 1, 1, 3)

        email_label = self._create_label("Email")
        client_grid.addWidget(email_label, 1, 0)
        
        self.receiver_email = ModernLineEdit("client@example.com")
        self.receiver_email.textChanged.connect(self.on_changed)
        client_grid.addWidget(self.receiver_email, 1, 1, 1, 3)
        
        address_label = self._create_label("Address")
        client_grid.addWidget(address_label, 2, 0, Qt.AlignmentFlag.AlignTop)
        
        self.receiver_address = ModernTextEdit("Street, City, Postal Code...")
        self.receiver_address.textChanged.connect(self.on_changed)
        client_grid.addWidget(self.receiver_address, 2, 1, 1, 3)
        
        client_grid.setColumnStretch(1, 1)

        client_card.content_layout.addLayout(client_grid)
        main_layout.addWidget(client_card, 1)

        llm_card = SectionCard("LLM Assistant")
        llm_layout = QVBoxLayout()
        llm_layout.setContentsMargins(0, 0, 0, 0)
        llm_layout.setSpacing(SPACING['xs'])
        
        llm_input_container = QFrame()
        llm_input_container.setObjectName("llm-input-container")
        llm_input_container.setStyleSheet(f"""
            QFrame#llm-input-container {{
                background-color: {COLORS['bg_dark']};
                border: 1px solid {COLORS['border']};
                border-radius: 0;
            }}
        """)
        llm_input_layout = QHBoxLayout(llm_input_container)
        llm_input_layout.setContentsMargins(SPACING['xs'], SPACING['xs'], SPACING['xs'], SPACING['xs'])
        llm_input_layout.setSpacing(SPACING['xs'])

        self.llm_instruction = LLMTextEdit()
        self.llm_instruction.setPlaceholderText("Enter instructions for the LLM... (⌘+Enter to send)")
        self.llm_instruction.setMinimumHeight(72)
        self.llm_instruction.setMaximumHeight(96)
        self.llm_instruction.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: transparent;
                border: none;
                color: {COLORS['text_primary']};
                font-size: 12px;
                padding: 0;
            }}
        """)
        self.llm_instruction.submitRequested.connect(self._on_llm_submit)
        llm_input_layout.addWidget(self.llm_instruction)

        self.llm_send_button = QPushButton()
        self.llm_send_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.llm_send_button.setToolTip("Send instruction to LLM")
        self.llm_send_button.setIcon(icon('auto_awesome', 16, COLORS['bg_dark']))
        self.llm_send_button.setFixedSize(32, 32)
        self.llm_send_button.clicked.connect(self._on_llm_submit)
        self.llm_send_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                border: none;
                border-radius: 4px;
                padding: 0;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent_hover']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['accent_muted']};
            }}
            QPushButton:disabled {{
                background-color: {COLORS['bg_hover']};
            }}
        """)
        llm_input_layout.addWidget(self.llm_send_button, 0, Qt.AlignmentFlag.AlignBottom)

        llm_layout.addWidget(llm_input_container)
        llm_card.content_layout.addLayout(llm_layout)
        main_layout.addWidget(llm_card, 3)

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

    def _on_generate_quotation_clicked(self):
        """Emit signal to request a new quotation number."""
        self.generateQuotationRequested.emit()

    def _on_llm_submit(self):
        """Handle LLM instruction submission."""
        instruction = self.llm_instruction.toPlainText().strip()
        if instruction:
            self.llmRequestSubmitted.emit(instruction)
        else:
            # Still emit with empty string so handler can show a message
            self.llmRequestSubmitted.emit("")

    def set_llm_enabled(self, enabled: bool, tooltip: str = ""):
        """Enable or disable the LLM send button with an optional tooltip."""
        self.llm_send_button.setEnabled(enabled)
        if tooltip:
            self.llm_send_button.setToolTip(tooltip)
        else:
            self.llm_send_button.setToolTip("")

    def set_llm_loading(self, loading: bool):
        """Set the LLM panel to loading state."""
        if loading:
            self.llm_send_button.setEnabled(False)
            self.llm_instruction.setEnabled(False)
        else:
            self.llm_send_button.setEnabled(True)
            self.llm_instruction.setEnabled(True)

    def clear_llm_instruction(self):
        """Clear the LLM instruction textarea."""
        self.llm_instruction.clear()

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

    def clear_data(self):
        """Clears all input fields."""
        self.blockSignals(True)
        self.quote_number_edit.clear()
        self.date_edit.setDate(QDate.currentDate())
        self.receiver_name.clear()
        self.receiver_email.clear()
        self.receiver_address.clear()
        self.blockSignals(False)
