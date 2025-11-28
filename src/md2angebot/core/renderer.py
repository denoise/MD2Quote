from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from .config import config
from ..utils import get_templates_path

class TemplateRenderer:
    def __init__(self):
        # Load templates from user config dir first, then app package
        template_dirs = [
            config.templates_dir,
            get_templates_path()  # Works both in development and bundled app
        ]
        
        self.env = Environment(
            loader=FileSystemLoader(template_dirs),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Add custom filters if needed
        self.env.filters['currency'] = self._format_currency

    def render(self, template_name: str, context: dict, preset_config: dict = None) -> str:
        """
        Renders a template with the given context.
        If template_name is not found, falls back to 'base.html'.
        
        Args:
            template_name: Name of the template file (without extension)
            context: Data context for rendering
            preset_config: Optional preset configuration to merge
        """
        try:
            template = self.env.get_template(f"{template_name}.html")
        except:
            # Fallback if specific template doesn't exist
            print(f"Template {template_name}.html not found, using base.html")
            template = self.env.get_template("base.html")
            
        # Determine base configuration
        # If preset_config is passed, use it. 
        # If not, and context doesn't have company info, try to use active preset.
        # We avoid merging config.config directly as it now has a different structure.
        
        base_config = {}
        if preset_config:
             base_config = preset_config
        elif 'company' not in context:
             base_config = config.get_active_preset()
             
        full_context = {**base_config, **context}
        return template.render(**full_context)

    def _format_currency(self, value, currency="EUR"):
        """Format number as currency string."""
        try:
            val = float(value)
            return f"€ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except (ValueError, TypeError):
            return value
