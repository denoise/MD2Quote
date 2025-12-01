"""Utility functions for md2angebot."""

import sys
from pathlib import Path


def get_app_path() -> Path:
    """
    Get the application base path.
    
    When running from PyInstaller bundle, returns the path to the bundled resources.
    When running from source, returns the project root directory.
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    else:
        return Path(__file__).parent.parent.parent.parent


def get_templates_path() -> Path:
    """Get the path to the templates directory."""
    return get_app_path() / 'templates'


def get_assets_path() -> Path:
    """Get the path to the assets directory."""
    return get_app_path() / 'assets'


def get_examples_path() -> Path:
    """Get the path to the examples directory."""
    return get_app_path() / 'examples'


