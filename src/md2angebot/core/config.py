import os
import yaml
import shutil
from pathlib import Path

class ConfigLoader:
    APP_NAME = "md2angebot"
    
    def __init__(self):
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
            # src/md2angebot/core/config.py -> ... -> root -> examples/config.yaml
            project_root = Path(__file__).parent.parent.parent.parent
            example_config = project_root / "examples" / "config.yaml"
            
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

# Global instance
config = ConfigLoader()

