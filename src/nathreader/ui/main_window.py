import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font as tkfont
from PIL import Image, ImageTk, ImageEnhance
import fitz  # PyMuPDF
import io
import os
from pathlib import Path
import json

class ModernPDFViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern PDF Viewer")
        self.root.geometry("1024x768")
        self.root.minsize(800, 600)
        
        # Settings
        self.settings_file = Path("viewer_settings.json")
        self.settings = self.load_settings()
        
        # UI Colors
        self.colors = {
            'light': {
                'bg': '#f0f0f0',
                'fg': '#333333',
                'toolbar': '#e0e0e0',
                'canvas': '#ffffff',
                'button': '#e0e0e0',
                'button_hover': '#d0d0d0',
                'button_active': '#c0c0c0',
            },
            'dark': {
                'bg': '#1e1e1e',
                'fg': '#e0e0e0',
                'toolbar': '#2d2d2d',
                'canvas': '#252526',
                'button': '#3c3c3c',
                'button_hover': '#4c4c4c',
                'button_active': '#5c5c5c',
            }
        }
        
        # Current theme
        self.theme = 'light' if self.settings.get('theme', 'light') == 'light' else 'dark'
        self.brightness = self.settings.get('brightness', 1.0)
        
        # Initialize UI
        self.setup_ui()
        
        # Initialize variables
        self.doc = None
        self.current_page = 0
        self.zoom = 1.0
        self.images = []
        self.current_image = None
        self.pages_frame = None  # Will hold all pages
        self.pages = []  # Will store page widgets
        
        # Bind keyboard shortcuts
        self.root.bind("<Control-o>", lambda e: self.open_pdf())
        self.root.bind("<Right>", lambda e: self.next_page())
        self.root.bind("<Left>", lambda e: self.prev_page())
        self.root.bind("<Control-plus>", lambda e: self.change_zoom(1.25))
        self.root.bind("<Control-minus>", lambda e: self.change_zoom(0.8))
        self.root.bind("<Control-n>", lambda e: self.toggle_night_mode())
        
        # Try to open test PDF if it exists
        self.after_id = self.root.after(100, self.try_open_test_pdf)
    
    def setup_ui(self):
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('default')
        
        # Configure custom styles
        self.style.configure('Pages.TFrame', background=self.get_color('canvas'))
        self.style.configure('Page.TFrame', background=self.get_color('canvas'))
        
        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Toolbar
        self.toolbar = tk.Frame(self.main_frame, bg=self.get_color('toolbar'))
        self.toolbar.pack(fill=tk.X, padx=2, pady=2)
        
        # Buttons
        btn_style = {
            'bg': self.get_color('button'),
            'fg': self.get_color('fg'),
            'bd': 0,
            'padx': 8,
            'pady': 4,
            'relief': 'flat',
            'font': ('Segoe UI', 9)
        }
        
        self.btn_open = tk.Button(self.toolbar, text="Open", command=self.open_pdf, **btn_style)
        self.btn_prev = tk.Button(self.toolbar, text="Previous", command=self.prev_page, **btn_style)
        self.btn_next = tk.Button(self.toolbar, text="Next", command=self.next_page, **btn_style)
        self.btn_zoom_in = tk.Button(self.toolbar, text="Zoom In", command=lambda: self.change_zoom(1.25), **btn_style)
        self.btn_zoom_out = tk.Button(self.toolbar, text="Zoom Out", command=lambda: self.change_zoom(0.8), **btn_style)
        self.btn_night = tk.Button(self.toolbar, text="Night Mode", command=self.toggle_night_mode, **btn_style)
        
        # Brightness slider
        self.brightness_frame = tk.Frame(self.toolbar, bg=self.get_color('toolbar'))
        self.brightness_label = tk.Label(self.brightness_frame, text="Brightness:", bg=self.get_color('toolbar'), fg=self.get_color('fg'))
        self.brightness_slider = tk.Scale(
            self.brightness_frame, 
            from_=0.1, 
            to=2.0, 
            resolution=0.1,
            orient=tk.HORIZONTAL,
            command=self.update_brightness,
            bg=self.get_color('toolbar'),
            fg=self.get_color('fg'),
            highlightthickness=0,
            length=100
        )
        self.brightness_slider.set(self.brightness)
        
        # Pack toolbar widgets
        self.btn_open.pack(side=tk.LEFT, padx=2)
        self.btn_prev.pack(side=tk.LEFT, padx=2)
        self.btn_next.pack(side=tk.LEFT, padx=2)
        self.btn_zoom_in.pack(side=tk.LEFT, padx=2)
        self.btn_zoom_out.pack(side=tk.LEFT, padx=2)
        self.btn_night.pack(side=tk.LEFT, padx=2)
        
        # Pack brightness controls
        self.brightness_frame.pack(side=tk.LEFT, padx=10)
        self.brightness_label.pack(side=tk.LEFT)
        self.brightness_slider.pack(side=tk.LEFT)
        
        # Canvas frame with scrollbars
        self.canvas_frame = ttk.Frame(self.main_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a canvas with scrollbars
        self.canvas = tk.Canvas(
            self.canvas_frame,
            bg=self.get_color('canvas'),
            highlightthickness=0
        )
        
        # Create a frame inside the canvas to hold the pages
        self.pages_frame = ttk.Frame(self.canvas, style='Pages.TFrame')
        
        # Create a window in the canvas to hold the frame
        self.canvas.create_window((0, 0), window=self.pages_frame, anchor='nw')
        
        # Create scrollbars
        self.scroll_y = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scroll_x = ttk.Scrollbar(self.canvas_frame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)
        
        # Grid layout
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scroll_y.grid(row=0, column=1, sticky="ns")
        self.scroll_x.grid(row=1, column=0, sticky="ew")
        
        # Bind the canvas configure event to update the scroll region
        self.pages_frame.bind('<Configure>', self.on_frame_configure)
        
        # Bind mouse wheel for scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", lambda e: self._on_mousewheel(e, delta=120))  # Linux up
        self.canvas.bind_all("<Button-5>", lambda e: self._on_mousewheel(e, delta=-120))  # Linux down
        
        # Configure grid weights
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(
            self.main_frame, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind mouse wheel for scrolling and zooming
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Button-4>", lambda e: self.on_mousewheel(e, delta=120))  # Linux up
        self.canvas.bind("<Button-5>", lambda e: self.on_mousewheel(e, delta=-120))  # Linux down
        
        # Bind mouse motion for hover effects
        for btn in [self.btn_open, self.btn_prev, self.btn_next, self.btn_zoom_in, self.btn_zoom_out, self.btn_night]:
            btn.bind("<Enter>", lambda e, b=btn: self.on_enter(e, b))
            btn.bind("<Leave>", lambda e, b=btn: self.on_leave(e, b))
            btn.bind("<ButtonPress-1>", lambda e, b=btn: self.on_press(e, b))
            btn.bind("<ButtonRelease-1>", lambda e, b=btn: self.on_release(e, b))
    
    def get_color(self, element):
        return self.colors[self.theme].get(element, '#000000')
    
    def update_theme(self):
        # Update colors
        self.toolbar.config(bg=self.get_color('toolbar'))
        self.canvas.config(bg=self.get_color('canvas'))
        self.brightness_frame.config(bg=self.get_color('toolbar'))
        self.brightness_label.config(bg=self.get_color('toolbar'), fg=self.get_color('fg'))
        self.brightness_slider.config(bg=self.get_color('toolbar'), fg=self.get_color('fg'))
        
        # Update button styles
        for btn in [self.btn_open, self.btn_prev, self.btn_next, self.btn_zoom_in, self.btn_zoom_out, self.btn_night]:
            btn.config(
                bg=self.get_color('button'),
                fg=self.get_color('fg'),
                activebackground=self.get_color('button_active'),
                activeforeground=self.get_color('fg')
            )
        
        # Redraw the current page with new theme
        if self.doc:
            self.show_page()
    
    def on_enter(self, event, button):
        button.config(bg=self.get_color('button_hover'))
    
    def on_leave(self, event, button):
        button.config(bg=self.get_color('button'))
    
    def on_press(self, event, button):
        button.config(bg=self.get_color('button_active'))
    
    def on_release(self, event, button):
        button.config(bg=self.get_color('button_hover'))
    
    def load_settings(self):
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def save_settings(self):
        self.settings['theme'] = self.theme
        self.settings['brightness'] = self.brightness
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f)
    
    def try_open_test_pdf(self):
        test_pdf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_document.pdf")
        if os.path.exists(test_pdf):
            try:
                self.load_pdf(test_pdf)
                self.status_var.set(f"Opened: {os.path.basename(test_pdf)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open test PDF: {str(e)}")
    
    def open_pdf(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        
        if not filepath:
            return
            
        try:
            self.load_pdf(filepath)
            self.status_var.set(f"Opened: {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open PDF: {str(e)}")
    
    def load_pdf(self, filepath):
        # Clear previous document
        self.canvas.delete("all")
        self.images = []
        
        # Open the PDF
        self.doc = fitz.open(filepath)
        self.current_page = 0
        self.zoom = 1.0
        self.show_page()

def on_enter(self, event, button):
    button.config(bg=self.get_color('button_hover'))

def on_leave(self, event, button):
    button.config(bg=self.get_color('button'))

def on_press(self, event, button):
    button.config(bg=self.get_color('button_active'))

def on_release(self, event, button):
    button.config(bg=self.get_color('button_hover'))

def load_settings(self):
    if self.settings_file.exists():
        try:
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_settings(self):
    self.settings['theme'] = self.theme
    self.settings['brightness'] = self.brightness
    with open(self.settings_file, 'w') as f:
        json.dump(self.settings, f)

def try_open_test_pdf(self):
    test_pdf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_document.pdf")
    if os.path.exists(test_pdf):
        try:
            self.load_pdf(test_pdf)
            self.status_var.set(f"Opened: {os.path.basename(test_pdf)}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open test PDF: {str(e)}")

def open_pdf(self):
    filepath = filedialog.askopenfilename(
        filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
    )

    if not filepath:
        return

    try:
        self.load_pdf(filepath)
        self.status_var.set(f"Opened: {os.path.basename(filepath)}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not open PDF: {str(e)}")

def load_pdf(self, filepath):
    # Clear previous document
    for widget in self.pages_frame.winfo_children():
        widget.destroy()
    self.pages = []

    # Open the PDF
    self.doc = fitz.open(filepath)
    self.current_page = 0
    self.zoom = 1.0
    self.show_page()

def show_page(self):
    if not self.doc:
        return

    # Clear previous pages
    for widget in self.pages_frame.winfo_children():
        widget.destroy()
    self.pages = []

    # Get the total number of pages
    total_pages = len(self.doc)

    # Render all pages
    for page_num in range(total_pages):
        # Create a frame for each page
        page_frame = ttk.Frame(self.pages_frame, padding=10, style='Page.TFrame')
        page_frame.pack(fill=tk.X, pady=5)

        # Create a canvas for the page
        page_canvas = tk.Canvas(page_frame, bg='white', highlightthickness=1, highlightbackground='#cccccc')
        page_canvas.pack()

        # Get and render the page
        page = self.doc.load_page(page_num)
        mat = fitz.Matrix(self.zoom, self.zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)

        # Convert to ImageTk format
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Apply brightness
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(self.brightness)

        # Apply night mode effect if needed
        if self.theme == 'dark':
            # Invert colors for dark mode
            img = Image.eval(img, lambda x: 255 - x)
            # Reduce brightness for eye comfort
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(0.7)

        # Convert to PhotoImage and keep a reference
        photo = ImageTk.PhotoImage(img)
        self.pages.append(photo)  # Keep a reference

        # Display the image
        page_canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        page_canvas.config(width=img.width, height=img.height)

        # Add page number
        page_label = ttk.Label(page_frame, text=f"Page {page_num + 1} of {total_pages}")
        page_label.pack(pady=(5, 15))

    # Update status bar
    self.status_var.set(f"Showing all pages (1-{total_pages})")

    # Update the canvas scroll region
    self.canvas.update_idletasks()
    self.canvas.config(scrollregion=self.canvas.bbox("all"))

def next_page(self):
    if self.doc and self.current_page < len(self.doc) - 1:
        self.current_page += 1
        self.show_page()

def prev_page(self):
    if self.doc and self.current_page > 0:
        self.current_page -= 1
        self.show_page()

def change_zoom(self, factor):
    if not self.doc:
        return

    self.zoom *= factor
    self.zoom = max(0.1, min(5.0, self.zoom))  # Limit zoom range
    self.show_page()

def update_brightness(self, value):
    try:
        self.brightness = float(value)
        if self.doc:
            self.show_page()
    except ValueError:
        pass

def toggle_night_mode(self):
    self.theme = 'dark' if self.theme == 'light' else 'light'
    self.update_theme()

def on_mousewheel(self, event, delta=None):
    if delta is None:
        delta = event.delta

    # Check if Control key is pressed for zooming
    if event.state & 0x4:  # Control key
        if delta > 0:
            self.change_zoom(1.1)
        else:
            self.change_zoom(0.9)
    else:
        # Normal scrolling
        self.canvas.yview_scroll(-1 * (delta // 120), "units")

def on_frame_configure(self, event=None):
    """Reset the scroll region to encompass the inner frame"""
    self.canvas.configure(scrollregion=self.canvas.bbox("all"))

def _on_mousewheel(self, event, delta=None):
    """Handle mouse wheel for scrolling"""
    if delta is None:
        delta = event.delta

    # On Windows, delta is 120 per wheel click
    # On macOS, it might be different, so we normalize it
    if abs(delta) > 100:  # Windows
        delta = delta // abs(delta) * 2

    self.canvas.yview_scroll(-1 * delta, "units")

def on_closing(self):
    self.save_settings()
    self.root.destroy()

def main():
    root = tk.Tk()
    app = ModernPDFViewer(root)
    
    # Handle window close
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Center the window
    window_width = 1024
    window_height = 768
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
