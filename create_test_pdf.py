from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_test_pdf(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Add title
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 100, "Test Document for NathFile Reader")
    
    # Add some content
    c.setFont("Helvetica", 12)
    text = """
    This is a test document for NathFile Reader.
    
    Features to test:
    1. PDF rendering
    2. Text search
    3. Page navigation
    4. Zoom functionality
    5. Print functionality
    
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
    Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
    """
    
    # Split text into lines and draw them
    y = height - 150
    for line in text.split('\n'):
        c.drawString(50, y, line.strip())
        y -= 20
    
    # Add a second page
    c.showPage()
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 100, "Second Page")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 150, "This is the second page of the test document.")
    
    c.save()

if __name__ == "__main__":
    create_test_pdf("test_document.pdf")
    print("Test PDF created: test_document.pdf")
