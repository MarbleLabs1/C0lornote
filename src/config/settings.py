"""
C0lorNote Settings Module

This module handles loading, saving, and managing application settings.
Settings are stored in YAML format for better readability and maintenance.
"""

import os
import yaml
import logging
from pathlib import Path

# Get the application's config directory
USER_HOME = str(Path.home())
APP_CONFIG_DIR = os.path.join(USER_HOME, ".config", "c0lornote")
CONFIG_FILE = os.path.join(APP_CONFIG_DIR, "settings.yaml")
DEFAULT_DB_PATH = os.path.join(APP_CONFIG_DIR, "notes.db")

# Default settings
DEFAULT_SETTINGS = {
    # Theme settings
    "theme": "arc",  # Default theme from ttkthemes
    "dark_mode": False,  # Light mode by default
    "use_system_theme": True,  # Try to use system theme by default
    
    # Window settings
    "window_width": 1000,
    "window_height": 700,
    "window_x": None,  # Center window by default
    "window_y": None,
    "maximized": False,
    
    # Font settings
    "note_font_family": "DejaVu Sans",  # Default system font
    "note_font_size": 11,
    "editor_font_family": "DejaVu Sans Mono",
    "editor_font_size": 12,
    "sidebar_font_family": "DejaVu Sans",
    "sidebar_font_size": 10,
    
    # Application behavior
    "autosave_interval": 300,  # Seconds
    "confirm_on_delete": True,
    "show_timestamps": True,
    "rich_text_editing": True,
    
    # Recent files
    "last_opened_notes": [],  # List of note IDs
    "last_selected_note": None,
    
    # Database settings
    "database_path": DEFAULT_DB_PATH,
    
    # Backup settings
    "enable_backups": True,
    "backup_directory": os.path.join(APP_CONFIG_DIR, "backups"),
    "backup_interval": 86400,  # Daily in seconds
    "max_backups": 5,  # Keep last 5 backups
}


def ensure_config_dir():
    """Ensure that the configuration directory exists"""
    try:
        if not os.path.exists(APP_CONFIG_DIR):
            os.makedirs(APP_CONFIG_DIR, exist_ok=True)
            
        if not os.path.exists(DEFAULT_SETTINGS["backup_directory"]):
            os.makedirs(DEFAULT_SETTINGS["backup_directory"], exist_ok=True)
            
        return True
    except Exception as e:
        logging.error(f"Failed to create configuration directory: {e}")
        return False


def load_settings():
    """
    Load settings from YAML file or return defaults if the file doesn't exist
    
    Returns:
        dict: Application settings dictionary
    """
    # Make sure config directory exists
    ensure_config_dir()
    
    # If the config file doesn't exist, create it with defaults
    if not os.path.exists(CONFIG_FILE):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()
    
    try:
        with open(CONFIG_FILE, 'r') as file:
            settings = yaml.safe_load(file)
            
        # Merge with defaults to ensure all settings exist
        # This helps when new settings are added in updates
        merged_settings = DEFAULT_SETTINGS.copy()
        if settings and isinstance(settings, dict):
            merged_settings.update(settings)
            
        return merged_settings
    except Exception as e:
        logging.error(f"Error loading settings: {e}")
        return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    """
    Save settings to YAML file
    
    Args:
        settings (dict): Settings dictionary to save
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure config directory exists
        ensure_config_dir()
        
        with open(CONFIG_FILE, 'w') as file:
            yaml.dump(settings, file, default_flow_style=False)
        return True
    except Exception as e:
        logging.error(f"Error saving settings: {e}")
        return False


def get_setting(key, default=None):
    """
    Get a specific setting with fallback to provided default or the DEFAULT_SETTINGS
    
    Args:
        key (str): Setting key to retrieve
        default: Default value if setting doesn't exist
        
    Returns:
        The setting value or default
    """
    settings = load_settings()
    if key in settings:
        return settings[key]
    
    # If default is provided, use it, otherwise try DEFAULT_SETTINGS
    if default is not None:
        return default
    
    return DEFAULT_SETTINGS.get(key)


def update_setting(key, value):
    """
    Update a single setting and save to file
    
    Args:
        key (str): Setting key to update
        value: New value for the setting
        
    Returns:
        bool: True if successful, False otherwise
    """
    settings = load_settings()
    settings[key] = value
    return save_settings(settings)


def reset_to_defaults():
    """
    Reset all settings to default values
    
    Returns:
        bool: True if successful, False otherwise
    """
    return save_settings(DEFAULT_SETTINGS.copy())

