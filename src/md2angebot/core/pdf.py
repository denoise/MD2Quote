from weasyprint import HTML, CSS
from pathlib import Path
from .config import config
from ..utils import get_templates_path

class PDFGenerator:
    def _get_css_files(self):
        css_files = []
        # 1. App bundled CSS - REMOVED to prevent conflicts with template-specific CSS
        # base_css_path = get_templates_path() / 'quotation.css'
        # if base_css_path.exists():
        #     css_files.append(CSS(filename=base_css_path))
            
        # 2. User custom CSS (keep this for global overrides)
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
