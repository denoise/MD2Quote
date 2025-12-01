from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
import sys
from .config import config
from ..utils import get_templates_path

class TemplateRenderer:
    def __init__(self):
        """
        Initialize the template renderer with appropriate template directory priority.
        
        Development Mode (running from source):
            1. Source templates (`./templates/`) - for live editing
            2. User config templates (`~/.config/md2angebot/templates/`) - fallback
        
        Production Mode (bundled .app):
            1. User config templates - user customizations
            2. Bundled templates - defaults
        """
        # Detect if running from source or bundled
        is_bundled = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
        
        if is_bundled:
            # Production: User config first, then bundled templates
            template_dirs = [
                config.templates_dir,
                get_templates_path()
            ]
        else:
            # Development: Source templates first for live editing
            template_dirs = [
                get_templates_path(),  # Source templates (priority)
                config.templates_dir,  # User config (fallback)
            ]
        
        self.env = Environment(
            loader=FileSystemLoader(template_dirs),
            autoescape=select_autoescape(['html', 'xml']),
            cache_size=0,  # Disable caching to ensure updates are seen
            auto_reload=True
        )
        
        # Clear cache before each render to pick up file changes
        # This is fast and ensures template changes are always detected
        self._clear_cache_on_render = True
        
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
        # Map legacy template names to new preset names
        legacy_map = {
            'modern-split': 'preset_1',
            'elegant-centered': 'preset_2',
            'minimal-sidebar': 'preset_3',
            'bold-stamp': 'preset_4',
            'classic-letterhead': 'preset_5'
        }
        if template_name in legacy_map:
             template_name = legacy_map[template_name]

        # Clear Jinja2 cache to pick up any file changes
        # This ensures template edits are immediately visible
        if self._clear_cache_on_render:
            try:
                if self.env.cache is not None:
                    self.env.cache.clear()
                if hasattr(self.env, 'bytecode_cache') and self.env.bytecode_cache:
                    self.env.bytecode_cache.clear()
            except Exception as e:
                print(f"Warning: Failed to clear Jinja2 cache: {e}")
        
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
                if preset_template in legacy_map:
                    template_name = legacy_map[preset_template]
                else:
                    template_name = preset_template

        try:
            template = self.env.get_template(f"{template_name}.html")
        except Exception as e:
            print(f"Template {template_name}.html not found ({e}), attempting fallback...")
            try:
                # Try preset_1 as the new default
                template = self.env.get_template("preset_1.html")
            except:
                # Last resort, try base.html if it still exists
                print("preset_1.html not found, trying base.html")
                template = self.env.get_template("base.html")
            
        # Ensure full_context has layout and snippets to prevent "undefined" errors in template
        full_context = {**base_config, **context}
        
        # Default fallback for layout if missing
        if 'layout' not in full_context:
            full_context['layout'] = {
                'template': 'preset_1',
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
