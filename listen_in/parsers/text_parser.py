"""Text file parser for Listen-in."""

from pathlib import Path
from typing import Dict, Any


class TextParser:
    """Parser for plain text files."""
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a text file and extract content with metadata.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Dictionary containing parsed content and metadata
        """
        path = Path(file_path)
        
        # Read the file content
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract basic metadata
        lines = content.split('\n')
        word_count = len(content.split())
        
        # Try to extract a title (first non-empty line)
        title = None
        for line in lines:
            if line.strip():
                title = line.strip()
                break
        
        return {
            "content": content,
            "metadata": {
                "filename": path.name,
                "title": title or path.stem,
                "word_count": word_count,
                "line_count": len(lines),
                "file_size": path.stat().st_size
            },
            "structure": {
                "sections": self._extract_sections(lines),
                "has_headings": False,  # Plain text doesn't have formal headings
                "estimated_reading_time": word_count // 200  # Average reading speed
            }
        }
    
    def _extract_sections(self, lines: list[str]) -> list[Dict[str, Any]]:
        """
        Extract logical sections from text based on paragraph breaks.
        
        Args:
            lines: List of text lines
            
        Returns:
            List of section dictionaries
        """
        sections = []
        current_section = []
        
        for line in lines:
            if line.strip():  # Non-empty line
                current_section.append(line)
            elif current_section:  # Empty line and we have content
                sections.append({
                    "content": "\n".join(current_section),
                    "word_count": len(" ".join(current_section).split())
                })
                current_section = []
        
        # Don't forget the last section
        if current_section:
            sections.append({
                "content": "\n".join(current_section),
                "word_count": len(" ".join(current_section).split())
            })
        
        return sections