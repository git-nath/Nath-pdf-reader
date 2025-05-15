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
        self._brightness = 1.0  # 1.0 is normal brightness
    
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
    
    def set_brightness(self, value: float) -> None:
        """Set the brightness level.
        
        Args:
            value: Brightness value (0.0 to 2.0, where 1.0 is normal)
        """
        old_value = getattr(self, '_brightness', 1.0)
        self._brightness = max(0.1, min(2.0, float(value)))  # Clamp between 0.1 and 2.0
        logger.debug(f"Document brightness changed from {old_value} to {self._brightness}")
    
    def get_brightness(self) -> float:
        """Get the current brightness level.
        
        Returns:
            float: Current brightness value.
        """
        return self._brightness
    
    def _apply_brightness(self, image: Image.Image) -> Image.Image:
        """Apply brightness adjustment to an image.
        
        Args:
            image: Input PIL Image
            
        Returns:
            Image.Image: Image with brightness adjusted
        """
        try:
            if not hasattr(self, '_brightness') or self._brightness == 1.0:
                return image
                
            # Ensure we have a valid image
            if image is None:
                return None
                
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to numpy array for faster processing
            import numpy as np
            
            # Convert to float for calculations
            img_array = np.array(image, dtype=np.float32) / 255.0
            
            # Apply brightness
            img_array = img_array * self._brightness
            
            # Clip values to [0, 1] range
            img_array = np.clip(img_array, 0, 1)
            
            # Convert back to 8-bit
            img_array = (img_array * 255).astype(np.uint8)
            
            # Convert back to PIL Image
            return Image.fromarray(img_array, 'RGB')
            
        except Exception as e:
            logger.error(f"Error applying brightness: {e}")
            return image
    
    def get_page(self, page_num: int, zoom: float = 1.0) -> Optional[Image.Image]:
        """Get a page as a PIL Image.
        
        Args:
            page_num: Page number (0-based).
            zoom: Zoom factor.
            
        Returns:
            Optional[Image.Image]: The page as a PIL Image, or None if there was an error.
        """
        try:
            if not self._loaded or self._document is None:
                logger.warning("Document not loaded or invalid")
                return None
                
            if not 0 <= page_num < self._page_count:
                logger.warning(f"Page number {page_num} out of range (0-{self._page_count-1})")
                return None
                
            # Get page and render to pixmap
            page = self._document.load_page(page_num)
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # Convert to PIL Image
            img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
            
            # Apply brightness if needed
            if hasattr(self, '_brightness') and self._brightness != 1.0:
                img = self._apply_brightness(img)
                
            return img
            
        except Exception as e:
            logger.error(f"Error in get_page: {e}")
            return None
            
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
