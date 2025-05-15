import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import fitz  # PyMuPDF
import io
import os

class SimplePDFViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple PDF Viewer")
        self.root.geometry("800x600")
        
        # Create main frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas with scrollbars
        self.canvas = tk.Canvas(self.main_frame, bg='white')
        self.scroll_y = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scroll_x = ttk.Scrollbar(self.main_frame, orient="horizontal", command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)
        
        # Grid layout
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scroll_y.grid(row=0, column=1, sticky="ns")
        self.scroll_x.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Menu
        menubar = tk.Menu(root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        root.config(menu=menubar)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Initialize variables
        self.doc = None
        self.current_page = 0
        self.zoom = 1.0
        self.images = []  # Keep references to images
        
        # Bind mouse wheel for scrolling
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Button-4>", lambda e: self.on_mousewheel(e, delta=120))
        self.canvas.bind("<Button-5>", lambda e: self.on_mousewheel(e, delta=-120))
    
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
        self.show_page()
    
    def show_page(self):
        if not self.doc:
            return
            
        try:
            # Get the page
            page = self.doc.load_page(self.current_page)
            
            # Render page to an image
            zoom_matrix = fitz.Matrix(self.zoom, self.zoom)
            pix = page.get_pixmap(matrix=zoom_matrix)
            
            # Convert to ImageTk format
            img_data = pix.tobytes("ppm")
            img = Image.open(io.BytesIO(img_data))
            self.photo = ImageTk.PhotoImage(image=img)
            
            # Keep a reference to the image
            self.images.append(self.photo)
            
            # Update canvas
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
            self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
            
            # Update status
            self.status_var.set(f"Page {self.current_page + 1} of {len(self.doc)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error displaying page: {str(e)}")
    
    def on_mousewheel(self, event, delta=None):
        if delta is None:
            delta = event.delta
        
        # Scroll vertically
        self.canvas.yview_scroll(-1 * (delta // 120), "units")

def main():
    root = tk.Tk()
    app = SimplePDFViewer(root)
    
    # Try to open test PDF if it exists
    test_pdf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_document.pdf")
    if os.path.exists(test_pdf):
        try:
            app.load_pdf(test_pdf)
            app.status_var.set(f"Opened: {os.path.basename(test_pdf)}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open test PDF: {str(e)}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
