import os
import yaml
import shutil
from pathlib import Path

class ConfigLoader:
    APP_NAME = "md2angebot"
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
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
        """Loads the configuration file."""
        if not self.config_path.exists():
            return {}
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

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

    def get_quote_types(self) -> dict:
        """Returns quote types from config or defaults."""
        types = self.get('quote_types')
        if types:
            return types
            
        # Default fallback if not in config
        return {
            'code': {
                'name': 'Code / Development',
                'logo': 'assets/images/logo_code.svg'
            }
        }

    def get_logo_path(self, quote_type: str = None) -> str:
        """Returns the resolved path for the logo based on quote type."""
        logo_path_str = None
        
        if quote_type:
            # Try to find in quote_types
            types = self.get_quote_types()
            if quote_type in types:
                logo_path_str = types[quote_type].get('logo')
        
        if not logo_path_str:
            # Fallback to default company logo
            logo_path_str = self.get('company.logo')
            
        resolved = self.resolve_path(logo_path_str)
        return str(resolved) if resolved else logo_path_str

# Global instance
config = ConfigLoader()
