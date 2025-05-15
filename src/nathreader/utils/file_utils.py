"""Utility functions for file operations."""

import os
from pathlib import Path
from typing import Optional, Tuple, Union

def ensure_directory_exists(directory: Union[str, Path]) -> Path:
    """Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory: The directory path to check/create.
        
    Returns:
        Path: The path to the directory.
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_valid_filename(filename: str) -> str:
    """Return a valid filename by removing invalid characters.
    
    Args:
        filename: The original filename.
        
    Returns:
        str: A sanitized filename.
    """
    # Replace invalid characters with underscores
    invalid_chars = '<>:"/\\|?*\0' + ''.join(chr(i) for i in range(1, 32))
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def get_file_extension(filename: str) -> str:
    """Get the lowercase extension of a filename.
    
    Args:
        filename: The filename to get the extension from.
        
    Returns:
        str: The lowercase file extension (without the dot).
    """
    return Path(filename).suffix.lower().lstrip('.')

def is_supported_file(filename: str) -> bool:
    """Check if a file has a supported extension.
    
    Args:
        filename: The name of the file to check.
        
    Returns:
        bool: True if the file has a supported extension, False otherwise.
    """
    supported_extensions = {'pdf', 'docx', 'pptx'}
    return get_file_extension(filename) in supported_extensions

def get_file_size(filepath: Union[str, Path]) -> Tuple[float, str]:
    """Get the size of a file in a human-readable format.
    
    Args:
        filepath: Path to the file.
        
    Returns:
        Tuple[float, str]: A tuple containing the size and the unit (e.g., (1.5, 'MB')).
    """
    size = os.path.getsize(filepath)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return size, unit
        size /= 1024.0
    return size, 'TB'
