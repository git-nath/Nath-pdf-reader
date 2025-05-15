"""Settings management for the application."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

# Default settings
DEFAULT_SETTINGS = {
    'theme': 'light',  # 'light' or 'dark'
    'brightness': 1.0,  # 0.0 to 1.0
    'recent_files': [],  # List of recently opened files
    'window_size': [1024, 768],  # [width, height]
    'window_position': [100, 100],  # [x, y]
    'zoom_level': 1.0,  # Zoom level
    'default_directory': str(Path.home() / 'Documents'),  # Default directory for file dialogs
}

class SettingsManager:
    """Manages application settings with persistence to disk."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize the settings manager.
        
        Args:
            config_dir: Directory to store the settings file. If None, uses a default location.
        """
        if config_dir is None:
            # Use platform-appropriate config directory
            if os.name == 'nt':  # Windows
                config_dir = os.getenv('APPDATA', os.path.expanduser('~'))
                config_dir = os.path.join(config_dir, 'NathFileReader')
            else:  # macOS/Linux
                config_dir = os.path.join(os.path.expanduser('~'), '.config', 'nathreader')
        
        self.config_dir = Path(config_dir)
        self.settings_file = self.config_dir / 'settings.json'
        self.settings: Dict[str, Any] = {}
        self.load()
    
    def load(self) -> None:
        """Load settings from disk."""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
            else:
                self.settings = DEFAULT_SETTINGS.copy()
                self.save()
        except (json.JSONDecodeError, IOError):
            # If there's an error loading the settings, use defaults
            self.settings = DEFAULT_SETTINGS.copy()
    
    def save(self) -> None:
        """Save current settings to disk."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving settings: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value.
        
        Args:
            key: The setting key.
            default: Default value if the key doesn't exist.
            
        Returns:
            The setting value or the default if not found.
        """
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any, save: bool = True) -> None:
        """Set a setting value.
        
        Args:
            key: The setting key.
            value: The value to set.
            save: Whether to save the settings to disk immediately.
        """
        self.settings[key] = value
        if save:
            self.save()
    
    def add_recent_file(self, filepath: str, max_recent: int = 10) -> None:
        """Add a file to the recent files list.
        
        Args:
            filepath: Path to the recently opened file.
            max_recent: Maximum number of recent files to keep.
        """
        recent_files = self.get('recent_files', [])
        
        # Remove if already in the list
        if filepath in recent_files:
            recent_files.remove(filepath)
        
        # Add to the beginning
        recent_files.insert(0, filepath)
        
        # Trim the list if it's too long
        if len(recent_files) > max_recent:
            recent_files = recent_files[:max_recent]
        
        self.set('recent_files', recent_files)
    
    def clear_recent_files(self) -> None:
        """Clear the list of recent files."""
        self.set('recent_files', [])
