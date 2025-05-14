import sys
import os
import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
from PIL import Image, ImageTk
import fitz  # PyMuPDF
import io

class NathFileReader(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("NathFile Reader")
        self.geometry("1000x700")
        
        # Store current document and page
        self.current_file = None
        self.doc = None
        self.current_page = 0
        self.zoom = 1.0
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create main content area
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Canvas for PDF display
        self.canvas = tk.Canvas(self.content_frame, bg='white')
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbars
        self.v_scroll = ctk.CTkScrollbar(self.content_frame, orientation="vertical", command=self.canvas.yview)
        self.h_scroll = ctk.CTkScrollbar(self.content_frame, orientation="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)
        
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="ew")
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ctk.CTkLabel(self, textvariable=self.status_var, anchor="w", padx=10)
        self.status_bar.grid(row=2, column=0, sticky="ew")
        
        # Create menu
        self.create_menu()
        
        # Bind mouse wheel for scrolling
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", lambda e: self._on_mousewheel(e, delta=120))
        self.canvas.bind("<Button-5>", lambda e: self._on_mousewheel(e, delta=-120))
    
    def create_toolbar(self):
        toolbar = ctk.CTkFrame(self)
        toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        
        # Buttons
        open_btn = ctk.CTkButton(toolbar, text="Open", command=self.open_file, width=80)
        open_btn.pack(side="left", padx=2)
        
        prev_btn = ctk.CTkButton(toolbar, text="Previous", command=self.prev_page, width=80)
        prev_btn.pack(side="left", padx=2)
        
        next_btn = ctk.CTkButton(toolbar, text="Next", command=self.next_page, width=80)
        next_btn.pack(side="left", padx=2)
        
        zoom_in_btn = ctk.CTkButton(toolbar, text="Zoom In", command=lambda: self.change_zoom(1.25), width=80)
        zoom_in_btn.pack(side="left", padx=2)
        
        zoom_out_btn = ctk.CTkButton(toolbar, text="Zoom Out", command=lambda: self.change_zoom(0.8), width=80)
        zoom_out_btn.pack(side="left", padx=2)
        
        self.page_label = ctk.CTkLabel(toolbar, text="Page: 0/0")
        self.page_label.pack(side="left", padx=10)
    
    def create_menu(self):
        menubar = tk.Menu(self)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Print...", command=self.print_document, accelerator="Ctrl+P")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Zoom In", command=lambda: self.change_zoom(1.25), accelerator="Ctrl++")
        view_menu.add_command(label="Zoom Out", command=lambda: self.change_zoom(0.8), accelerator="Ctrl+-")
        view_menu.add_separator()
        view_menu.add_command(label="Previous Page", command=self.prev_page, accelerator="Page Up")
        view_menu.add_command(label="Next Page", command=self.next_page, accelerator="Page Down")
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.config(menu=menubar)
        
        # Bind keyboard shortcuts
        self.bind("<Control-o>", lambda e: self.open_file())
        self.bind("<Control-p>", lambda e: self.print_document())
        self.bind("<Control-plus>", lambda e: self.change_zoom(1.25))
        self.bind("<Control-minus>", lambda e: self.change_zoom(0.8))
        self.bind("<Prior>", lambda e: self.prev_page())  # Page Up
        self.bind("<Next>", lambda e: self.next_page())    # Page Down
    
    def open_file(self, filepath=None):
        if not filepath:
            filepath = filedialog.askopenfilename(
                title="Open Document",
                filetypes=[
                    ("Supported Files", "*.pdf *.docx *.pptx"),
                    ("PDF Files", "*.pdf"),
                    ("Word Documents", "*.docx"),
                    ("PowerPoint Presentations", "*.pptx"),
                    ("All Files", "*.*")
                ]
            )
        
        if not filepath:
            return
        
        try:
            if filepath.lower().endswith('.pdf'):
                self.load_pdf(filepath)
            else:
                messagebox.showinfo("Info", f"File format not yet supported: {os.path.basename(filepath)}")
                return
            
            self.current_file = filepath
            self.title(f"NathFile Reader - {os.path.basename(filepath)}")
            self.status_var.set(f"Opened: {os.path.basename(filepath)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {str(e)}")
    
    def load_pdf(self, filepath):
        try:
            if self.doc:
                self.doc.close()
            
            print(f"Trying to open PDF: {filepath}")
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"File not found: {filepath}")
                
            self.doc = fitz.open(filepath)
            print(f"Successfully opened PDF with {len(self.doc)} pages")
            self.current_page = 0
            self.zoom = 1.0
            self.update_page()
            
        except Exception as e:
            error_msg = f"Error loading PDF: {str(e)}"
            print(error_msg)
            messagebox.showerror("Error", error_msg)
            import traceback
            traceback.print_exc()
    
    def update_page(self):
        try:
            if not self.doc:
                print("No document loaded")
                return
            
            print(f"Loading page {self.current_page}")
            page = self.doc.load_page(self.current_page)
            zoom_matrix = fitz.Matrix(self.zoom, self.zoom)
            
            print("Rendering page...")
            pix = page.get_pixmap(matrix=zoom_matrix)
            print(f"Page rendered: {pix.width}x{pix.height}")
            
            # Convert to ImageTk format
            print("Converting to PPM...")
            img_data = pix.tobytes("ppm")
            print("Creating PIL image...")
            img = Image.open(io.BytesIO(img_data))
            print("Creating PhotoImage...")
            self.tk_img = ImageTk.PhotoImage(image=img)
            
            # Update canvas
            print("Updating canvas...")
            self.canvas.delete("all")
            self.canvas.config(scrollregion=(0, 0, self.tk_img.width(), self.tk_img.height()))
            self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)
            
            # Update page label
            self.page_label.configure(text=f"Page: {self.current_page + 1}/{len(self.doc)}")
            print("Page update complete")
            
        except Exception as e:
            error_msg = f"Error updating page: {str(e)}"
            print(error_msg)
            messagebox.showerror("Error", error_msg)
            import traceback
            traceback.print_exc()
    
    def next_page(self):
        if self.doc and self.current_page < len(self.doc) - 1:
            self.current_page += 1
            self.update_page()
    
    def prev_page(self):
        if self.doc and self.current_page > 0:
            self.current_page -= 1
            self.update_page()
    
    def change_zoom(self, factor):
        if self.doc:
            self.zoom *= factor
            self.zoom = max(0.1, min(5.0, self.zoom))  # Limit zoom range
            self.update_page()
    
    def print_document(self, event=None):
        if not self.current_file:
            messagebox.showinfo("Info", "No document is open to print.")
            return
            
        if self.current_file.lower().endswith('.pdf'):
            try:
                import os
                os.startfile(self.current_file, 'print')
                self.status_var.set("Sent to printer")
            except Exception as e:
                messagebox.showerror("Print Error", f"Could not print document: {str(e)}")
        else:
            messagebox.showinfo("Info", "Printing is currently only supported for PDF files.")
    
    def _on_mousewheel(self, event, delta=None):
        if delta is None:
            delta = event.delta
        
        if event.state & 0x1:  # Check if Control key is pressed
            # Zoom with Ctrl + MouseWheel
            if delta > 0:
                self.change_zoom(1.25)
            else:
                self.change_zoom(0.8)
        else:
            # Normal scrolling
            self.canvas.yview_scroll(-1 * (delta // 120), "units")
    
    def show_about(self):
        about_text = """NathFile Reader
Version 1.0.0

A modern file reader for Windows 11

Supported formats:
- PDF Documents (.pdf)

Coming soon:
- Word Documents (.docx)
- PowerPoint Presentations (.pptx)"""
        
        messagebox.showinfo("About NathFile Reader", about_text)

def main():
    ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
    
    app = NathFileReader()
    
    # Try to open test PDF if it exists
    test_pdf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_document.pdf")
    if os.path.exists(test_pdf):
        app.after(100, lambda: app.open_file(test_pdf))
    
    app.mainloop()

if __name__ == "__main__":
    main()
