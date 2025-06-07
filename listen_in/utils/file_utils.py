"""File utility functions for Listen-in."""

from pathlib import Path
from typing import Optional


def save_script(content: str, output_path: str) -> None:
    """
    Save the generated script to a file.
    
    Args:
        content: The script content to save
        output_path: Path where the script should be saved
    """
    path = Path(output_path)
    
    # Ensure the directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write the content
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def validate_file_path(file_path: str, allowed_extensions: Optional[list[str]] = None) -> Path:
    """
    Validate that a file path exists and has an allowed extension.
    
    Args:
        file_path: Path to validate
        allowed_extensions: List of allowed file extensions (with dots)
        
    Returns:
        Path object if valid
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file extension is not allowed
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
    
    if allowed_extensions and path.suffix.lower() not in allowed_extensions:
        raise ValueError(f"File type {path.suffix} not supported. Allowed: {', '.join(allowed_extensions)}")
    
    return path


def estimate_reading_time(word_count: int, words_per_minute: int = 150) -> int:
    """
    Estimate speaking/reading time in minutes.
    
    Args:
        word_count: Number of words in the document
        words_per_minute: Average speaking rate (default: 150 for podcasts)
        
    Returns:
        Estimated time in minutes
    """
    return max(1, word_count // words_per_minute)