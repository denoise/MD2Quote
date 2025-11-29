from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QStackedWidget
from PyQt6.QtPdf import QPdfDocument
from PyQt6.QtPdfWidgets import QPdfView
from PyQt6.QtCore import QBuffer, QIODevice, QTimer
from .styles import COLORS, SPACING


class PreviewWidget(QWidget):
    """Container widget for the PDF preview with smooth double-buffered updates."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("preview-container")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Section header
        header = QLabel("Preview")
        header.setObjectName("preview-label")
        header.setStyleSheet(f"""
            color: {COLORS['text_muted']};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding: {SPACING['sm']}px {SPACING['md']}px;
            background-color: {COLORS['bg_base']};
            border-bottom: 1px solid {COLORS['border']};
        """)
        layout.addWidget(header)

        # Double-buffered PDF views using a stacked widget
        self._stack = QStackedWidget(self)
        self._stack.setStyleSheet(f"background-color: {COLORS['bg_dark']};")
        
        # Create two PDF views for double-buffering
        self._pdf_views = []
        self._pdf_documents = []
        self._buffers = [None, None]  # Keep buffers alive
        
        for i in range(2):
            pdf_view = QPdfView(self)
            pdf_view.setObjectName(f"pdf-view-{i}")
            pdf_document = QPdfDocument(self)
            pdf_view.setDocument(pdf_document)
            
            # View settings
            pdf_view.setPageMode(QPdfView.PageMode.MultiPage)
            pdf_view.setZoomMode(QPdfView.ZoomMode.FitToWidth)
            
            # Style the view
            pdf_view.setStyleSheet(f"""
                QPdfView {{
                    background-color: {COLORS['bg_dark']};
                    border: none;
                }}
            """)
            
            self._pdf_views.append(pdf_view)
            self._pdf_documents.append(pdf_document)
            self._stack.addWidget(pdf_view)
        
        # Track which buffer is active (0 or 1)
        self._active_buffer = 0
        
        layout.addWidget(self._stack)
        
        # Store pending scroll position for restoration
        self._pending_scroll_position = None
        self._is_first_load = True

    @property
    def pdf_view(self):
        """Returns the currently active PDF view (for compatibility)."""
        return self._pdf_views[self._active_buffer]
    
    @property
    def pdf_document(self):
        """Returns the currently active PDF document (for compatibility)."""
        return self._pdf_documents[self._active_buffer]

    def update_preview(self, pdf_bytes: bytes):
        """Updates the preview with new PDF content using double-buffering for smooth transitions."""
        # Save current scroll position from the active view
        active_view = self._pdf_views[self._active_buffer]
        scrollbar = active_view.verticalScrollBar()
        saved_scroll_value = scrollbar.value()
        saved_scroll_max = scrollbar.maximum()
        
        # Calculate relative scroll position (0.0 to 1.0) to handle document size changes
        if saved_scroll_max > 0:
            self._pending_scroll_position = saved_scroll_value / saved_scroll_max
        else:
            self._pending_scroll_position = 0.0
        
        # Load into the INACTIVE buffer
        next_buffer = 1 - self._active_buffer
        next_view = self._pdf_views[next_buffer]
        next_document = self._pdf_documents[next_buffer]
        
        # Create buffer and load PDF into inactive document
        self._buffers[next_buffer] = QBuffer()
        self._buffers[next_buffer].setData(pdf_bytes)
        self._buffers[next_buffer].open(QIODevice.OpenModeFlag.ReadOnly)
        next_document.load(self._buffers[next_buffer])
        
        # Schedule the swap after document is ready
        QTimer.singleShot(30, lambda: self._swap_buffers(next_buffer))
    
    def _swap_buffers(self, next_buffer: int):
        """Swaps to the newly loaded buffer and restores scroll position."""
        next_view = self._pdf_views[next_buffer]
        saved_position = self._pending_scroll_position
        
        # Pre-set scroll position on the new view before showing it
        if saved_position is not None:
            scrollbar = next_view.verticalScrollBar()
            new_max = scrollbar.maximum()
            if new_max > 0:
                scrollbar.setValue(int(saved_position * new_max))
        
        # Freeze updates during swap for smoother transition
        self._stack.setUpdatesEnabled(False)
        
        # Switch to the new buffer
        self._stack.setCurrentIndex(next_buffer)
        self._active_buffer = next_buffer
        
        # Re-enable updates
        self._stack.setUpdatesEnabled(True)
        
        # Fine-tune scroll position after swap (in case it wasn't quite ready)
        if saved_position is not None and not self._is_first_load:
            QTimer.singleShot(10, lambda: self._fine_tune_scroll(saved_position))
        
        self._is_first_load = False
        self._pending_scroll_position = None
    
    def _fine_tune_scroll(self, position: float):
        """Fine-tunes scroll position after the view is fully rendered."""
        scrollbar = self._pdf_views[self._active_buffer].verticalScrollBar()
        new_max = scrollbar.maximum()
        if new_max > 0:
            scrollbar.setValue(int(position * new_max))
