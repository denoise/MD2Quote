import os
import yaml
import shutil
from pathlib import Path
from datetime import datetime
from ..utils import get_app_path


# Fixed mapping between presets and layout templates
# Each preset is associated with a specific template that cannot be changed
PRESET_TEMPLATE_MAP = {
    'preset_1': 'modern-split',
    'preset_2': 'elegant-centered',
    'preset_3': 'minimal-sidebar',
    'preset_4': 'bold-stamp',
    'preset_5': 'classic-letterhead',
}

class ConfigLoader:
    APP_NAME = "md2angebot"
    
    def __init__(self):
        self.project_root = get_app_path()  # Works both in development and bundled app
        self.config_dir = self._get_config_dir()
        self.config_path = self.config_dir / "config.yaml"
        self.templates_dir = self.config_dir / "templates"
        self.styles_dir = self.config_dir / "styles"
        self._ensure_config_exists()
        self.config = self._load_config()

    def _get_config_dir(self) -> Path:
        """Returns the user configuration directory."""
        return Path(os.path.expanduser(f"~/.config/{self.APP_NAME}"))

    def _ensure_config_exists(self):
        """Creates config directory and default files if they don't exist."""
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)
            self.templates_dir.mkdir(exist_ok=True)
            self.styles_dir.mkdir(exist_ok=True)

        if not self.config_path.exists():
            # Try to find the example config in the project root
            example_config = self.project_root / "examples" / "config.yaml"
            
            if example_config.exists():
                try:
                    shutil.copy(example_config, self.config_path)
                    print(f"Copied example config to {self.config_path}")
                except Exception as e:
                    print(f"Could not copy example config: {e}")
            else:
                print("Example config not found, starting with empty config.")

    def _load_config(self) -> dict:
        """Loads the configuration file and migrates if necessary."""
        if not self.config_path.exists():
            return self._create_default_structure()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
                
            # Check if migration is needed (old config structure has company at root)
            if 'company' in data and 'presets' not in data:
                return self._migrate_config(data)
            
            # Ensure structure is valid even if file exists
            if 'presets' not in data:
                 return self._create_default_structure()
                 
            # Backfill missing keys (like layout/snippets) in existing presets
            updated = False
            presets = data.get('presets', {})
            for key, preset in presets.items():
                empty = self._get_empty_preset("temp")
                
                if 'layout' not in preset:
                    preset['layout'] = empty['layout']
                    updated = True
                    
                if 'snippets' not in preset:
                    preset['snippets'] = empty['snippets']
                    updated = True
                    
            if updated:
                print("Backfilled missing config keys (layout/snippets)")
                # Save the updated config
                try:
                     with open(self.config_path, 'w', encoding='utf-8') as f:
                        yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
                except Exception as e:
                    print(f"Error saving backfilled config: {e}")

            return data
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._create_default_structure()

    def _create_default_structure(self) -> dict:
        """Creates the default preset structure."""
        presets = {}
        for i in range(1, 6):
            key = f"preset_{i}"
            presets[key] = self._get_empty_preset(f"Preset {i}", key)
            
        # Set some defaults for preset 1
        presets['preset_1']['name'] = 'Default Profile'
        
        return {
            'presets': presets,
            'active_preset': 'preset_1'
        }

    def _get_empty_preset(self, name: str, preset_key: str = 'preset_1') -> dict:
        """Returns an empty preset structure with the fixed template for this preset."""
        # Each preset has a fixed template that cannot be changed by the user
        template = PRESET_TEMPLATE_MAP.get(preset_key, 'modern-split')
        return {
            'name': name,
            'company': {},
            'contact': {
                'enabled': True
            },
            'legal': {
                'enabled': True
            },
            'bank': {
                'enabled': True
            },
            'layout': {
                'template': template,
                'page_margins': [20, 20, 20, 20]
            },
            'snippets': {
                'enabled': True,
                'intro_text': '',
                'terms': '',
                'signature_block': True,
                'custom_footer': ''
            },
            'defaults': {
                'currency': 'EUR',
                'tax_rate': 19,
                'payment_days': 14,
                'language': 'en'
            },
            'quotation_number': {
                'enabled': True,
                'format': '{YYYY}-{NNN}',  # Default format: 2025-001
                'counter': 0,
                'last_reset_year': None,
                'last_reset_month': None
            },
            'typography': {
                'heading': 'Montserrat',
                'body': 'Source Sans Pro',
                'mono': 'JetBrains Mono',
                'sizes': {
                    'company_name': 24,
                    'heading1': 18,
                    'heading2': 14,
                    'body': 10,
                    'small': 8
                }
            },
            'colors': {
                'primary': '#1a1a2e',
                'accent': '#e94560',
                'background': '#ffffff',
                'text': '#2d2d2d',
                'muted': '#6c757d',
                'border': '#dee2e6',
                'table_alt': '#f8f9fa'
            }
        }

    def _migrate_config(self, old_data: dict) -> dict:
        """Migrates old flat config to preset structure."""
        print("Migrating configuration to preset system...")
        
        new_config = self._create_default_structure()
        
        # Copy old data to preset_1
        preset1 = new_config['presets']['preset_1']
        
        for section in ['company', 'contact', 'legal', 'bank', 'defaults', 'typography', 'colors']:
            if section in old_data:
                preset1[section] = old_data[section]
        
        # Ensure new keys exist even if they weren't in old_data
        empty = self._get_empty_preset("temp")
        if 'layout' not in preset1:
             preset1['layout'] = empty['layout']
        if 'snippets' not in preset1:
             preset1['snippets'] = empty['snippets']
             
        preset1['name'] = old_data.get('company', {}).get('name', 'Migrated Profile')
        
        # Save the migrated config immediately
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(new_config, f, allow_unicode=True, sort_keys=False)
        except Exception as e:
            print(f"Error saving migrated config: {e}")
            
        return new_config

    def get(self, key: str, default=None):
        """Retrieve a value from configuration using dot notation."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def get_active_preset_name(self) -> str:
        """Returns the key of the active preset (e.g., 'preset_1')."""
        return self.config.get('active_preset', 'preset_1')

    def set_active_preset(self, preset_key: str):
        """Sets the active preset key."""
        if preset_key in self.config.get('presets', {}):
            self.config['active_preset'] = preset_key
            # Persist change? usually done via save, but we can do it here if we want instant persistence of state
            # For now we assume save is explicit in config dialog, but for main window usage, we might want to persist.
            # The Main Window usage usually implies just switching for the session, unless we want to remember last used.
            # Let's keep it in memory and let explicit save handle persistence, or handle it in Main Window close.
            # Actually, the user might expect it to be saved. I'll leave it in memory for now as per common pattern.

    def get_preset(self, preset_key: str) -> dict:
        """Returns the configuration dict for a specific preset."""
        return self.config.get('presets', {}).get(preset_key, self._get_empty_preset("Unknown", preset_key))

    def get_active_preset(self) -> dict:
        """Returns the configuration dict for the active preset."""
        return self.get_preset(self.get_active_preset_name())

    def generate_quotation_number(self, preset_key: str) -> str:
        """
        Generates a new quotation number for the given preset based on its format.
        Increments the counter and persists the change.
        
        Format placeholders:
        - {YYYY}: Full year (2025)
        - {YY}: Two-digit year (25)
        - {MM}: Month (01-12)
        - {DD}: Day (01-31)
        - {N}, {NN}, {NNN}, {NNNN}: Counter with padding
        - {PREFIX}: Uses company name abbreviation
        
        Returns empty string if quotation numbering is disabled.
        """
        preset = self.config.get('presets', {}).get(preset_key, {})
        qn_config = preset.get('quotation_number', {})
        
        if not qn_config.get('enabled', True):
            return ''
        
        format_str = qn_config.get('format', '{YYYY}-{NNN}')
        counter = qn_config.get('counter', 0)
        last_reset_year = qn_config.get('last_reset_year')
        last_reset_month = qn_config.get('last_reset_month')
        
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        
        # Check if we need to reset the counter (yearly or monthly reset)
        reset_counter = False
        
        # Check for yearly reset (if format contains {YYYY} or {YY})
        if '{YYYY}' in format_str or '{YY}' in format_str:
            if last_reset_year != current_year:
                reset_counter = True
        
        # Check for monthly reset (if format contains {MM})
        if '{MM}' in format_str:
            if last_reset_year != current_year or last_reset_month != current_month:
                reset_counter = True
        
        if reset_counter:
            counter = 0
        
        # Increment counter
        counter += 1
        
        # Build the quotation number
        result = format_str
        result = result.replace('{YYYY}', str(current_year))
        result = result.replace('{YY}', str(current_year)[-2:])
        result = result.replace('{MM}', f'{current_month:02d}')
        result = result.replace('{DD}', f'{now.day:02d}')
        
        # Handle counter placeholders with different padding
        result = result.replace('{NNNN}', f'{counter:04d}')
        result = result.replace('{NNN}', f'{counter:03d}')
        result = result.replace('{NN}', f'{counter:02d}')
        result = result.replace('{N}', str(counter))
        
        # Optional: PREFIX from company name
        company_name = preset.get('company', {}).get('name', '')
        if company_name:
            # Create abbreviation from first letters of words
            prefix = ''.join(word[0].upper() for word in company_name.split() if word)[:3]
        else:
            prefix = 'QT'
        result = result.replace('{PREFIX}', prefix)
        
        # Update and persist the counter
        if 'quotation_number' not in self.config['presets'][preset_key]:
            self.config['presets'][preset_key]['quotation_number'] = {}
        
        self.config['presets'][preset_key]['quotation_number']['counter'] = counter
        self.config['presets'][preset_key]['quotation_number']['last_reset_year'] = current_year
        self.config['presets'][preset_key]['quotation_number']['last_reset_month'] = current_month
        
        # Persist to disk
        self._save_config()
        
        return result

    def get_last_quotation_number(self, preset_key: str) -> str:
        """
        Returns the last generated quotation number without incrementing.
        Useful for displaying current state.
        """
        preset = self.config.get('presets', {}).get(preset_key, {})
        qn_config = preset.get('quotation_number', {})
        
        if not qn_config.get('enabled', True):
            return ''
        
        format_str = qn_config.get('format', '{YYYY}-{NNN}')
        counter = qn_config.get('counter', 0)
        
        if counter == 0:
            return ''  # No quotation generated yet
        
        now = datetime.now()
        last_year = qn_config.get('last_reset_year', now.year)
        last_month = qn_config.get('last_reset_month', now.month)
        
        # Build the quotation number with stored values
        result = format_str
        result = result.replace('{YYYY}', str(last_year))
        result = result.replace('{YY}', str(last_year)[-2:])
        result = result.replace('{MM}', f'{last_month:02d}')
        result = result.replace('{DD}', f'{now.day:02d}')
        
        result = result.replace('{NNNN}', f'{counter:04d}')
        result = result.replace('{NNN}', f'{counter:03d}')
        result = result.replace('{NN}', f'{counter:02d}')
        result = result.replace('{N}', str(counter))
        
        # PREFIX
        preset = self.config.get('presets', {}).get(preset_key, {})
        company_name = preset.get('company', {}).get('name', '')
        if company_name:
            prefix = ''.join(word[0].upper() for word in company_name.split() if word)[:3]
        else:
            prefix = 'QT'
        result = result.replace('{PREFIX}', prefix)
        
        return result

    def _save_config(self):
        """Saves the current configuration to disk."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        except Exception as e:
            print(f"Error saving config: {e}")

    def resolve_path(self, path_str: str) -> Path:
        """Resolves a path string to an absolute Path object."""
        if not path_str:
            return None
        
        # Expand user home directory
        path = Path(os.path.expanduser(path_str))
        
        # If absolute and exists, return it
        if path.is_absolute():
            return path if path.exists() else None
            
        # Check relative to user config dir
        p = self.config_dir / path
        if p.exists():
            return p
            
        # Check relative to project root (assets, etc.)
        p = self.project_root / path
        if p.exists():
            return p
            
        return None

# Global instance
config = ConfigLoader()
