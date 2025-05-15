from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_test_pdf():
    # Create a PDF document
    c = canvas.Canvas("test_document.pdf", pagesize=letter)
    width, height = letter
    
    # Set font and size
    c.setFont("Helvetica-Bold", 24)
    
    # Add title
    c.drawString(72, height - 72, "Test PDF Document")
    c.setFont("Helvetica", 12)
    
    # Add some content
    text = """
    This is a test PDF document created for NathFile Reader.
    
    Features to test:
    1. Page navigation
    2. Zoom in/out
    3. Scrolling
    4. Printing
    
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
    Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
    Ut enim ad minim veniam, quis nostrud exercitation ullamco.
    """
    
    # Split text into lines and add to PDF
    y = height - 120
    for line in text.split('\n'):
        c.drawString(72, y, line.strip())
        y -= 20
    
    # Add a second page
    c.showPage()
    c.setFont("Helvetica-Bold", 18)
    c.drawString(72, height - 72, "Second Page")
    c.setFont("Helvetica", 12)
    c.drawString(72, height - 100, "This is the second page of the test document.")
    
    # Close the PDF object cleanly
    c.save()
    print("Test PDF created: test_document.pdf")

if __name__ == "__main__":
    create_test_pdf()
