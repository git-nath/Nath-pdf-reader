"""NathReader - A modern PDF reader application."""

import os
import sys
import logging
from pathlib import Path

def main():
    """Launch the NathReader application."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('nathreader.log')
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        # Add the parent directory to the path so we can import nathreader
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        # Import the application class
        from nathreader.app import PDFReaderApp
        
        # Create and run the application
        app = PDFReaderApp()
        
        # Handle command line arguments
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
            if os.path.isfile(file_path):
                app.open_document(file_path)
        
        # Start the main event loop
        app.mainloop()
        
    except Exception as e:
        logger.exception("Unhandled exception in main")
        print(f"An error occurred: {str(e)}", file=sys.stderr)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
