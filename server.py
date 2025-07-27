#!/usr/bin/env python3
"""
PDF Document Structure Extractor Web Server
Provides a web interface for uploading and processing PDFs.
"""

from flask import Flask, request, jsonify, render_template_string, send_file
import os
import json
import tempfile
from pathlib import Path
from pdf_extractor import PDFExtractor
import zipfile
from io import BytesIO

app = Flask(__name__)

# Initialize PDF extractor
extractor = PDFExtractor()

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>PDF Document Structure Extractor</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .upload-area { border: 2px dashed #ccc; padding: 40px; text-align: center; margin: 20px 0; }
        .upload-area:hover { border-color: #999; }
        .results { margin: 20px 0; padding: 20px; background: #f5f5f5; border-radius: 5px; }
        .heading { margin: 10px 0; padding: 5px; border-left: 3px solid #007bff; }
        .h1 { margin-left: 0px; border-color: #dc3545; }
        .h2 { margin-left: 20px; border-color: #ffc107; }
        .h3 { margin-left: 40px; border-color: #28a745; }
        .error { color: red; padding: 10px; background: #ffe6e6; border-radius: 5px; }
        .success { color: green; padding: 10px; background: #e6ffe6; border-radius: 5px; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .json-output { background: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; border-radius: 5px; font-family: monospace; white-space: pre-wrap; }
    </style>
</head>
<body>
    <h1>PDF Document Structure Extractor</h1>
    <p>Upload PDF files to extract their document structure including titles and hierarchical headings (H1-H3).</p>
    
    <form id="uploadForm" enctype="multipart/form-data">
        <div class="upload-area" onclick="document.getElementById('fileInput').click()">
            <input type="file" id="fileInput" name="files" multiple accept=".pdf" style="display: none;">
            <p>Click here to select PDF files or drag and drop them</p>
            <p><small>Supports multiple files up to 50 pages each</small></p>
        </div>
        <button type="submit">Process PDFs</button>
    </form>
    
    <div id="results"></div>
    
    <script>
        const form = document.getElementById('uploadForm');
        const fileInput = document.getElementById('fileInput');
        const results = document.getElementById('results');
        
        // Drag and drop functionality
        const uploadArea = document.querySelector('.upload-area');
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = '#007bff';
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.style.borderColor = '#ccc';
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = '#ccc';
            fileInput.files = e.dataTransfer.files;
            updateFileList();
        });
        
        fileInput.addEventListener('change', updateFileList);
        
        function updateFileList() {
            const files = fileInput.files;
            if (files.length > 0) {
                const fileList = Array.from(files).map(f => f.name).join(', ');
                uploadArea.innerHTML = `<p>Selected files: ${fileList}</p>`;
            }
        }
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            if (fileInput.files.length === 0) {
                results.innerHTML = '<div class="error">Please select at least one PDF file.</div>';
                return;
            }
            
            const formData = new FormData();
            for (let file of fileInput.files) {
                formData.append('files', file);
            }
            
            results.innerHTML = '<div>Processing PDFs...</div>';
            
            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                displayResults(data);
            } catch (error) {
                results.innerHTML = `<div class="error">Error: ${error.message}</div>`;
            }
        });
        
        function displayResults(data) {
            if (data.error) {
                results.innerHTML = `<div class="error">${data.error}</div>`;
                return;
            }
            
            let html = '<div class="success">Processing completed successfully!</div>';
            
            data.results.forEach(result => {
                html += `<div class="results">`;
                html += `<h3>📄 ${result.filename}</h3>`;
                html += `<p><strong>Title:</strong> ${result.data.title}</p>`;
                
                // Summary feature removed for competition requirements
                
                if (result.data.outline.length > 0) {
                    html += `<h4>📋 Document Structure:</h4>`;
                    result.data.outline.forEach(item => {
                        const level = item.level.toLowerCase();
                        html += `<div class="heading ${level}">`;
                        html += `<strong>${item.level}:</strong> ${item.text} <span style="color: #666;">(Page ${item.page})</span>`;
                        html += `</div>`;
                    });
                } else {
                    html += `<p><em>No headings detected in this document.</em></p>`;
                }
                
                html += `<h4>📊 JSON Output:</h4>`;
                html += `<div class="json-output">${JSON.stringify(result.data, null, 2)}</div>`;
                html += `</div>`;
            });
            
            results.innerHTML = html;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the main web interface."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle PDF file uploads and process them."""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        if not files:
            return jsonify({'error': 'No files selected'}), 400
        
        results = []
        
        for file in files:
            if file.filename == '':
                continue
                
            if not file.filename.lower().endswith('.pdf'):
                results.append({
                    'filename': file.filename,
                    'error': 'File is not a PDF'
                })
                continue
            
            try:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                    file.save(temp_file.name)
                    
                    # Process the PDF (no summarization for competition)
                    result = extractor.extract_structure(temp_file.name)
                    
                    results.append({
                        'filename': file.filename,
                        'data': result
                    })
                    
                    # Clean up temp file
                    os.unlink(temp_file.name)
                    
            except Exception as e:
                results.append({
                    'filename': file.filename,
                    'error': str(e)
                })
        
        return jsonify({'results': results})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/batch')
def batch_process():
    """Process all PDFs in the input directory (legacy batch mode)."""
    try:
        input_dir = Path("input")
        output_dir = Path("output")
        
        if not input_dir.exists():
            return jsonify({'error': 'Input directory does not exist'}), 400
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all PDF files
        pdf_files = list(input_dir.glob("*.pdf"))
        
        if not pdf_files:
            return jsonify({'message': 'No PDF files found in input directory'})
        
        results = []
        
        for pdf_file in pdf_files:
            try:
                # Extract document structure
                result = extractor.extract_structure(str(pdf_file))
                
                # Generate output filename
                output_filename = pdf_file.stem + ".json"
                output_path = output_dir / output_filename
                
                # Write JSON output
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                results.append({
                    'filename': pdf_file.name,
                    'output': output_filename,
                    'data': result
                })
                
            except Exception as e:
                results.append({
                    'filename': pdf_file.name,
                    'error': str(e)
                })
        
        return jsonify({
            'message': f'Processed {len(pdf_files)} PDF files',
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'message': 'PDF Document Structure Extractor is running'})

if __name__ == '__main__':
    print("Starting PDF Document Structure Extractor Web Server...")
    print("Web interface will be available at http://0.0.0.0:5000")
    print("API endpoints:")
    print("  - POST /upload - Upload and process PDF files")
    print("  - GET /batch - Process PDFs from input directory")
    print("  - GET /health - Health check")
    
    app.run(host='0.0.0.0', port=5000, debug=True)