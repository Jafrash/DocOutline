# PDF Document Structure Extractor

A high-performance PDF document structure extractor that identifies titles and headings (H1-H3) for hackathon competition Round 1A.

## Overview

This solution processes PDF documents up to 50 pages and extracts:
- Document title
- Hierarchical headings (H1, H2, H3) with page numbers
- Outputs structured JSON format

## Approach

### Core Components

1. **PDF Processing**: Uses PyMuPDF (fitz) for fast, reliable PDF text extraction
2. **Heading Detection**: Rule-based system analyzing font properties, text patterns, and document structure
3. **Title Extraction**: Combines metadata analysis with first-page text analysis
4. **Adaptive Classification**: Adjusts heading level thresholds based on document font distribution

### Detection Strategy

#### Font Analysis
- Font size comparison against document average
- Bold/weight detection through font flags and names
- Adaptive thresholding based on document characteristics

#### Pattern Recognition
- Numbered headings (1., 1.1, 1.1.1)
- Chapter/Section markers
- Common heading keywords
- Capitalization patterns

#### Positional Analysis
- Text position within page layout
- Heading length optimization
- Page-relative positioning

## Technical Details

### Performance Optimizations
- CPU-only processing for AMD64 architecture
- Memory-efficient streaming processing
- Fast PyMuPDF library for PDF parsing
- Minimal dependency footprint

### Accuracy Features
- Multi-factor confidence scoring
- Adaptive font size thresholds
- Pattern-based heading classification
- Text cleaning and normalization

## Building and Running

### Docker Build
```bash
docker build --platform linux/amd64 -t pdf-extractor:latest .
```

### Docker Run
```bash
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none pdf-extractor:latest
```

## Libraries Used

### Primary Dependencies
- **PyMuPDF (fitz) v1.23.14**: Fast, reliable PDF text extraction and analysis
  - Chosen for superior performance over alternatives like PyPDF2
  - Provides detailed font and formatting information
  - Memory-efficient processing of large documents

### Built-in Python Libraries
- **re**: Regular expression pattern matching for heading detection
- **pathlib**: Modern path handling and file operations
- **json**: Standard JSON serialization for output
- **os**: Environment detection and system operations

## Performance Characteristics

- **Processing Speed**: < 10 seconds for 50-page documents
- **Memory Efficiency**: Streaming processing approach
- **Accuracy**: Multi-factor confidence scoring with adaptive thresholds
- **Compatibility**: AMD64 architecture, CPU-only processing
- **Size**: Minimal container footprint with PyMuPDF as only external dependency

## Output Format

The solution generates JSON files with the following structure:

```json
{
  "title": "Document Title",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 1 },
    { "level": "H2", "text": "Background", "page": 1 },
    { "level": "H3", "text": "History", "page": 2 }
  ]
}
```

## Multilingual Support

The solution includes basic multilingual handling through:
- Unicode text preservation with UTF-8 encoding
- Character-agnostic pattern matching
- Font-based analysis independent of language
- Proper JSON serialization with `ensure_ascii=False`

## Architecture Summary

1. **Input Processing**: Automatically scans for all PDF files in input directory
2. **Document Analysis**: Extracts text with full formatting information
3. **Heading Detection**: Applies rule-based classification with confidence scoring
4. **Title Extraction**: Combines metadata and content analysis
5. **Output Generation**: Creates structured JSON with hierarchical outline
