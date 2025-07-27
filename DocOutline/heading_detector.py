"""
Heading Detection module for identifying and classifying headings in PDF documents.
"""

import re
from typing import Dict, Any, Optional, List

class HeadingDetector:
    """Class for detecting and classifying headings based on text properties."""
    
    def __init__(self):
        """Initialize the heading detector with rules and patterns."""
        # Common heading patterns
        self.heading_patterns = [
            r'^(Chapter|CHAPTER)\s+\d+',
            r'^(Section|SECTION)\s+\d+',
            r'^\d+\.\s+',
            r'^\d+\.\d+\s+',
            r'^\d+\.\d+\.\d+\s+',
            r'^[IVX]+\.\s+',
            r'^[A-Z]\.\s+',
            r'^[a-z]\)\s+',
            r'^\(\d+\)\s+',
            r'^•\s+',
            r'^-\s+',
        ]
        
        # Words that commonly appear in headings
        self.heading_keywords = [
            'introduction', 'conclusion', 'summary', 'overview', 'background',
            'methodology', 'results', 'discussion', 'analysis', 'findings',
            'recommendations', 'references', 'bibliography', 'appendix',
            'abstract', 'executive', 'foreword', 'preface', 'acknowledgments'
        ]
        
        # Font size thresholds (will be calibrated per document)
        self.font_thresholds = {
            'h1_min': 16,
            'h2_min': 14,
            'h3_min': 12,
            'body_max': 11
        }
        
        # Keep track of font sizes seen in document for adaptive thresholding
        self.font_sizes_seen = []
    
    def analyze_text(self, text: str, font_size: float, font_name: str, 
                    flags: int, bbox: List[float], page_height: float) -> Optional[Dict[str, str]]:
        """
        Analyze a text span to determine if it's a heading and classify its level.
        
        Args:
            text: The text content
            font_size: Font size of the text
            font_name: Font family name
            flags: Font flags (bold, italic, etc.)
            bbox: Bounding box coordinates [x0, y0, x1, y1]
            page_height: Height of the page
            
        Returns:
            Dictionary with heading info if detected, None otherwise
        """
        # Record font size for adaptive thresholding
        self.font_sizes_seen.append(font_size)
        
        # Basic text filtering
        if not self._is_potential_heading(text):
            return None
        
        # Calculate confidence score
        confidence = self._calculate_heading_confidence(
            text, font_size, font_name, flags, bbox, page_height
        )
        
        # Require minimum confidence
        if confidence < 0.3:
            return None
        
        # Determine heading level
        level = self._classify_heading_level(text, font_size, flags, confidence)
        
        if level:
            return {
                "level": level,
                "text": self._clean_heading_text(text)
            }
        
        return None
    
    def _is_potential_heading(self, text: str) -> bool:
        """Check if text could potentially be a heading."""
        # Filter out very short or very long text
        if len(text.strip()) < 3 or len(text.strip()) > 200:
            return False
        
        # Filter out text that looks like body content
        if len(text.split()) > 20:  # Too many words for a heading
            return False
        
        # Filter out text with lowercase start (unless it's a numbered list)
        if text[0].islower() and not re.match(r'^\d+\.', text):
            return False
        
        return True
    
    def _calculate_heading_confidence(self, text: str, font_size: float, 
                                   font_name: str, flags: int, bbox: List[float], 
                                   page_height: float) -> float:
        """Calculate confidence that this text is a heading."""
        confidence = 0.0
        
        # Font size factor (larger = more likely heading)
        avg_font_size = sum(self.font_sizes_seen) / len(self.font_sizes_seen) if self.font_sizes_seen else 12
        if font_size > avg_font_size * 1.2:
            confidence += 0.3
        elif font_size > avg_font_size * 1.1:
            confidence += 0.2
        
        # Bold text is more likely to be a heading
        if flags & 2**4:  # Bold flag
            confidence += 0.2
        
        # Font name analysis
        font_lower = font_name.lower()
        if 'bold' in font_lower or 'black' in font_lower:
            confidence += 0.15
        if 'heading' in font_lower or 'title' in font_lower:
            confidence += 0.2
        
        # Pattern matching
        for pattern in self.heading_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                confidence += 0.3
                break
        
        # Keyword matching
        text_lower = text.lower()
        for keyword in self.heading_keywords:
            if keyword in text_lower:
                confidence += 0.1
                break
        
        # Position on page (headings often at top of sections)
        y_position = bbox[1] if bbox else 0
        relative_position = y_position / page_height if page_height > 0 else 0
        if relative_position < 0.1:  # Top 10% of page
            confidence += 0.1
        
        # Length factor (moderate length preferred for headings)
        text_length = len(text.strip())
        if 10 <= text_length <= 80:
            confidence += 0.1
        
        # Capitalization pattern
        if text.isupper():
            confidence += 0.1
        elif text.istitle():
            confidence += 0.05
        
        return min(confidence, 1.0)
    
    def _classify_heading_level(self, text: str, font_size: float, 
                              flags: int, confidence: float) -> Optional[str]:
        """Classify the heading level (H1, H2, H3)."""
        # Adaptive font size thresholds based on document
        if self.font_sizes_seen:
            max_font = max(self.font_sizes_seen)
            avg_font = sum(self.font_sizes_seen) / len(self.font_sizes_seen)
            
            # Adjust thresholds based on document's font size distribution
            h1_threshold = max(avg_font * 1.4, 16)
            h2_threshold = max(avg_font * 1.2, 14)
            h3_threshold = max(avg_font * 1.1, 12)
        else:
            h1_threshold = self.font_thresholds['h1_min']
            h2_threshold = self.font_thresholds['h2_min']
            h3_threshold = self.font_thresholds['h3_min']
        
        # Pattern-based classification
        if re.match(r'^(Chapter|CHAPTER)\s+\d+', text):
            return "H1"
        elif re.match(r'^(Section|SECTION)\s+\d+', text):
            return "H2"
        elif re.match(r'^\d+\.\s+', text):
            return "H1"
        elif re.match(r'^\d+\.\d+\s+', text):
            return "H2"
        elif re.match(r'^\d+\.\d+\.\d+\s+', text):
            return "H3"
        
        # Font size based classification
        if font_size >= h1_threshold and confidence > 0.5:
            return "H1"
        elif font_size >= h2_threshold and confidence > 0.4:
            return "H2"
        elif font_size >= h3_threshold and confidence > 0.3:
            return "H3"
        
        # Default to H2 for moderate confidence headings
        if confidence > 0.5:
            return "H2"
        elif confidence > 0.4:
            return "H3"
        
        return None
    
    def _clean_heading_text(self, text: str) -> str:
        """Clean and normalize heading text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove trailing punctuation (except periods in numbered headings)
        if not re.match(r'^\d+\.', text):
            text = re.sub(r'[.,:;!?]+$', '', text)
        
        return text
