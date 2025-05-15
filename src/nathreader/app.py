"""Main application class for the PDF reader."""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple, Callable
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk

# Local imports
from nathreader.core.document import Document, DocumentFactory
from nathreader.ui.toolbar import Toolbar
from nathreader.ui.statusbar import StatusBar
from nathreader.ui.theme import ThemeManager
from nathreader.ui.settings_dialog import SettingsDialog
from nathreader.utils.settings import SettingsManager
from nathreader.utils.file_utils import ensure_directory_exists, is_supported_file

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PDFReaderApp(ctk.CTk):
    """Main application class for the PDF reader."""
    
    def __init__(self):
        """Initialize the application."""
        super().__init__()
        
        # Initialize settings
        self.settings = SettingsManager()
        
        # Set up the main window
        self.title("NathReader")
        self.geometry("1024x768")
        self.minsize(800, 600)
        
        # Initialize theme manager
        self.theme = ThemeManager(self.settings)
        
        # Current document
        self.current_doc: Optional[Document] = None
        self.current_file: Optional[str] = None
        self.current_page: int = 0
        self.zoom_level: float = 1.0
        
        # Set up the UI
        self._setup_ui()
        
        # Bind window events
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<Control-o>", lambda e: self.open_document())
        self.bind("<Control-q>", lambda e: self.quit())
        self.bind("<F1>", lambda e: self.show_help())
        
        # Apply saved window geometry
        self._restore_window_geometry()
    
    def _setup_ui(self) -> None:
        """Set up the main application UI."""
        # Configure the grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create toolbar
        self.toolbar = Toolbar(self, self.theme)
        self.toolbar.grid(row=0, column=0, sticky='ew')
        
        # Register toolbar callbacks
        self.toolbar.register_callback('open_file', self.open_document)
        self.toolbar.register_callback('prev_page', self.prev_page)
        self.toolbar.register_callback('next_page', self.next_page)
        self.toolbar.register_callback('zoom_in', lambda: self.change_zoom(1.25))
        self.toolbar.register_callback('zoom_out', lambda: self.change_zoom(0.8))
        self.toolbar.register_callback('fit_width', self.fit_width)
        self.toolbar.register_callback('fit_page', self.fit_page)
        self.toolbar.register_callback('settings', self.show_settings)
        
        # Create main content area
        self.content_frame = ttk.Frame(self, style='Content.TFrame')
        self.content_frame.grid(row=1, column=0, sticky='nsew')
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Create canvas for PDF display
        self.canvas = tk.Canvas(
            self.content_frame,
            bg='white',
            highlightthickness=0
        )
        self.canvas.grid(row=0, column=0, sticky='nsew')
        
        # Add scrollbars
        self.v_scroll = ttk.Scrollbar(
            self.content_frame,
            orient='vertical',
            command=self.canvas.yview
        )
        self.v_scroll.grid(row=0, column=1, sticky='ns')
        
        self.h_scroll = ttk.Scrollbar(
            self.content_frame,
            orient='horizontal',
            command=self.canvas.xview
        )
        self.h_scroll.grid(row=1, column=0, sticky='ew')
        
        # Configure canvas scrolling
        self.canvas.configure(
            yscrollcommand=self.v_scroll.set,
            xscrollcommand=self.h_scroll.set
        )
        
        # Create frame for document pages
        self.pages_frame = ttk.Frame(self.canvas, style='Pages.TFrame')
        self.canvas.create_window((0, 0), window=self.pages_frame, anchor='nw')
        
        # Bind mouse wheel for scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Shift-MouseWheel>", self._on_shift_mousewheel)
        
        # Bind canvas resize
        self.pages_frame.bind("<Configure>", self._on_canvas_configure)
        
        # Create status bar
        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=2, column=0, sticky='ew')
        self.status_bar.set_status("Ready")
        
        # Update the UI based on the current theme
        self._update_theme()
    
    def _update_theme(self) -> None:
        """Update the UI based on the current theme."""
        colors = self.theme.current_theme_colors
        
        # Update canvas background
        self.canvas.configure(bg=colors['canvas'])
        
        # Update styles
        style = ttk.Style()
        style.configure('Content.TFrame', background=colors['bg'])
        style.configure('Pages.TFrame', background=colors['canvas'])
        
        # Update status bar
        self.status_bar.set_zoom(self.zoom_level * 100)
    
    def _restore_window_geometry(self) -> None:
        """Restore the window geometry from settings."""
        size = self.settings.get('window_size')
        position = self.settings.get('window_position')
        
        if size and len(size) == 2:
            self.geometry(f"{size[0]}x{size[1]}")
        
        if position and len(position) == 2:
            self.geometry(f"+{position[0]}+{position[1]}")
        else:
            # Center the window on screen
            self.update_idletasks()
            width = self.winfo_width()
            height = self.winfo_height()
            x = (self.winfo_screenwidth() // 2) - (width // 2)
            y = (self.winfo_screenheight() // 2) - (height // 2)
            self.geometry(f'+{x}+{y}')
        
        # Restore window state
        if self.settings.get('window_maximized', False):
            self.state('zoomed')
    
    def _save_window_geometry(self) -> None:
        """Save the current window geometry to settings."""
        if self.state() == 'zoomed':
            self.settings.set('window_maximized', True)
        else:
            self.settings.set('window_maximized', False)
            
            # Save window size and position
            self.settings.set('window_size', [self.winfo_width(), self.winfo_height()])
            self.settings.set('window_position', [self.winfo_x(), self.winfo_y()])
    
    def open_document(self, filepath: Optional[str] = None) -> None:
        """Open a document.
        
        Args:
            filepath: Path to the document to open. If None, shows a file dialog.
        """
        if filepath is None:
            # Show file dialog
            initial_dir = self.settings.get('default_directory', os.path.expanduser('~'))
            filetypes = [
                ('PDF Files', '*.pdf'),
                ('All Files', '*.*')
            ]
            
            filepath = filedialog.askopenfilename(
                title="Open Document",
                initialdir=initial_dir,
                filetypes=filetypes
            )
            
            if not filepath:
                return  # User cancelled
        
        # Check if the file exists
        if not os.path.isfile(filepath):
            messagebox.showerror("Error", f"File not found: {filepath}")
            return
        
        # Close current document if open
        if self.current_doc is not None:
            self.current_doc.close()
            self.current_doc = None
        
        try:
            # Create appropriate document handler
            doc = DocumentFactory.create_document(filepath)
            if doc is None:
                messagebox.showerror("Error", f"Unsupported file type: {os.path.splitext(filepath)[1]}")
                return
            
            # Load the document
            if not doc.load():
                raise Exception("Failed to load document")
            
            # Update document references
            self.current_doc = doc
            self.current_file = filepath
            self.current_page = 0
            
            # Update UI
            self.title(f"NathReader - {os.path.basename(filepath)}")
            self.status_bar.set_status(f"Opened: {os.path.basename(filepath)}")
            
            # Add to recent files
            self.settings.add_recent_file(filepath)
            
            # Display the first page
            self.show_page()
            
            # Update toolbar
            self.toolbar.update_page_counter(1, self.current_doc.page_count)
            
        except Exception as e:
            logger.exception("Error opening document")
            messagebox.showerror("Error", f"Failed to open document: {str(e)}")
    
    def show_page(self) -> None:
        """Display the current page."""
        if self.current_doc is None:
            return
        
        # Clear previous page
        for widget in self.pages_frame.winfo_children():
            widget.destroy()
        
        try:
            # Get the page as a PIL Image
            img = self.current_doc.get_page(self.current_page, self.zoom_level)
            if img is None:
                raise Exception("Failed to render page")
            
            # Convert PIL Image to PhotoImage using ImageTk
            from PIL import ImageTk
            
            # Convert image to RGB mode if it's not already
            if img.mode != 'RGB':
                img = img.convert('RGB')
                
            # Create a PhotoImage from the PIL Image
            self.current_image = ImageTk.PhotoImage(image=img)
            
            # Create a label to display the image
            label = ttk.Label(
                self.pages_frame,
                image=self.current_image,
                borderwidth=0
            )
            label.pack(padx=10, pady=10)
            
            # Update scroll region
            self.pages_frame.update_idletasks()
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
            
            # Update status bar
            self.status_bar.set_page_size(img.width, img.height)
            
        except Exception as e:
            logger.exception("Error displaying page")
            messagebox.showerror("Error", f"Failed to display page: {str(e)}")
    
    def prev_page(self) -> None:
        """Go to the previous page."""
        if self.current_doc is None or self.current_page <= 0:
            return
        
        self.current_page -= 1
        self.show_page()
        self.toolbar.update_page_counter(self.current_page + 1, self.current_doc.page_count)
    
    def next_page(self) -> None:
        """Go to the next page."""
        if self.current_doc is None or self.current_page >= self.current_doc.page_count - 1:
            return
        
        self.current_page += 1
        self.show_page()
        self.toolbar.update_page_counter(self.current_page + 1, self.current_doc.page_count)
    
    def change_zoom(self, factor: float) -> None:
        """Change the zoom level.
        
        Args:
            factor: Zoom factor (e.g., 1.25 for zoom in, 0.8 for zoom out).
        """
        if self.current_doc is None:
            return
        
        self.zoom_level *= factor
        self.zoom_level = max(0.1, min(self.zoom_level, 10.0))  # Limit zoom range
        
        # Update status bar
        self.status_bar.set_zoom(int(self.zoom_level * 100))
        
        # Redraw the current page
        self.show_page()
    
    def fit_width(self) -> None:
        """Fit the page width to the window."""
        if self.current_doc is None:
            return
        
        # Get the width of the canvas
        canvas_width = self.canvas.winfo_width() - 20  # Account for padding
        
        # Get the page size
        try:
            page = self.current_doc._document.load_page(self.current_page)
            page_width = page.rect.width
            
            # Calculate zoom level to fit width
            self.zoom_level = canvas_width / page_width
            
            # Update status bar
            self.status_bar.set_zoom(int(self.zoom_level * 100))
            
            # Redraw the page
            self.show_page()
            
        except Exception as e:
            logger.exception("Error fitting page width")
            messagebox.showerror("Error", f"Failed to fit page width: {str(e)}")
    
    def fit_page(self) -> None:
        """Fit the entire page to the window."""
        if self.current_doc is None:
            return
        
        # Get the size of the canvas
        canvas_width = self.canvas.winfo_width() - 20  # Account for padding
        canvas_height = self.canvas.winfo_height() - 20  # Account for padding
        
        # Get the page size
        try:
            page = self.current_doc._document.load_page(self.current_page)
            page_width = page.rect.width
            page_height = page.rect.height
            
            # Calculate zoom level to fit the entire page
            width_ratio = canvas_width / page_width
            height_ratio = canvas_height / page_height
            self.zoom_level = min(width_ratio, height_ratio)
            
            # Update status bar
            self.status_bar.set_zoom(int(self.zoom_level * 100))
            
            # Redraw the page
            self.show_page()
            
        except Exception as e:
            logger.exception("Error fitting page")
            messagebox.showerror("Error", f"Failed to fit page: {str(e)}")
    
    def show_settings(self) -> None:
        """Show the settings dialog."""
        dialog = SettingsDialog(self, self.settings, self.theme)
        dialog.set_callback(self._on_settings_changed)
        self.wait_window(dialog)
    
    def show_help(self) -> None:
        """Show the help dialog."""
        help_text = """NathReader - PDF Reader

Keyboard Shortcuts:
  Ctrl+O - Open document
  Ctrl+Q - Quit
  Left/Right Arrow - Navigate pages
  Ctrl++ - Zoom in
  Ctrl+- - Zoom out
  F1 - Show this help

For more information, visit our website.
"""
        messagebox.showinfo("Help", help_text)
    
    def _on_settings_changed(self, settings: Dict[str, Any]) -> None:
        """Handle settings changes.
        
        Args:
            settings: Dictionary of changed settings.
        """
        if 'theme' in settings:
            self.theme.set_theme(settings['theme'])
            self._update_theme()
        
        # Handle other setting changes as needed
        logger.info("Settings updated: %s", settings)
    
    def _on_canvas_configure(self, event: tk.Event) -> None:
        """Handle canvas resize events."""
        # Update the scroll region to match the size of the pages frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_mousewheel(self, event: tk.Event) -> None:
        """Handle mouse wheel events for vertical scrolling."""
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
    
    def _on_shift_mousewheel(self, event: tk.Event) -> None:
        """Handle shift+mouse wheel for horizontal scrolling."""
        if event.num == 4 or event.delta > 0:
            self.canvas.xview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.xview_scroll(1, "units")
    
    def _on_close(self) -> None:
        """Handle window close event."""
        # Save window geometry
        self._save_window_geometry()
        
        # Close the current document
        if self.current_doc is not None:
            self.current_doc.close()
        
        # Save settings
        self.settings.save()
        
        # Close the application
        self.destroy()

def main():
    """Main entry point for the application."""
    try:
        # Set DPI awareness on Windows
        if os.name == 'nt':
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        
        # Create and run the application
        app = PDFReaderApp()
        
        # Open file from command line if provided
        if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
            app.after(100, lambda: app.open_document(sys.argv[1]))
        
        app.mainloop()
        
    except Exception as e:
        logger.exception("Unhandled exception")
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
