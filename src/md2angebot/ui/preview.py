from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtPdf import QPdfDocument
from PyQt6.QtPdfWidgets import QPdfView
from PyQt6.QtCore import QBuffer, QIODevice

class PreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.pdf_view = QPdfView(self)
        self.pdf_document = QPdfDocument(self)
        self.pdf_view.setDocument(self.pdf_document)
        
        # View settings
        self.pdf_view.setPageMode(QPdfView.PageMode.MultiPage)
        self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitToWidth)
        
        self.layout.addWidget(self.pdf_view)

    def update_preview(self, pdf_bytes: bytes):
        """
        Updates the preview with new PDF content.
        """
        # We need to keep a reference to the buffer or load it directly
        # QPdfDocument.load expects a QIODevice or filename.
        
        self.buffer = QBuffer()
        self.buffer.setData(pdf_bytes)
        self.buffer.open(QIODevice.OpenModeFlag.ReadOnly)
        
        self.pdf_document.load(self.buffer)

