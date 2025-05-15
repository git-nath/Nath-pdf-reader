"""Status bar component for the PDF viewer."""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, Any

class StatusBar(ttk.Frame):
    """Status bar for the PDF viewer."""
    
    def __init__(self, parent, **kwargs):
        """Initialize the status bar.
        
        Args:
            parent: Parent widget.
            **kwargs: Additional arguments to pass to the parent class.
        """
        super().__init__(parent, **{'style': 'Statusbar.TFrame', **kwargs})
        self._vars: Dict[str, tk.StringVar] = {}
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the status bar UI components."""
        # Configure the grid
        self.columnconfigure(0, weight=1)
        
        # Status message (left-aligned)
        self.status_var = tk.StringVar()
        status_label = ttk.Label(
            self,
            textvariable=self.status_var,
            anchor='w',
            style='Statusbar.TLabel'
        )
        status_label.grid(row=0, column=0, sticky='we', padx=5, pady=2)
        
        # Zoom level (right-aligned)
        self.zoom_var = tk.StringVar(value='100%')
        zoom_label = ttk.Label(
            self,
            textvariable=self.zoom_var,
            anchor='e',
            style='Statusbar.TLabel',
            width=8
        )
        zoom_label.grid(row=0, column=1, sticky='e', padx=5, pady=2)
        
        # Page size (right-aligned)
        self.size_var = tk.StringVar(value='-')
        size_label = ttk.Label(
            self,
            textvariable=self.size_var,
            anchor='e',
            style='Statusbar.TLabel',
            width=15
        )
        size_label.grid(row=0, column=2, sticky='e', padx=5, pady=2)
        
        # Document info (right-aligned)
        self.info_var = tk.StringVar(value='')
        info_label = ttk.Label(
            self,
            textvariable=self.info_var,
            anchor='e',
            style='Statusbar.TLabel',
            width=30
        )
        info_label.grid(row=0, column=3, sticky='e', padx=5, pady=2)
    
    def set_status(self, message: str) -> None:
        """Set the status message.
        
        Args:
            message: The message to display.
        """
        self.status_var.set(message)
    
    def set_zoom(self, zoom: float) -> None:
        """Set the zoom level display.
        
        Args:
            zoom: The zoom level as a multiplier (e.g., 1.0 for 100%).
        """
        self.zoom_var.set(f"{int(zoom * 100)}%")
    
    def set_page_size(self, width: int, height: int) -> None:
        """Set the page size display.
        
        Args:
            width: Page width in pixels.
            height: Page height in pixels.
        """
        self.size_var.set(f"{width} × {height} px")
    
    def set_document_info(self, info: str) -> None:
        """Set the document information.
        
        Args:
            info: Document information to display.
        """
        self.info_var.set(info)
    
    def clear(self) -> None:
        """Clear all status information."""
        self.status_var.set('')
        self.zoom_var.set('')
        self.size_var.set('')
        self.info_var.set('')
