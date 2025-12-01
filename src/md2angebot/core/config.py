import os
import yaml
import shutil
import copy
import time
import zipfile
from pathlib import Path
from datetime import datetime
from .llm import DEFAULT_SYSTEM_PROMPT
from ..utils import get_app_path, get_templates_path


# Default preset keys (used for initial setup and template resolution)
DEFAULT_PRESET_KEYS = ['preset_1', 'preset_2', 'preset_3', 'preset_4', 'preset_5']

LEGACY_SYSTEM_PROMPTS = [
    """You are an assistant that generates proposal content in Markdown for MD2Angebot.

Follow these rules:
- Produce only the proposal body; do not add headers, footers, quotation numbers, dates, or client/company contact blocks.
- Do not create sections such as "Client Information", acceptance/signature areas, payment instructions, or validity/expiry dates unless they already exist in the provided context.
- Do not ask for or include client information—the application supplies required metadata.
- Preserve any "+++" markers exactly; they represent page breaks and must never be removed.
- Output must be clean Markdown content only, without assistant chatter, questions, or explanations.
- Use clear, professional language with concise sections and bullet points; include scope, deliverables, and timelines when relevant.""",
    '''You are an assistant helping create professional quotations and proposals.

When generating content, follow these guidelines:
- Use clear, professional language
- Structure content with appropriate headings and bullet points
- Include relevant details like scope, deliverables, and timelines when applicable
- Format output as valid Markdown
- Be concise but thorough

When editing existing content:
- Preserve the overall structure unless asked to change it
- Improve clarity and professionalism
- Fix any grammatical or formatting issues
- Maintain the original intent and key information'''
]

DEFAULT_LLM_CONFIG = {
    'provider': 'openrouter',
    'api_key': '',
    'model': 'anthropic/claude-sonnet-4',
    'system_prompt': DEFAULT_SYSTEM_PROMPT
}

class ConfigLoader:
    APP_NAME = "md2angebot"
    
    def __init__(self):
        self.project_root = get_app_path()
        self.config_dir = self._get_config_dir()
        self.config_path = self.config_dir / "config.yaml"
        self.templates_dir = self.config_dir / "templates"
        self.styles_dir = self.config_dir / "styles"
        self.logos_dir = self.config_dir / "logos"
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
            self.logos_dir.mkdir(exist_ok=True)
        
        # Ensure logos dir exists even if config dir already exists
        if not self.logos_dir.exists():
            self.logos_dir.mkdir(exist_ok=True)

        if not self.config_path.exists():
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
                
            if 'company' in data and 'presets' not in data:
                return self._migrate_config(data)
            
            if 'presets' not in data:
                 return self._create_default_structure()

            data = self._migrate_template_names(data)
                 
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
                
                if 'company' in preset:
                    company = preset['company']
                    if 'show_name' not in company:
                        company['show_name'] = True
                        updated = True
                    if 'show_tagline' not in company:
                        company['show_tagline'] = True
                        updated = True
                    if 'show_logo' not in company:
                        company['show_logo'] = True
                        updated = True
                    if 'logo_width' not in company:
                        company['logo_width'] = 40
                        updated = True
                
                if 'defaults' in preset and 'vat_type' not in preset['defaults']:
                    preset['defaults']['vat_type'] = 'german_vat'
                    updated = True
                    
            if updated:
                print("Backfilled missing config keys (layout/snippets/company_flags)")
                try:
                     with open(self.config_path, 'w', encoding='utf-8') as f:
                        yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
                except Exception as e:
                    print(f"Error saving backfilled config: {e}")

            if 'llm' not in data:
                data['llm'] = DEFAULT_LLM_CONFIG.copy()
                try:
                    with open(self.config_path, 'w', encoding='utf-8') as f:
                        yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
                    print("Backfilled LLM config")
                except Exception as e:
                    print(f"Error saving backfilled LLM config: {e}")

            data = self._migrate_llm_prompt(data)
            data = self._migrate_logos(data)
            return data
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._create_default_structure()

    def _migrate_template_names(self, data: dict) -> dict:
        """Migrates old template names to new preset names."""
        old_names = {
            'modern-split': 'preset_1',
            'elegant-centered': 'preset_2',
            'minimal-sidebar': 'preset_3',
            'bold-stamp': 'preset_4',
            'classic-letterhead': 'preset_5'
        }
        updated = False
        presets = data.get('presets', {})
        for key, preset in presets.items():
            layout = preset.get('layout', {})
            current_template = layout.get('template')
            if current_template in old_names:
                layout['template'] = old_names[current_template]
                updated = True
        
        if updated:
            print("Migrated old template names to new preset names.")
            try:
                 with open(self.config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
            except Exception as e:
                print(f"Error saving config after template migration: {e}")
        
        return data

    def _migrate_llm_prompt(self, data: dict) -> dict:
        """Updates legacy or missing LLM prompts without overwriting custom text."""
        llm_cfg = data.get('llm')
        if not isinstance(llm_cfg, dict):
            return data

        current_prompt = llm_cfg.get('system_prompt', '')
        updated = False

        if not current_prompt:
            llm_cfg['system_prompt'] = DEFAULT_SYSTEM_PROMPT
            updated = True
        elif current_prompt in LEGACY_SYSTEM_PROMPTS:
            llm_cfg['system_prompt'] = DEFAULT_SYSTEM_PROMPT
            updated = True

        if updated:
            try:
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
                print("Updated LLM system prompt to latest default.")
            except Exception as e:
                print(f"Error saving config after LLM prompt migration: {e}")

        return data

    def _migrate_logos(self, data: dict) -> dict:
        """Migrates logos from external paths to internal storage."""
        presets = data.get('presets', {})
        updated = False
        
        for preset_key, preset in presets.items():
            company = preset.get('company', {})
            logo_path = company.get('logo', '')
            
            if not logo_path:
                continue
                
            # Skip if already in logos dir (just a filename, no path separators)
            if '/' not in logo_path and '\\' not in logo_path:
                # Check if this is already a migrated logo (exists in logos_dir)
                if (self.logos_dir / logo_path).exists():
                    continue
            
            # Try to resolve the path
            resolved = self.resolve_path(logo_path)
            if resolved and resolved.exists():
                # Copy to internal storage
                new_logo_path = self.copy_logo(str(resolved), preset_key)
                if new_logo_path != logo_path:
                    company['logo'] = new_logo_path
                    updated = True
                    print(f"Migrated logo for '{preset.get('name', preset_key)}' to internal storage")
        
        if updated:
            try:
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
                print("Saved logo migration changes.")
            except Exception as e:
                print(f"Error saving config after logo migration: {e}")
        
        return data

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
            'active_preset': 'preset_1',
            'llm': DEFAULT_LLM_CONFIG.copy()
        }

    def _get_empty_preset(self, name: str, preset_key: str = 'preset_1') -> dict:
        """Returns an empty preset structure. Template name matches preset key."""
        # Each preset has its own template file(s) with matching name
        return {
            'name': name,
            'company': {
                'name': '',
                'tagline': '',
                'logo': '',
                'logo_width': 40,
                'show_name': True,
                'show_tagline': True,
                'show_logo': True
            },
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
                'template': preset_key,
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
                'vat_type': 'german_vat',  # Options: 'none', 'kleinunternehmer', 'german_vat'
                'tax_rate': 19,
                'payment_days': 14,
                'language': 'de'
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
        """Sets the active preset key and persists it to disk."""
        if preset_key in self.config.get('presets', {}):
            self.config['active_preset'] = preset_key
            self._save_config()

    def get_preset(self, preset_key: str) -> dict:
        """Returns the configuration dict for a specific preset."""
        return self.config.get('presets', {}).get(preset_key, self._get_empty_preset("Unknown", preset_key))

    def get_active_preset(self) -> dict:
        """Returns the configuration dict for the active preset."""
        return self.get_preset(self.get_active_preset_name())

    def get_llm_config(self) -> dict:
        """Returns the LLM configuration."""
        return self.config.get('llm', DEFAULT_LLM_CONFIG.copy())

    def set_llm_config(self, llm_config: dict):
        """Sets the LLM configuration."""
        self.config['llm'] = llm_config

    def is_llm_configured(self) -> bool:
        """Check if the LLM service is properly configured with an API key."""
        llm_config = self.get_llm_config()
        api_key = llm_config.get('api_key', '')
        return bool(api_key and api_key.strip())

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
        
        # Check relative to logos dir (for stored logos)
        p = self.logos_dir / path
        if p.exists():
            return p
            
        # Check relative to project root (assets, etc.)
        p = self.project_root / path
        if p.exists():
            return p
            
        return None

    def copy_logo(self, source_path: str, preset_key: str) -> str:
        """
        Copies a logo file to the internal logos directory.
        
        Args:
            source_path: The original path to the logo file
            preset_key: The preset key (used to create a unique filename)
            
        Returns:
            The relative path to the stored logo (relative to logos_dir),
            or the original path if copy fails or source doesn't exist.
        """
        if not source_path:
            return ""
        
        source = Path(os.path.expanduser(source_path))
        
        # If already in logos dir, return as-is (just the filename)
        try:
            if source.parent.resolve() == self.logos_dir.resolve():
                return source.name
        except Exception:
            pass
        
        # Check if source exists
        if not source.exists():
            # Try to resolve it first
            resolved = self.resolve_path(source_path)
            if resolved:
                source = resolved
            else:
                # Source doesn't exist, return original path
                return source_path
        
        # Create unique filename: preset_key + original extension
        suffix = source.suffix.lower()
        target_name = f"{preset_key}_logo{suffix}"
        target_path = self.logos_dir / target_name
        
        try:
            # Ensure logos dir exists
            self.logos_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy the file
            shutil.copy2(source, target_path)
            
            # Return just the filename (will be resolved via logos_dir)
            return target_name
        except Exception as e:
            print(f"Warning: Could not copy logo to internal storage: {e}")
            return source_path

    # -------------------------------------------------------------------------
    # Preset CRUD Operations
    # -------------------------------------------------------------------------

    def _generate_preset_key(self) -> str:
        """Generates a unique preset key using timestamp."""
        return f"profile_{int(time.time() * 1000)}"

    def _find_template_file(self, template_name: str, extension: str) -> Path:
        """
        Find a template file, prioritizing user config then app templates.
        Returns the path if found, None otherwise.
        """
        filename = f"{template_name}.{extension}"
        
        # 1. Check user config templates dir
        user_path = self.templates_dir / filename
        if user_path.exists():
            return user_path
            
        # 2. Check app templates dir
        app_path = get_templates_path() / filename
        if app_path.exists():
            return app_path
            
        return None

    def _copy_template_files(self, source_key: str, target_key: str) -> tuple[bool, str]:
        """
        Copy template files (HTML and CSS) from source preset to target preset.
        Target files are stored in user config templates directory.
        
        Returns a tuple of (success, message).
        """
        # Ensure templates dir exists
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        copied_files = []
        errors = []
        
        for ext in ['html', 'css']:
            source_path = self._find_template_file(source_key, ext)
            if not source_path:
                errors.append(f"Source {ext.upper()} not found: {source_key}.{ext}")
                continue
            
            target_path = self.templates_dir / f"{target_key}.{ext}"
            
            # Don't copy if source and target are the same file
            if source_path.resolve() == target_path.resolve():
                continue
            
            try:
                shutil.copy2(source_path, target_path)
                copied_files.append(f"{target_key}.{ext}")
            except Exception as e:
                errors.append(f"Failed to copy {ext.upper()}: {e}")
        
        if errors:
            return (False, "; ".join(errors))
        elif copied_files:
            return (True, f"Template files copied: {', '.join(copied_files)}")
        else:
            return (True, "Templates already up to date")

    def _delete_template_files(self, preset_key: str) -> tuple[bool, str]:
        """
        Delete template files (HTML and CSS) for a preset from user config dir.
        Only deletes from user config dir, not from app templates.
        
        Returns a tuple of (success, message).
        """
        deleted_files = []
        errors = []
        
        for ext in ['html', 'css']:
            user_path = self.templates_dir / f"{preset_key}.{ext}"
            if user_path.exists():
                try:
                    user_path.unlink()
                    deleted_files.append(f"{preset_key}.{ext}")
                except Exception as e:
                    errors.append(f"Failed to delete {ext.upper()}: {e}")
        
        if errors:
            return (False, "; ".join(errors))
        elif deleted_files:
            return (True, f"Template files deleted: {', '.join(deleted_files)}")
        else:
            return (True, "No template files to delete")

    def get_preset_list(self) -> list[tuple[str, str]]:
        """
        Returns a list of (preset_key, preset_name) tuples for all presets,
        sorted by the user-defined order.
        """
        presets = self.config.get('presets', {})
        preset_order = self.config.get('preset_order', [])
        
        # Ensure order list is valid (contains only existing keys)
        ordered_keys = [k for k in preset_order if k in presets]
        
        # Add any presets that might be missing from the order list (fallback)
        for key in presets:
            if key not in ordered_keys:
                ordered_keys.append(key)
                
        result = []
        for key in ordered_keys:
            name = presets[key].get('name', key)
            result.append((key, name))
            
        return result

    def create_preset(self, name: str, source_key: str = None) -> tuple[str, str]:
        """
        Creates a new preset by copying from source_key (or active preset if None).
        Also copies the template files.
        
        Returns a tuple of (new_preset_key, error_message or None).
        """
        if source_key is None:
            source_key = self.get_active_preset_name()
        
        source_preset = self.config.get('presets', {}).get(source_key)
        if not source_preset:
            return (None, f"Source preset '{source_key}' not found")
        
        # Generate unique key
        new_key = self._generate_preset_key()
        
        # Deep copy the source preset
        new_preset = copy.deepcopy(source_preset)
        new_preset['name'] = name
        # Update template to match new key
        if 'layout' not in new_preset:
            new_preset['layout'] = {}
        new_preset['layout']['template'] = new_key
        
        # Reset quotation counter for new preset
        if 'quotation_number' in new_preset:
            new_preset['quotation_number']['counter'] = 0
            new_preset['quotation_number']['last_reset_year'] = None
            new_preset['quotation_number']['last_reset_month'] = None
        
        # Copy template files
        success, message = self._copy_template_files(source_key, new_key)
        if not success:
            return (None, f"Failed to copy templates: {message}")
        
        # Add to config
        self.config.setdefault('presets', {})[new_key] = new_preset
        
        # Add to order
        if 'preset_order' not in self.config:
            self.config['preset_order'] = []
        self.config['preset_order'].append(new_key)
        
        return (new_key, None)

    def duplicate_preset(self, source_key: str, new_name: str = None) -> tuple[str, str]:
        """
        Duplicates an existing preset with a new name.
        If new_name is None, appends " (Copy)" to the source name.
        
        Returns a tuple of (new_preset_key, error_message or None).
        """
        source_preset = self.config.get('presets', {}).get(source_key)
        if not source_preset:
            return (None, f"Source preset '{source_key}' not found")
        
        if new_name is None:
            source_name = source_preset.get('name', source_key)
            new_name = f"{source_name} (Copy)"
        
        return self.create_preset(new_name, source_key)

    def delete_preset(self, preset_key: str) -> tuple[bool, str]:
        """
        Deletes a preset and its template files.
        Cannot delete the last remaining preset.
        
        Returns a tuple of (success, error_message or None).
        """
        presets = self.config.get('presets', {})
        
        if preset_key not in presets:
            return (False, f"Preset '{preset_key}' not found")
        
        if len(presets) <= 1:
            return (False, "Cannot delete the last preset")
        
        # Delete template files (only from user config dir)
        self._delete_template_files(preset_key)
        
        # Remove from config
        del presets[preset_key]
        
        # Remove from order
        if 'preset_order' in self.config:
            if preset_key in self.config['preset_order']:
                self.config['preset_order'].remove(preset_key)
        
        # If active preset was deleted, switch to first available
        if self.config.get('active_preset') == preset_key:
            first_key = next(iter(presets.keys()))
            self.config['active_preset'] = first_key
        
        return (True, None)

    def export_preset(self, preset_key: str, export_path: str, preset_data: dict = None) -> tuple[bool, str]:
        """
        Exports a preset to a zip file containing config, templates, and logo.
        If preset_data is provided, it uses that configuration (useful for exporting unsaved changes).
        Otherwise, it uses the stored configuration for preset_key.
        """
        if preset_data is None:
            preset_data = self.config.get('presets', {}).get(preset_key)
            
        if not preset_data:
            return (False, f"Preset data not found for '{preset_key}'")

        try:
            # Make a copy to modify for export
            export_data = copy.deepcopy(preset_data)
            
            with zipfile.ZipFile(export_path, 'w') as zf:
                # 1. Handle logo - include in export if exists
                logo_path_str = preset_data.get('company', {}).get('logo', '')
                if logo_path_str:
                    logo_path = self.resolve_path(logo_path_str)
                    if logo_path and logo_path.exists():
                        # Store logo with its original extension
                        logo_arcname = f"logo{logo_path.suffix.lower()}"
                        zf.write(logo_path, arcname=logo_arcname)
                        # Update export config to reference the archived logo name
                        export_data['company']['logo'] = logo_arcname
                
                # 2. Write profile config
                zf.writestr('profile.yaml', yaml.dump(export_data, allow_unicode=True, sort_keys=False))

                # 3. Write template files
                template_name = preset_data.get('layout', {}).get('template', preset_key)
                
                for ext in ['html', 'css']:
                    file_path = self._find_template_file(template_name, ext)
                    if file_path:
                        # Store as template.html / template.css for portable import
                        zf.write(file_path, arcname=f"template.{ext}")
            
            return (True, None)
        except Exception as e:
            return (False, str(e))

    def import_preset(self, import_path: str) -> tuple[str, str]:
        """
        Imports a preset from a zip file.
        Returns (new_preset_key, error_message).
        """
        if not os.path.exists(import_path):
            return (None, "File not found")

        try:
            with zipfile.ZipFile(import_path, 'r') as zf:
                files = zf.namelist()
                
                # 1. Read config
                if 'profile.yaml' not in files:
                    return (None, "Invalid profile archive: profile.yaml missing")
                
                try:
                    profile_data = yaml.safe_load(zf.read('profile.yaml'))
                except yaml.YAMLError:
                    return (None, "Invalid profile.yaml format")
                    
                if not profile_data or not isinstance(profile_data, dict):
                    return (None, "Invalid profile configuration")

                # 2. Generate new key
                new_key = self._generate_preset_key()
                
                # 3. Update profile data with new key and ensure unique name
                if 'layout' not in profile_data:
                    profile_data['layout'] = {}
                profile_data['layout']['template'] = new_key
                
                # Check for name collision and append (Imported) if needed
                original_name = profile_data.get('name', 'Imported Profile')
                existing_names = [p.get('name') for p in self.config.get('presets', {}).values()]
                if original_name in existing_names:
                    profile_data['name'] = f"{original_name} (Imported)"
                
                # 4. Extract and save templates
                self.templates_dir.mkdir(parents=True, exist_ok=True)
                
                # Determine which files to extract
                html_source = 'template.html' if 'template.html' in files else next((f for f in files if f.endswith('.html')), None)
                css_source = 'template.css' if 'template.css' in files else next((f for f in files if f.endswith('.css')), None)
                
                if html_source:
                    with open(self.templates_dir / f"{new_key}.html", 'wb') as f:
                        f.write(zf.read(html_source))
                else:
                    # Fallback: Create basic HTML if missing
                    with open(self.templates_dir / f"{new_key}.html", 'w', encoding='utf-8') as f:
                        f.write("<!-- Imported template placeholder -->\n{{ content }}")

                if css_source:
                    with open(self.templates_dir / f"{new_key}.css", 'wb') as f:
                        f.write(zf.read(css_source))
                else:
                    # Fallback: Create empty CSS if missing
                    with open(self.templates_dir / f"{new_key}.css", 'w', encoding='utf-8') as f:
                        f.write("/* Imported CSS placeholder */")

                # 5. Extract and save logo if present
                logo_files = [f for f in files if f.startswith('logo.') or f.startswith('logo')]
                logo_source = next((f for f in logo_files if any(f.endswith(ext) for ext in ['.svg', '.png', '.jpg', '.jpeg'])), None)
                
                if logo_source:
                    self.logos_dir.mkdir(parents=True, exist_ok=True)
                    logo_ext = Path(logo_source).suffix.lower()
                    logo_filename = f"{new_key}_logo{logo_ext}"
                    logo_target = self.logos_dir / logo_filename
                    
                    with open(logo_target, 'wb') as f:
                        f.write(zf.read(logo_source))
                    
                    # Update profile data to reference the stored logo
                    if 'company' not in profile_data:
                        profile_data['company'] = {}
                    profile_data['company']['logo'] = logo_filename

                # 6. Save to config
                self.config.setdefault('presets', {})[new_key] = profile_data
                
                # Add to order
                if 'preset_order' not in self.config:
                    self.config['preset_order'] = []
                self.config['preset_order'].append(new_key)
                
                self._save_config()
                
                return (new_key, None)

        except Exception as e:
            return (None, f"Import failed: {str(e)}")

    def rename_preset(self, preset_key: str, new_name: str) -> tuple[bool, str]:
        """
        Renames a preset (changes the display name, not the key).
        
        Returns a tuple of (success, error_message or None).
        """
        preset = self.config.get('presets', {}).get(preset_key)
        if not preset:
            return (False, f"Preset '{preset_key}' not found")
        
        preset['name'] = new_name
        return (True, None)

# Global instance
config = ConfigLoader()
