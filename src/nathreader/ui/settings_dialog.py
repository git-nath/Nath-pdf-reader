"""Settings dialog for the PDF viewer."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional, Callable, List, Tuple
import customtkinter as ctk

class SettingsDialog(ctk.CTkToplevel):
    """A dialog for application settings."""
    
    def __init__(self, parent, settings_manager, theme_manager, **kwargs):
        """Initialize the settings dialog.
        
        Args:
            parent: Parent window.
            settings_manager: Settings manager instance.
            theme_manager: Theme manager instance.
            **kwargs: Additional arguments to pass to the parent class.
        """
        super().__init__(parent, **kwargs)
        
        self.settings = settings_manager
        self.theme = theme_manager
        self.callback = None
        
        self.title("Settings")
        self.geometry("600x500")
        self.resizable(True, True)
        
        # Make the dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Initialize UI
        self._setup_ui()
        
        # Center the dialog
        self._center_on_parent()
        
        # Bind the close event
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
    
    def _setup_ui(self) -> None:
        """Set up the settings dialog UI."""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Notebook for settings categories
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True, pady=(0, 10))
        
        # General tab
        self._create_general_tab()
        
        # Appearance tab
        self._create_appearance_tab()
        
        # PDF tab
        self._create_pdf_tab()
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=(5, 0))
        
        # OK button
        ok_btn = ttk.Button(
            btn_frame,
            text="OK",
            command=self._on_ok,
            style='Accent.TButton'
        )
        ok_btn.pack(side='right', padx=5)
        
        # Cancel button
        cancel_btn = ttk.Button(
            btn_frame,
            text="Cancel",
            command=self._on_cancel
        )
        cancel_btn.pack(side='right', padx=5)
        
        # Apply button
        apply_btn = ttk.Button(
            btn_frame,
            text="Apply",
            command=self._on_apply
        )
        apply_btn.pack(side='right', padx=5)
        
        # Reset button
        reset_btn = ttk.Button(
            btn_frame,
            text="Reset to Defaults",
            command=self._on_reset
        )
        reset_btn.pack(side='left')
    
    def _create_general_tab(self) -> None:
        """Create the General settings tab."""
        general_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(general_frame, text="General")
        
        # Startup settings
        startup_group = ttk.LabelFrame(
            general_frame,
            text="Startup",
            padding=(10, 5, 10, 10)
        )
        startup_group.pack(fill='x', pady=(0, 10))
        
        # Restore last session
        self.restore_session_var = tk.BooleanVar(
            value=self.settings.get('restore_session', True)
        )
        restore_session_cb = ttk.Checkbutton(
            startup_group,
            text="Restore last session on startup",
            variable=self.restore_session_var
        )
        restore_session_cb.pack(anchor='w', pady=2)
        
        # Check for updates
        self.check_updates_var = tk.BooleanVar(
            value=self.settings.get('check_updates', True)
        )
        check_updates_cb = ttk.Checkbutton(
            startup_group,
            text="Check for updates on startup",
            variable=self.check_updates_var
        )
        check_updates_cb.pack(anchor='w', pady=2)
        
        # File handling settings
        file_group = ttk.LabelFrame(
            general_frame,
            text="File Handling",
            padding=(10, 5, 10, 10)
        )
        file_group.pack(fill='x', pady=(0, 10))
        
        # Default directory
        ttk.Label(file_group, text="Default directory:").pack(anchor='w', pady=2)
        
        dir_frame = ttk.Frame(file_group)
        dir_frame.pack(fill='x', pady=2)
        
        self.default_dir_var = tk.StringVar(
            value=self.settings.get('default_directory', '')
        )
        dir_entry = ttk.Entry(dir_frame, textvariable=self.default_dir_var)
        dir_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        browse_btn = ttk.Button(
            dir_frame,
            text="Browse...",
            command=self._browse_directory
        )
        browse_btn.pack(side='right')
        
        # Recent files limit
        ttk.Label(
            file_group,
            text="Number of recent files to remember:"
        ).pack(anchor='w', pady=(10, 0))
        
        self.recent_files_var = tk.IntVar(
            value=self.settings.get('recent_files_limit', 10)
        )
        recent_files_spin = ttk.Spinbox(
            file_group,
            from_=1,
            to=50,
            textvariable=self.recent_files_var,
            width=5
        )
        recent_files_spin.pack(anchor='w', pady=2)
    
    def _create_appearance_tab(self) -> None:
        """Create the Appearance settings tab."""
        appearance_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(appearance_frame, text="Appearance")
        
        # Theme settings
        theme_group = ttk.LabelFrame(
            appearance_frame,
            text="Theme",
            padding=(10, 5, 10, 10)
        )
        theme_group.pack(fill='x', pady=(0, 10))
        
        # Theme selection
        ttk.Label(theme_group, text="Color theme:").pack(anchor='w', pady=2)
        
        self.theme_var = tk.StringVar(value=self.settings.get('theme', 'system'))
        
        theme_frame = ttk.Frame(theme_group)
        theme_frame.pack(fill='x', pady=2)
        
        themes = [
            ('Light', 'light'),
            ('Dark', 'dark'),
            ('System', 'system')
        ]
        
        for text, value in themes:
            rb = ttk.Radiobutton(
                theme_frame,
                text=text,
                variable=self.theme_var,
                value=value,
                command=self._on_theme_change
            )
            rb.pack(anchor='w', pady=2)
        
        # Font settings
        font_group = ttk.LabelFrame(
            appearance_frame,
            text="Font",
            padding=(10, 5, 10, 10)
        )
        font_group.pack(fill='x', pady=(0, 10))
        
        # Font family
        ttk.Label(font_group, text="Font family:").pack(anchor='w', pady=2)
        
        self.font_family_var = tk.StringVar(
            value=self.settings.get('font_family', 'Segoe UI')
        )
        font_family_combo = ttk.Combobox(
            font_group,
            textvariable=self.font_family_var,
            values=['Segoe UI', 'Arial', 'Helvetica', 'Times New Roman', 'Courier New'],
            state='readonly',
            width=20
        )
        font_family_combo.pack(anchor='w', pady=2)
        
        # Font size
        ttk.Label(font_group, text="Font size:").pack(anchor='w', pady=2)
        
        self.font_size_var = tk.IntVar(
            value=self.settings.get('font_size', 9)
        )
        font_size_spin = ttk.Spinbox(
            font_group,
            from_=8,
            to=24,
            textvariable=self.font_size_var,
            width=5
        )
        font_size_spin.pack(anchor='w', pady=2)
    
    def _create_pdf_tab(self) -> None:
        """Create the PDF settings tab."""
        pdf_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(pdf_frame, text="PDF")
        
        # Display settings
        display_group = ttk.LabelFrame(
            pdf_frame,
            text="Display",
            padding=(10, 5, 10, 10)
        )
        display_group.pack(fill='x', pady=(0, 10))
        
        # Default zoom
        ttk.Label(display_group, text="Default zoom:").pack(anchor='w', pady=2)
        
        self.default_zoom_var = tk.StringVar(
            value=self.settings.get('default_zoom', 'fit_width')
        )
        
        zoom_options = [
            ('Fit Page', 'fit_page'),
            ('Fit Width', 'fit_width'),
            ('50%', '0.5'),
            ('75%', '0.75'),
            ('100%', '1.0'),
            ('125%', '1.25'),
            ('150%', '1.5'),
            ('200%', '2.0'),
            ('300%', '3.0')
        ]
        
        zoom_frame = ttk.Frame(display_group)
        zoom_frame.pack(fill='x', pady=2)
        
        for text, value in zoom_options:
            rb = ttk.Radiobutton(
                zoom_frame,
                text=text,
                variable=self.default_zoom_var,
                value=value
            )
            rb.pack(anchor='w', pady=1)
        
        # Page layout
        ttk.Label(display_group, text="Page layout:").pack(anchor='w', pady=(10, 2))
        
        self.page_layout_var = tk.StringVar(
            value=self.settings.get('page_layout', 'single')
        )
        
        layout_frame = ttk.Frame(display_group)
        layout_frame.pack(fill='x', pady=2)
        
        layouts = [
            ('Single Page', 'single'),
            ('Continuous', 'continuous'),
            ('Two Pages', 'two'),
            ('Two Pages (Continuous)', 'two_continuous')
        ]
        
        for text, value in layouts:
            rb = ttk.Radiobutton(
                layout_frame,
                text=text,
                variable=self.page_layout_var,
                value=value
            )
            rb.pack(anchor='w', pady=1)
        
        # Rendering settings
        render_group = ttk.LabelFrame(
            pdf_frame,
            text="Rendering",
            padding=(10, 5, 10, 10)
        )
        render_group.pack(fill='x', pady=(0, 10))
        
        # Anti-aliasing
        self.antialias_var = tk.BooleanVar(
            value=self.settings.get('antialias', True)
        )
        antialias_cb = ttk.Checkbutton(
            render_group,
            text="Enable anti-aliasing",
            variable=self.antialias_var
        )
        antialias_cb.pack(anchor='w', pady=2)
        
        # Render hints
        ttk.Label(render_group, text="Render quality:").pack(anchor='w', pady=(10, 2))
        
        self.render_quality_var = tk.StringVar(
            value=self.settings.get('render_quality', 'high')
        )
        
        quality_frame = ttk.Frame(render_group)
        quality_frame.pack(fill='x', pady=2)
        
        qualities = [
            ('Best (slower)', 'high'),
            ('Balanced', 'medium'),
            ('Fast (lower quality)', 'low')
        ]
        
        for text, value in qualities:
            rb = ttk.Radiobutton(
                quality_frame,
                text=text,
                variable=self.render_quality_var,
                value=value
            )
            rb.pack(anchor='w', pady=1)
    
    def _browse_directory(self) -> None:
        """Open a directory selection dialog."""
        from tkinter import filedialog
        
        directory = filedialog.askdirectory(
            title="Select Default Directory",
            mustexist=True
        )
        
        if directory:
            self.default_dir_var.set(directory)
    
    def _on_theme_change(self) -> None:
        """Handle theme change."""
        theme = self.theme_var.get()
        # Apply theme preview if needed
        # This would depend on your theming system
        pass
    
    def _on_ok(self) -> None:
        """Handle OK button click."""
        self._apply_settings()
        self.destroy()
    
    def _on_apply(self) -> None:
        """Handle Apply button click."""
        self._apply_settings()
    
    def _on_cancel(self) -> None:
        """Handle Cancel button click."""
        self.destroy()
    
    def _on_reset(self) -> None:
        """Handle Reset to Defaults button click."""
        if messagebox.askyesno(
            "Reset Settings",
            "Are you sure you want to reset all settings to their default values?"
        ):
            # Reset settings to defaults
            self._load_defaults()
    
    def _load_defaults(self) -> None:
        """Load default settings."""
        # This would load default values into the UI
        # Implementation depends on your default settings structure
        pass
    
    def _apply_settings(self) -> None:
        """Apply the current settings."""
        # Save settings
        settings = {
            'theme': self.theme_var.get(),
            'restore_session': self.restore_session_var.get(),
            'check_updates': self.check_updates_var.get(),
            'default_directory': self.default_dir_var.get(),
            'recent_files_limit': self.recent_files_var.get(),
            'font_family': self.font_family_var.get(),
            'font_size': self.font_size_var.get(),
            'default_zoom': self.default_zoom_var.get(),
            'page_layout': self.page_layout_var.get(),
            'antialias': self.antialias_var.get(),
            'render_quality': self.render_quality_var.get()
        }
        
        # Save settings through the settings manager
        for key, value in settings.items():
            self.settings.set(key, value, save=False)
        
        # Save all settings
        self.settings.save()
        
        # Notify the parent if a callback is registered
        if self.callback:
            self.callback(settings)
    
    def _center_on_parent(self) -> None:
        """Center the dialog on its parent window."""
        self.update_idletasks()
        
        parent = self.master
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.geometry(f"+{x}+{y}")
    
    def set_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Set a callback to be called when settings are applied.
        
        Args:
            callback: A function that takes a dictionary of settings.
        """
        self.callback = callback
