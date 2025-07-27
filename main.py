#!/usr/bin/env python3
"""
PDF Document Structure Extractor
Main entry point for processing PDFs and extracting document structure.
"""

import os
import sys
import json
import time
from pathlib import Path
from pdf_extractor import PDFExtractor

def process_pdf_files():
    """Process all PDF files from input directory and generate JSON outputs."""
    # Use Docker paths if running in container, local paths otherwise
    if os.path.exists("/app"):
        input_dir = Path("/app/input")
        output_dir = Path("/app/output")
    else:
        input_dir = Path("input")
        output_dir = Path("output")
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if input directory exists
    if not input_dir.exists():
        print(f"Input directory {input_dir} does not exist")
        return
    
    # Find all PDF files in input directory
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in input directory")
        return
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    # Initialize PDF extractor
    extractor = PDFExtractor()
    
    # Process each PDF file
    for pdf_file in pdf_files:
        try:
            start_time = time.time()
            print(f"Processing: {pdf_file.name}")
            
            # Extract document structure
            result = extractor.extract_structure(str(pdf_file))
            
            # Generate output filename
            output_filename = pdf_file.stem + ".json"
            output_path = output_dir / output_filename
            
            # Write JSON output
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            processing_time = time.time() - start_time
            print(f"Completed: {pdf_file.name} -> {output_filename} ({processing_time:.2f}s)")
            
        except Exception as e:
            print(f"Error processing {pdf_file.name}: {str(e)}")
            # Create error output
            error_result = {
                "title": "Error extracting title",
                "outline": [],
                "error": str(e)
            }
            output_filename = pdf_file.stem + ".json"
            output_path = output_dir / output_filename
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(error_result, f, indent=2)

def main():
    """Main function."""
    print("PDF Document Structure Extractor v1.0")
    # Dynamic message based on environment
    if os.path.exists("/app"):
        print("Processing PDFs from /app/input to /app/output")
    else:
        print("Processing PDFs from input to output")
    
    try:
        process_pdf_files()
        print("Processing completed successfully")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
