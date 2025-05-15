"""Core document handling functionality."""

import fitz  # PyMuPDF
from pathlib import Path
from typing import Optional, List, Tuple, Any, Dict
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

class Document:
    """Base class for document handling."""
    
    def __init__(self, filepath: str):
        """Initialize the document.
        
        Args:
            filepath: Path to the document file.
        """
        self.filepath = Path(filepath)
        self._document = None
        self._metadata = {}
        self._page_count = 0
        self._current_page = 0
        self._loaded = False
    
    def __del__(self):
        """Clean up resources when the object is deleted."""
        self.close()
    
    def close(self) -> None:
        """Close the document and release resources."""
        if self._document is not None:
            try:
                self._document.close()
            except Exception as e:
                logger.error(f"Error closing document: {e}")
            self._document = None
        self._loaded = False
    
    def load(self) -> bool:
        """Load the document.
        
        Returns:
            bool: True if the document was loaded successfully, False otherwise.
        """
        try:
            self._document = fitz.open(self.filepath)
            self._page_count = len(self._document)
            self._loaded = True
            self._load_metadata()
            return True
        except Exception as e:
            logger.error(f"Error loading document {self.filepath}: {e}")
            self.close()
            return False
    
    def _load_metadata(self) -> None:
        """Load document metadata."""
        if not self._loaded or self._document is None:
            return
            
        try:
            self._metadata = {
                'title': self._document.metadata.get('title', ''),
                'author': self._document.metadata.get('author', ''),
                'subject': self._document.metadata.get('subject', ''),
                'keywords': self._document.metadata.get('keywords', ''),
                'creator': self._document.metadata.get('creator', ''),
                'producer': self._document.metadata.get('producer', ''),
                'creation_date': self._document.metadata.get('creationDate', ''),
                'modification_date': self._document.metadata.get('modDate', ''),
                'format': self._document.metadata.get('format', ''),
                'encryption': self._document.metadata.get('encryption', ''),
                'pages': self._page_count,
            }
        except Exception as e:
            logger.error(f"Error loading document metadata: {e}")
            self._metadata = {}
    
    def get_page(self, page_num: int, zoom: float = 1.0) -> Optional[Image.Image]:
        """Get a page as a PIL Image.
        
        Args:
            page_num: Page number (0-based).
            zoom: Zoom factor.
            
        Returns:
            Optional[Image.Image]: The page as a PIL Image, or None if there was an error.
        """
        if not self._loaded or self._document is None:
            return None
            
        if not 0 <= page_num < self._page_count:
            return None
            
        try:
            page = self._document.load_page(page_num)
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # Convert to PIL Image
            img_data = pix.tobytes('ppm')
            return Image.open(io.BytesIO(img_data))
            
        except Exception as e:
            logger.error(f"Error getting page {page_num}: {e}")
            return None
    
    @property
    def page_count(self) -> int:
        """Get the total number of pages in the document."""
        return self._page_count
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the document metadata."""
        return self._metadata
    
    @property
    def is_loaded(self) -> bool:
        """Check if the document is loaded."""
        return self._loaded


class DocumentFactory:
    """Factory for creating document objects based on file type."""
    
    @staticmethod
    def create_document(filepath: str) -> Optional[Document]:
        """Create an appropriate document handler based on file extension.
        
        Args:
            filepath: Path to the document file.
            
        Returns:
            Optional[Document]: A document object, or None if the file type is not supported.
        """
        path = Path(filepath)
        suffix = path.suffix.lower()
        
        if suffix == '.pdf':
            return PDFDocument(filepath)
        # Add support for other document types here
        # elif suffix in ('.docx', '.doc'):
        #     return WordDocument(filepath)
        # elif suffix in ('.pptx', '.ppt'):
        #     return PowerPointDocument(filepath)
        else:
            return None


class PDFDocument(Document):
    """PDF document handler."""
    
    def __init__(self, filepath: str):
        """Initialize the PDF document.
        
        Args:
            filepath: Path to the PDF file.
        """
        super().__init__(filepath)
        self._toc = []
    
    def load(self) -> bool:
        """Load the PDF document.
        
        Returns:
            bool: True if the document was loaded successfully, False otherwise.
        """
        if not super().load():
            return False
        
        try:
            # Load table of contents
            if self._document is not None:
                self._toc = self._document.get_toc()
            return True
        except Exception as e:
            logger.error(f"Error loading PDF document {self.filepath}: {e}")
            self.close()
            return False
    
    @property
    def toc(self) -> List[Tuple[int, str, int]]:
        """Get the table of contents.
        
        Returns:
            List[Tuple[int, str, int]]: A list of (level, title, page) tuples.
        """
        return self._toc
