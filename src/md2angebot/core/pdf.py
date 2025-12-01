from pathlib import Path
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtCore import QEventLoop, QUrl, QMarginsF
from PyQt6.QtGui import QPageLayout, QPageSize
from ..core.config import config


# Default page margins in millimeters (top, right, bottom, left)
DEFAULT_PAGE_MARGINS = (20, 20, 20, 20)


class PDFGenerator:
    """Generates PDFs from HTML using Qt's WebEngine."""
    
    def __init__(self):
        self._view = None
        self._margins = DEFAULT_PAGE_MARGINS
    
    def set_margins(self, margins: tuple):
        """Set page margins in mm as (top, right, bottom, left)."""
        self._margins = margins
    
    def _ensure_view(self):
        """Lazily initialize the web view."""
        if self._view is None:
            self._view = QWebEngineView()
            self._view.setMinimumSize(1, 1)
    
    def _get_page_layout(self):
        """Returns A4 page layout with configured margins."""
        top, right, bottom, left = self._margins
        return QPageLayout(
            QPageSize(QPageSize.PageSizeId.A4),
            QPageLayout.Orientation.Portrait,
            QMarginsF(left, top, right, bottom),  # QMarginsF takes (left, top, right, bottom)
            QPageLayout.Unit.Millimeter
        )
    
    def generate(self, html_content: str, output_path: str):
        """Generates a PDF from HTML content and saves to file."""
        pdf_bytes = self.generate_bytes(html_content)
        Path(output_path).write_bytes(pdf_bytes)
    
    def generate_bytes(self, html_content: str) -> bytes:
        """Generates a PDF and returns bytes."""
        self._ensure_view()
        
        # Use config directory as base URL for resolving relative paths
        base_url = QUrl.fromLocalFile(str(config.config_dir) + "/")
        
        # Load HTML into the view
        loop = QEventLoop()
        self._view.loadFinished.connect(loop.quit)
        self._view.setHtml(html_content, base_url)
        loop.exec()
        
        # Generate PDF
        pdf_data = []
        
        def on_pdf_ready(data):
            pdf_data.append(bytes(data))
            loop.quit()
        
        self._view.page().printToPdf(on_pdf_ready, self._get_page_layout())
        loop.exec()
        
        return pdf_data[0] if pdf_data else b""
