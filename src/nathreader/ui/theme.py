"""Theme and appearance management for the application."""

from typing import Dict, Any, Optional, Literal
import customtkinter as ctk
from pathlib import Path
import json
import os
import tkinter as tk
from tkinter import ttk

ThemeType = Literal['light', 'dark', 'system']

class ThemeManager:
    """Manages the application's theme and appearance settings."""
    
    def __init__(self, settings_manager):
        """Initialize the theme manager.
        
        Args:
            settings_manager: The settings manager instance.
        """
        self.settings = settings_manager
        self.current_theme: ThemeType = self.settings.get('theme', 'system')
        self._themes: Dict[str, Dict[str, Any]] = {
            'light': {
                'name': 'Light',
                'bg': '#f0f0f0',
                'fg': '#333333',
                'text': '#000000',
                'accent': '#1a73e8',
                'accent_hover': '#0d62c9',
                'accent_pressed': '#0a4e9e',
                'border': '#cccccc',
                'canvas': '#ffffff',
                'button': '#e0e0e0',
                'button_hover': '#d0d0d0',
                'button_active': '#c0c0c0',
                'scrollbar': '#c1c1c1',
                'scrollbar_hover': '#a8a8a8',
            },
            'dark': {
                'name': 'Dark',
                'bg': '#1e1e1e',
                'fg': '#e0e0e0',
                'text': '#ffffff',
                'accent': '#5b9cf8',
                'accent_hover': '#7aacf9',
                'accent_pressed': '#3a8bf7',
                'border': '#444444',
                'canvas': '#252526',
                'button': '#3c3c3c',
                'button_hover': '#4c4c4c',
                'button_active': '#5c5c5c',
                'scrollbar': '#4a4a4a',
                'scrollbar_hover': '#5a5a5a',
            }
        }
        
        # Initialize CTk theme
        self._setup_ctk_theme()
    
    def _setup_ctk_theme(self) -> None:
        """Set up the CustomTkinter theme."""
        # Set appearance mode (light/dark)
        ctk.set_appearance_mode(self.current_theme.capitalize())
        
        # Set default color theme (blue, green, dark-blue)
        ctk.set_default_color_theme("blue")
        
        # Configure custom styles
        self._configure_styles()
    
    def _configure_styles(self) -> None:
        """Configure custom styles for widgets."""
        theme = self._themes[self.current_theme if self.current_theme != 'system' else 'light']
        
        # Create a style object for ttk widgets
        style = ttk.Style()
        
        # Configure main frame style
        style.configure('Main.TFrame', background=theme['bg'])
        
        # Configure button styles
        style.configure('Toolbutton.TButton',
                      background=theme['button'],
                      foreground=theme['text'],
                      borderwidth=1,
                      relief='flat')
        
        style.map('Toolbutton.TButton',
                background=[('active', theme['button_hover']),
                           ('pressed', theme['button_active'])],
                relief=[('pressed', 'sunken'), ('!pressed', 'flat')])
        
        # Configure entry style
        style.configure('TEntry',
                      fieldbackground=theme['canvas'],
                      foreground=theme['text'],
                      insertcolor=theme['text'],
                      borderwidth=1,
                      relief='solid')
        
        # Configure scrollbar style
        style.configure('TScrollbar',
                      background=theme['scrollbar'],
                      troughcolor=theme['bg'],
                      borderwidth=0,
                      arrowsize=12)
        
        style.map('TScrollbar',
                 background=[('active', theme['scrollbar_hover'])])
    
    def get_theme(self, theme_name: Optional[ThemeType] = None) -> Dict[str, Any]:
        """Get theme colors for a specific theme.
        
        Args:
            theme_name: Name of the theme ('light', 'dark', or 'system').
                       If None, returns the current theme.
        
        Returns:
            Dict[str, Any]: A dictionary of theme colors and settings.
        """
        if theme_name is None:
            theme_name = self.current_theme
        
        if theme_name == 'system':
            # Use light theme as fallback for system theme
            return self._themes['light']
        
        return self._themes.get(theme_name, {})
    
    def set_theme(self, theme_name: ThemeType, save: bool = True) -> bool:
        """Set the current theme.
        
        Args:
            theme_name: Name of the theme ('light', 'dark', or 'system').
            save: Whether to save the theme preference.
            
        Returns:
            bool: True if the theme was changed, False otherwise.
        """
        if theme_name not in ('light', 'dark', 'system'):
            return False
            
        if theme_name != self.current_theme:
            self.current_theme = theme_name
            
            # Update CTk appearance mode
            ctk.set_appearance_mode(theme_name.capitalize())
            
            # Reconfigure styles
            self._configure_styles()
            
            # Save the preference
            if save:
                self.settings.set('theme', theme_name)
            
            return True
        
        return False
    
    def toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        if self.current_theme == 'dark':
            self.set_theme('light')
        else:
            self.set_theme('dark')
    
    @property
    def current_theme_colors(self) -> Dict[str, Any]:
        """Get the colors for the current theme."""
        return self.get_theme()


def load_fonts() -> None:
    """Load custom fonts for the application."""
    # This is a placeholder for future font loading functionality
    pass
