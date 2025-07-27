# PDF Document Structure Extractor

## Overview

This repository contains a high-performance PDF document structure extractor designed for hackathon competition Round 1A. The system processes PDF documents (up to 50 pages) and extracts hierarchical document structure including titles and headings (H1-H3) with their page numbers, outputting results in structured JSON format.

## User Preferences

Preferred communication style: Simple, everyday language.

## Project Status

**COMPLETED**: Ready for hackathon competition Round 1A
- All core requirements implemented and tested
- Docker container optimized for AMD64 architecture
- Performance meets <10 second requirement for 50-page documents
- JSON output format matches competition specifications
- Multi-language support included
- Error handling and graceful degradation implemented

## System Architecture

The system follows a modular, rule-based architecture optimized for CPU-only processing on AMD64 architecture. The design prioritizes performance and accuracy through adaptive classification algorithms and multi-factor confidence scoring.

### Core Architecture Components

1. **Main Processing Pipeline** (`main.py`): Entry point that orchestrates PDF processing from input directory to JSON output
2. **PDF Extraction Engine** (`pdf_extractor.py`): Core extraction logic using PyMuPDF for PDF parsing
3. **Heading Detection System** (`heading_detector.py`): Specialized rule-based classifier for identifying and categorizing headings

## Key Components

### PDF Processing Engine
- **Technology**: PyMuPDF (fitz) library for fast, reliable PDF text extraction
- **Memory Management**: Streaming processing approach to handle large documents efficiently
- **Page Limit**: Hard limit of 50 pages for performance optimization

### Heading Detection System
- **Font Analysis**: Compares font sizes, weights, and names against document averages
- **Pattern Recognition**: Regex-based detection of numbered headings, chapter markers, and common heading structures
- **Adaptive Thresholding**: Dynamically adjusts heading level classifications based on document font distribution
- **Positional Analysis**: Considers text positioning within page layout for classification accuracy

### Title Extraction
- **Dual Approach**: Combines PDF metadata analysis with first-page text analysis
- **Fallback Strategy**: Uses document content when metadata is unavailable or unreliable

## Data Flow

1. **Input Processing**: Scans `/app/input` directory for PDF files
2. **Document Opening**: Uses PyMuPDF to load and validate PDF documents
3. **Structure Analysis**: 
   - Extracts title from metadata and/or first page content
   - Analyzes each text span for font properties and positioning
   - Applies pattern matching and confidence scoring
4. **Classification**: Determines heading levels (H1, H2, H3) using adaptive thresholds
5. **Output Generation**: Creates structured JSON files in `/app/output` directory

## External Dependencies

### Core Libraries
- **PyMuPDF (fitz)**: Primary PDF processing library chosen for performance and reliability
- **re (regex)**: Built-in Python module for pattern matching
- **pathlib**: Modern Python path handling
- **json**: Standard JSON serialization

### Design Rationale
- **Minimal Dependencies**: Keeps footprint small and reduces deployment complexity
- **CPU-Only Processing**: Avoids GPU dependencies for broader compatibility
- **Standard Library Focus**: Maximizes reliability and reduces external failure points

## Deployment Strategy

### Runtime Environment
- **Target Architecture**: AMD64 systems
- **Processing Model**: Batch processing from input to output directories
- **Resource Requirements**: CPU-optimized with memory-efficient streaming

### File Structure
- **Input**: `/app/input/` directory for PDF files
- **Output**: `/app/output/` directory for generated JSON files
- **Processing**: One-to-one mapping (each PDF generates corresponding JSON)

### Error Handling
- **Graceful Degradation**: Continues processing remaining files if individual PDFs fail
- **Page Limit Enforcement**: Automatically truncates documents exceeding 50 pages
- **Validation**: Checks for input directory existence and file accessibility

### Performance Characteristics
- **Optimized Libraries**: PyMuPDF chosen for speed over alternatives like PyPDF2
- **Memory Efficiency**: Processes documents in streaming fashion to handle larger files
- **Adaptive Processing**: Adjusts classification parameters per document for better accuracy