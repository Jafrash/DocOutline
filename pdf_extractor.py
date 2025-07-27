"""
PDF Extractor module for extracting document structure from PDF files.
"""

import fitz  # PyMuPDF
import re
import os
from typing import List, Dict, Any, Tuple, Optional
from heading_detector import HeadingDetector
from openai import OpenAI

class PDFExtractor:
    """Main class for extracting document structure from PDFs."""
    
    def __init__(self):
        """Initialize the PDF extractor."""
        self.heading_detector = HeadingDetector()
        
        # Initialize OpenAI client if API key is available
        self.openai_client = None
        if os.environ.get("OPENAI_API_KEY"):
            try:
                self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            except Exception as e:
                print(f"Warning: Failed to initialize OpenAI client: {e}")
                self.openai_client = None
    
    def extract_structure(self, pdf_path: str, include_summary: bool = True) -> Dict[str, Any]:
        """
        Extract document structure from PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            include_summary: Whether to generate AI summary of the content
            
        Returns:
            Dictionary containing title, outline structure, and optional summary
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
            
            # Extract full text for summarization
            full_text = self._extract_full_text(doc) if include_summary else ""
            
            doc.close()
            
            result = {
                "title": title,
                "outline": outline
            }
            
            # Add summary if requested and OpenAI is available
            if include_summary and self.openai_client and full_text:
                try:
                    summary = self._generate_summary(full_text)
                    if summary:
                        result["summary"] = summary
                    else:
                        result["summary"] = self._generate_basic_summary(full_text)
                except Exception as e:
                    print(f"Warning: Failed to generate AI summary: {e}")
                    result["summary"] = self._generate_basic_summary(full_text)
            elif include_summary and not self.openai_client:
                result["summary"] = self._generate_basic_summary(full_text) if full_text else "Summary not available (no content extracted)"
            elif include_summary:
                result["summary"] = self._generate_basic_summary(full_text) if full_text else "Summary not available (no content extracted)"
            
            return result
            
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
    
    def _extract_full_text(self, doc: fitz.Document) -> str:
        """
        Extract all text content from PDF for summarization.
        
        Args:
            doc: PyMuPDF document object
            
        Returns:
            Complete text content of the document
        """
        full_text = []
        
        # Process up to 50 pages
        max_pages = min(len(doc), 50)
        
        for page_num in range(max_pages):
            page = doc[page_num]
            
            # Extract plain text from page
            text = page.get_text()
            if text.strip():
                full_text.append(text.strip())
        
        return "\n\n".join(full_text)
    
    def _generate_summary(self, text: str) -> Optional[str]:
        """
        Generate AI summary of the document text.
        
        Args:
            text: Full text content to summarize
            
        Returns:
            Generated summary or None if failed
        """
        if not self.openai_client or not text.strip():
            return None
        
        try:
            # Truncate text if too long (GPT-4o has context limits)
            max_chars = 50000  # Conservative limit for content
            if len(text) > max_chars:
                text = text[:max_chars] + "..."
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert document analyst. Provide a concise but comprehensive summary of the document that captures the main points, key findings, and important details. Focus on the substance and structure of the content."
                    },
                    {
                        "role": "user",
                        "content": f"Please provide a detailed summary of this document:\n\n{text}"
                    }
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return None
    
    def _generate_basic_summary(self, text: str) -> str:
        """
        Generate a basic text-based summary when AI is not available.
        
        Args:
            text: Full text content to summarize
            
        Returns:
            Basic summary with key statistics and excerpts
        """
        if not text.strip():
            return "No content available for summary."
        
        # Basic text statistics
        lines = text.split('\n')
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        words = text.split()
        
        # Extract first few meaningful paragraphs
        meaningful_paragraphs = []
        for para in paragraphs[:5]:  # Take first 5 paragraphs
            if len(para) > 50 and not para.isupper():  # Skip headers and short paragraphs
                meaningful_paragraphs.append(para)
        
        # Build basic summary
        summary_parts = []
        summary_parts.append(f"Document contains {len(words)} words across {len(paragraphs)} paragraphs.")
        
        if meaningful_paragraphs:
            summary_parts.append("Key content preview:")
            for i, para in enumerate(meaningful_paragraphs[:3]):  # Show first 3 meaningful paragraphs
                if len(para) > 200:
                    para = para[:200] + "..."
                summary_parts.append(f"{i+1}. {para}")
        
        return "\n\n".join(summary_parts)
