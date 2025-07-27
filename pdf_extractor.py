"""
PDF Extractor module for extracting document structure from PDF files.
"""

import fitz  # PyMuPDF
import re
from typing import List, Dict, Any, Tuple
from heading_detector import HeadingDetector

class PDFExtractor:
    """Main class for extracting document structure from PDFs."""
    
    def __init__(self):
        """Initialize the PDF extractor."""
        self.heading_detector = HeadingDetector()
    
    def extract_structure(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract document structure from PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing title and outline structure
        """
        try:
            # Open PDF document
            doc = fitz.open(pdf_path)
            
            # Check page count limit
            if len(doc) > 50:
                print(f"Warning: PDF has {len(doc)} pages, processing first 50 only")
            
            # Extract title
            title = self._extract_title(doc)
            
            # Extract outline/headings
            outline = self._extract_outline(doc)
            
            doc.close()
            
            return {
                "title": title,
                "outline": outline
            }
            
        except Exception as e:
            raise Exception(f"Failed to process PDF: {str(e)}")
    
    def _extract_title(self, doc: fitz.Document) -> str:
        """
        Extract document title from PDF.
        
        Args:
            doc: PyMuPDF document object
            
        Returns:
            Document title as string
        """
        # Try to get title from metadata first
        metadata = doc.metadata
        if metadata and metadata.get('title'):
            title = metadata['title'].strip()
            if title and len(title) < 200:  # Reasonable title length
                return title
        
        # If no metadata title, try to extract from first page
        if len(doc) > 0:
            first_page = doc[0]
            
            # Get text blocks with formatting info
            blocks = first_page.get_text("dict")
            
            # Look for the largest text in the upper portion of the first page
            title_candidates = []
            
            for block in blocks.get("blocks", []):
                if block.get("type") == 0:  # Text block
                    for line in block.get("lines", []):
                        line_bbox = line.get("bbox", [0, 0, 0, 0])
                        line_y = line_bbox[1]  # Top y coordinate
                        
                        # Only consider text in upper 1/3 of page
                        if line_y < first_page.rect.height / 3:
                            for span in line.get("spans", []):
                                text = span.get("text", "").strip()
                                font_size = span.get("size", 0)
                                
                                if text and len(text) > 5 and font_size > 12:
                                    title_candidates.append({
                                        "text": text,
                                        "size": font_size,
                                        "y": line_y
                                    })
            
            # Sort by font size (descending) and position (ascending)
            title_candidates.sort(key=lambda x: (-x["size"], x["y"]))
            
            if title_candidates:
                # Clean up the title text
                title = title_candidates[0]["text"]
                title = re.sub(r'\s+', ' ', title).strip()
                return title
        
        return "Untitled Document"
    
    def _extract_outline(self, doc: fitz.Document) -> List[Dict[str, Any]]:
        """
        Extract document outline/headings from PDF.
        
        Args:
            doc: PyMuPDF document object
            
        Returns:
            List of heading dictionaries with level, text, and page
        """
        outline = []
        
        # Process up to 50 pages
        max_pages = min(len(doc), 50)
        
        for page_num in range(max_pages):
            page = doc[page_num]
            
            # Get text blocks with detailed formatting
            blocks = page.get_text("dict")
            
            for block in blocks.get("blocks", []):
                if block.get("type") == 0:  # Text block
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            text = span.get("text", "").strip()
                            
                            if not text:
                                continue
                            
                            # Analyze this text span for heading characteristics
                            heading_info = self.heading_detector.analyze_text(
                                text=text,
                                font_size=span.get("size", 12),
                                font_name=span.get("font", ""),
                                flags=span.get("flags", 0),
                                bbox=span.get("bbox", [0, 0, 0, 0]),
                                page_height=page.rect.height
                            )
                            
                            if heading_info:
                                outline.append({
                                    "level": heading_info["level"],
                                    "text": heading_info["text"],
                                    "page": page_num + 1
                                })
        
        return outline
