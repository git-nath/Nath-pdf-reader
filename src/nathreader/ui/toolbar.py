"""Toolbar component for the PDF viewer."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Callable, Dict, Any
from pathlib import Path
import customtkinter as ctk

class Toolbar(ttk.Frame):
    """Main toolbar for the PDF viewer."""
    
    def __init__(self, parent, theme_manager, **kwargs):
        """Initialize the toolbar.
        
        Args:
            parent: Parent widget.
            theme_manager: Theme manager instance.
            **kwargs: Additional arguments to pass to the parent class.
        """
        super().__init__(parent, **{'style': 'Toolbar.TFrame', **kwargs})
        self.theme = theme_manager
        self._callbacks: Dict[str, Callable] = {}
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the toolbar UI components."""
        # File operations frame
        file_frame = ttk.Frame(self, style='Toolbar.TFrame')
        file_frame.pack(side='left', padx=2, pady=2)
        
        # Navigation frame
        nav_frame = ttk.Frame(self, style='Toolbar.TFrame')
        nav_frame.pack(side='left', padx=10, pady=2)
        
        # View frame
        view_frame = ttk.Frame(self, style='Toolbar.TFrame')
        view_frame.pack(side='left', padx=10, pady=2)
        
        # Tools frame
        tools_frame = ttk.Frame(self, style='Toolbar.TFrame')
        tools_frame.pack(side='right', padx=2, pady=2)
        
        # File buttons
        self._create_button(file_frame, 'Open', 'open_file', '📂')
        
        # Navigation buttons
        self._create_button(nav_frame, 'Previous', 'prev_page', '⬅️')
        self._create_button(nav_frame, 'Next', 'next_page', '➡️')
        
        # View buttons
        self._create_button(view_frame, 'Zoom In', 'zoom_in', '🔍+')
        self._create_button(view_frame, 'Zoom Out', 'zoom_out', '🔍-')
        self._create_button(view_frame, 'Fit Width', 'fit_width', '↔️')
        self._create_button(view_frame, 'Fit Page', 'fit_page', '⤢')
        
        # Brightness control
        brightness_frame = ttk.Frame(view_frame, style='Toolbar.TFrame')
        brightness_frame.pack(side='left', padx=5)
        
        # Brightness label
        ttk.Label(brightness_frame, text='🔆', style='Toolbar.TLabel').pack(side='left')
        
        # Brightness slider
        self.brightness_slider = ttk.Scale(
            brightness_frame,
            from_=0.1,
            to=2.0,
            value=1.0,
            orient='horizontal',
            length=80,
            command=self._on_brightness_change
        )
        self.brightness_slider.pack(side='left', padx=2)
        self.brightness_slider.set(1.0)  # Default brightness
        
        # Tools buttons
        self._create_button(tools_frame, 'Search', 'search', '🔍')
        self._create_button(tools_frame, 'Outline', 'outline', '📑')
        self._create_button(tools_frame, 'Bookmarks', 'bookmarks', '🔖')
        self._create_button(tools_frame, 'Settings', 'settings', '⚙️')
        
        # Page counter
        self.page_var = tk.StringVar(value='0 / 0')
        page_label = ttk.Label(
            nav_frame,
            textvariable=self.page_var,
            style='Toolbar.TLabel',
            font=('Segoe UI', 10)
        )
        page_label.pack(side='left', padx=5)
    
    def _on_brightness_change(self, value):
        """Handle brightness slider change."""
        try:
            brightness = float(value)
            self._trigger_callback('set_brightness', brightness)
        except (ValueError, TypeError):
            pass
    
    def set_brightness(self, value: float) -> None:
        """Set the brightness slider value.
        
        Args:
            value: Brightness value (0.1 to 2.0)
        """
        self.brightness_slider.set(min(max(0.1, float(value)), 2.0))
    
    def _create_button(self, parent, text, command, symbol=None, tooltip=None):
        """Create a toolbar button.
        
        Args:
            parent: Parent widget.
            text: Button text.
            command: Command to execute when clicked.
            symbol: Optional symbol to display instead of text.
            tooltip: Optional tooltip text.
            
        Returns:
            ttk.Button: The created button.
        """
        if symbol:
            btn = ttk.Button(parent, text=symbol, width=2, command=lambda: self._trigger_callback(command))
        else:
            btn = ttk.Button(parent, text=text, command=lambda: self._trigger_callback(command))
            
        btn.pack(side='left', padx=1, pady=1)
        
        if tooltip:
            self._create_tooltip(btn, tooltip)
            
        return btn
    
    def _add_tooltip(self, widget: ttk.Widget, text: str) -> None:
        """Add a tooltip to a widget.
        
        Args:
            widget: The widget to add the tooltip to.
            text: The tooltip text.
        """
        # This is a placeholder for tooltip functionality
        # In a real implementation, you would use a tooltip library or implement one
        pass
    
    def _handle_command(self, command: str) -> None:
        """Handle a toolbar button click.
        
        Args:
            command: The command name.
        """
        if command in self._callbacks:
            self._callbacks[command]()
    
    def register_callback(self, event: str, callback: Callable) -> None:
        """Register a callback function for an event.
        
        Args:
            event: Event name (e.g., 'open_file', 'prev_page').
            callback: Function to call when the event is triggered.
        """
        self._callbacks[event] = callback
        
        # Special handling for brightness control
        if event == 'set_brightness':
            self.brightness_slider.config(command=lambda v: callback(float(v)))
    
    def _trigger_callback(self, event: str, *args, **kwargs) -> Any:
        """Trigger a callback function.
        
        Args:
            event: Event name.
            *args: Positional arguments to pass to the callback.
            **kwargs: Keyword arguments to pass to the callback.
            
        Returns:
            Any: The return value of the callback function, or None if no callback is registered.
        """
        if event in self._callbacks:
            return self._callbacks[event](*args, **kwargs)
        return None
    
    def update_page_counter(self, current: int, total: int) -> None:
        """Update the page counter.
        
        Args:
            current: Current page number (1-based).
            total: Total number of pages.
        """
        self.page_var.set(f"{current} / {total}")
    
    def set_theme(self, theme_name: str) -> None:
        """Update the toolbar's appearance based on the current theme.
        
        Args:
            theme_name: The name of the theme ('light', 'dark', or 'system').
        """
        # This would update the toolbar's appearance based on the theme
        # Implementation depends on how theming is handled in your application
        pass
