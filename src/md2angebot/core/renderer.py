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
            autoescape=select_autoescape(['html', 'xml']),
            cache_size=0,  # Disable caching to ensure updates are seen
            auto_reload=True
        )
        
        # Add custom filters if needed
        self.env.filters['currency'] = self._format_currency

    def render(self, template_name: str, context: dict, preset_config: dict = None) -> str:
        """
        Renders a template with the given context.
        If template_name is 'base' (default), tries to use the preset's configured template.
        
        Args:
            template_name: Name of the template file (without extension)
            context: Data context for rendering
            preset_config: Optional preset configuration to merge
        """
        # Determine base configuration first to check for template preference
        base_config = {}
        if preset_config:
             base_config = preset_config
        elif 'company' not in context:
             base_config = config.get_active_preset()

        # Check if we should use a preset-specific template
        # Only override if template_name is the default "base"
        if template_name == "base" and 'layout' in base_config:
            preset_template = base_config['layout'].get('template')
            if preset_template:
                template_name = preset_template

        try:
            template = self.env.get_template(f"{template_name}.html")
        except Exception as e:
            print(f"Template {template_name}.html not found ({e}), attempting fallback...")
            try:
                # Try modern-split as the new default
                template = self.env.get_template("modern-split.html")
            except:
                # Last resort, try base.html if it still exists
                print("modern-split.html not found, trying base.html")
                template = self.env.get_template("base.html")
            
        # Ensure full_context has layout and snippets to prevent "undefined" errors in template
        full_context = {**base_config, **context}
        
        # Default fallback for layout if missing
        if 'layout' not in full_context:
            full_context['layout'] = {
                'template': 'modern-split',
                'page_margins': [20, 20, 20, 20]
            }
        
        # Default fallback for snippets if missing
        if 'snippets' not in full_context:
            full_context['snippets'] = {
                'intro_text': '',
                'terms': '',
                'signature_block': True,
                'custom_footer': ''
            }
            
        return template.render(**full_context)

    def _format_currency(self, value, currency="EUR"):
        """Format number as currency string."""
        try:
            val = float(value)
            return f"€ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except (ValueError, TypeError):
            return value
