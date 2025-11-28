import os
import yaml
import shutil
from pathlib import Path
from ..utils import get_app_path

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
                 
            return data
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._create_default_structure()

    def _create_default_structure(self) -> dict:
        """Creates the default preset structure."""
        presets = {}
        for i in range(1, 6):
            key = f"preset_{i}"
            presets[key] = self._get_empty_preset(f"Preset {i}")
            
        # Set some defaults for preset 1
        presets['preset_1']['name'] = 'Default Profile'
        
        return {
            'presets': presets,
            'active_preset': 'preset_1'
        }

    def _get_empty_preset(self, name: str) -> dict:
        """Returns an empty preset structure."""
        return {
            'name': name,
            'company': {},
            'contact': {},
            'legal': {},
            'bank': {},
            'defaults': {
                'currency': 'EUR',
                'tax_rate': 19,
                'payment_days': 14,
                'language': 'en'
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
        return self.config.get('presets', {}).get(preset_key, self._get_empty_preset("Unknown"))

    def get_active_preset(self) -> dict:
        """Returns the configuration dict for the active preset."""
        return self.get_preset(self.get_active_preset_name())

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
