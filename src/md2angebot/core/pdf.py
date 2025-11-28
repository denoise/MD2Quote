from weasyprint import HTML, CSS
from pathlib import Path
from .config import config

class PDFGenerator:
    def _get_css_files(self):
        css_files = []
        # 1. App bundled CSS
        # Adjust path to find templates relative to this file
        # src/md2angebot/core/pdf.py -> src/md2angebot/core -> src/md2angebot -> src -> root -> templates
        base_css_path = Path(__file__).parent.parent.parent.parent / 'templates' / 'quotation.css'
        
        if base_css_path.exists():
            css_files.append(CSS(filename=base_css_path))
            
        # 2. User custom CSS
        user_css_path = config.styles_dir / 'quotation.css'
        if user_css_path.exists():
            css_files.append(CSS(filename=user_css_path))
        
        return css_files

    def generate(self, html_content: str, output_path: str):
        """
        Generates a PDF from HTML content and saves to file.
        """
        HTML(string=html_content, base_url=str(config.config_dir)).write_pdf(
            output_path,
            stylesheets=self._get_css_files()
        )

    def generate_bytes(self, html_content: str) -> bytes:
        """
        Generates a PDF and returns bytes.
        """
        return HTML(string=html_content, base_url=str(config.config_dir)).write_pdf(
            stylesheets=self._get_css_files()
        )
