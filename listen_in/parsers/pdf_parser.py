"""PDF document parser for podcast generation."""

import os
from pathlib import Path
from typing import Dict, Any, List
import PyPDF2
import pdfplumber


class PDFParser:
    """Parser for PDF documents."""
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a PDF file and extract its content.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing content, metadata, and structure
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if path.suffix.lower() != '.pdf':
            raise ValueError(f"Not a PDF file: {file_path}")
        
        # Try pdfplumber first (better text extraction)
        try:
            return self._parse_with_pdfplumber(path)
        except Exception as e:
            print(f"pdfplumber failed, trying PyPDF2: {e}")
            # Fallback to PyPDF2
            return self._parse_with_pypdf2(path)
    
    def _parse_with_pdfplumber(self, path: Path) -> Dict[str, Any]:
        """Parse PDF using pdfplumber (better for complex layouts)."""
        import pdfplumber
        
        full_text = []
        sections = []
        
        with pdfplumber.open(path) as pdf:
            # Extract metadata
            metadata = {
                "filename": path.name,
                "title": pdf.metadata.get('Title', path.stem),
                "author": pdf.metadata.get('Author', 'Unknown'),
                "pages": len(pdf.pages),
                "file_size": path.stat().st_size
            }
            
            # Extract text from each page
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    full_text.append(page_text)
                    sections.append({
                        "content": page_text,
                        "page": i + 1,
                        "word_count": len(page_text.split())
                    })
        
        content = "\n\n".join(full_text)
        word_count = len(content.split())
        
        metadata.update({
            "word_count": word_count,
            "line_count": content.count('\n') + 1,
        })
        
        return {
            "content": content,
            "metadata": metadata,
            "structure": {
                "sections": sections,
                "has_headings": self._detect_headings(content),
                "estimated_reading_time": word_count // 200  # ~200 words per minute
            }
        }
    
    def _parse_with_pypdf2(self, path: Path) -> Dict[str, Any]:
        """Parse PDF using PyPDF2 (fallback option)."""
        full_text = []
        sections = []
        
        with open(path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extract metadata
            info = pdf_reader.metadata or {}
            metadata = {
                "filename": path.name,
                "title": info.get('/Title', path.stem),
                "author": info.get('/Author', 'Unknown'),
                "pages": len(pdf_reader.pages),
                "file_size": path.stat().st_size
            }
            
            # Extract text from each page
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text:
                    full_text.append(page_text)
                    sections.append({
                        "content": page_text,
                        "page": i + 1,
                        "word_count": len(page_text.split())
                    })
        
        content = "\n\n".join(full_text)
        word_count = len(content.split())
        
        metadata.update({
            "word_count": word_count,
            "line_count": content.count('\n') + 1,
        })
        
        return {
            "content": content,
            "metadata": metadata,
            "structure": {
                "sections": sections,
                "has_headings": self._detect_headings(content),
                "estimated_reading_time": word_count // 200
            }
        }
    
    def _detect_headings(self, content: str) -> bool:
        """Detect if the content has heading patterns."""
        # Common heading patterns in PDFs
        heading_patterns = [
            'CHAPTER', 'Chapter', 'SECTION', 'Section',
            'ARTICLE', 'Article', 'PART', 'Part',
            '\n1.', '\n2.', '\n3.',  # Numbered sections
            '\nI.', '\nII.', '\nIII.',  # Roman numerals
        ]
        
        return any(pattern in content for pattern in heading_patterns)