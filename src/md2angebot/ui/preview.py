from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtPdf import QPdfDocument
from PyQt6.QtPdfWidgets import QPdfView
from PyQt6.QtCore import QBuffer, QIODevice
from .styles import COLORS, SPACING


class PreviewWidget(QWidget):
    """Container widget for the PDF preview."""
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

        # PDF Viewer
        self.pdf_view = QPdfView(self)
        self.pdf_view.setObjectName("pdf-view")
        self.pdf_document = QPdfDocument(self)
        self.pdf_view.setDocument(self.pdf_document)
        
        # View settings
        self.pdf_view.setPageMode(QPdfView.PageMode.MultiPage)
        self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitToWidth)
        
        # Style the view
        self.pdf_view.setStyleSheet(f"""
            QPdfView {{
                background-color: {COLORS['bg_dark']};
                border: none;
            }}
        """)
        
        layout.addWidget(self.pdf_view)

    def update_preview(self, pdf_bytes: bytes):
        """Updates the preview with new PDF content."""
        self.buffer = QBuffer()
        self.buffer.setData(pdf_bytes)
        self.buffer.open(QIODevice.OpenModeFlag.ReadOnly)
        self.pdf_document.load(self.buffer)
