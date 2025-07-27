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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DocOutline - PDF Structure Extractor</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .header {
            text-align: center;
            margin-bottom: 3rem;
            color: white;
        }
        
        .header h1 {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .header .subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
            font-weight: 300;
        }
        
        .main-card {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            overflow: hidden;
            margin-bottom: 2rem;
        }
        
        .card-header {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            padding: 2rem;
            text-align: center;
            color: white;
        }
        
        .card-header h2 {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        
        .card-body {
            padding: 2.5rem;
        }
        
        .upload-zone {
            border: 3px dashed #e1e5e9;
            border-radius: 15px;
            padding: 3rem 2rem;
            text-align: center;
            background: #f8fafc;
            transition: all 0.3s ease;
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }
        
        .upload-zone:hover {
            border-color: #4facfe;
            background: #f0f9ff;
            transform: translateY(-2px);
        }
        
        .upload-zone.dragover {
            border-color: #4facfe;
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            transform: scale(1.02);
        }
        
        .upload-icon {
            font-size: 4rem;
            color: #4facfe;
            margin-bottom: 1rem;
            display: block;
        }
        
        .upload-text {
            font-size: 1.25rem;
            font-weight: 500;
            color: #334155;
            margin-bottom: 0.5rem;
        }
        
        .upload-subtext {
            color: #64748b;
            font-size: 0.95rem;
        }
        
        .selected-files {
            margin-top: 1rem;
            padding: 1rem;
            background: #e0f2fe;
            border-radius: 10px;
            border-left: 4px solid #4facfe;
        }
        
        .process-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 50px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 1.5rem;
            width: 100%;
            position: relative;
            overflow: hidden;
        }
        
        .process-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        
        .process-btn:disabled {
            opacity: 0.7;
            cursor: not-allowed;
            transform: none;
        }
        
        .loading {
            display: none;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }
        
        .spinner {
            width: 20px;
            height: 20px;
            border: 2px solid rgba(255,255,255,0.3);
            border-top: 2px solid white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .results-section {
            margin-top: 2rem;
        }
        
        .result-card {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.08);
            margin-bottom: 1.5rem;
            overflow: hidden;
            border: 1px solid #e2e8f0;
        }
        
        .result-header {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            padding: 1.5rem;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .result-title {
            font-size: 1.3rem;
            font-weight: 600;
            color: #1e293b;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .result-body {
            padding: 1.5rem;
        }
        
        .document-title {
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid #f59e0b;
            margin-bottom: 1.5rem;
        }
        
        .heading-item {
            padding: 0.75rem 1rem;
            margin: 0.5rem 0;
            border-radius: 8px;
            border-left: 4px solid;
            background: #f8fafc;
            transition: all 0.2s ease;
        }
        
        .heading-item:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .h1 {
            border-left-color: #ef4444;
            background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
            margin-left: 0;
        }
        
        .h2 {
            border-left-color: #f59e0b;
            background: linear-gradient(135deg, #fefbeb 0%, #fef3c7 100%);
            margin-left: 1.5rem;
        }
        
        .h3 {
            border-left-color: #10b981;
            background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
            margin-left: 3rem;
        }
        
        .heading-level {
            font-weight: 600;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .heading-text {
            font-weight: 500;
            margin: 0.25rem 0;
        }
        
        .heading-page {
            font-size: 0.85rem;
            color: #64748b;
        }
        
        .json-section {
            margin-top: 1.5rem;
            background: #1e293b;
            border-radius: 10px;
            padding: 1.5rem;
            color: #e2e8f0;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.9rem;
            line-height: 1.5;
            overflow-x: auto;
        }
        
        .json-header {
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid #334155;
        }
        
        .alert {
            padding: 1rem 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
            font-weight: 500;
        }
        
        .alert-success {
            background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
            color: #065f46;
            border-left: 4px solid #10b981;
        }
        
        .alert-error {
            background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
            color: #991b1b;
            border-left: 4px solid #ef4444;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
        }
        
        .stat-number {
            font-size: 2rem;
            font-weight: 700;
            color: #4facfe;
        }
        
        .stat-label {
            font-size: 0.9rem;
            color: #64748b;
            margin-top: 0.25rem;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 1rem;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .card-body {
                padding: 1.5rem;
            }
            
            .upload-zone {
                padding: 2rem 1rem;
            }
            
            .h2, .h3 {
                margin-left: 0.5rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-file-pdf"></i> DocOutline</h1>
            <p class="subtitle">Extract document structure and headings from PDF files</p>
        </div>
        
        <div class="main-card">
            <div class="card-header">
                <h2><i class="fas fa-upload"></i> Upload Your PDFs</h2>
                <p>Drag and drop or click to select PDF files for analysis</p>
            </div>
            
            <div class="card-body">
                <form id="uploadForm" enctype="multipart/form-data">
                    <div class="upload-zone" onclick="document.getElementById('fileInput').click()">
                        <input type="file" id="fileInput" name="files" multiple accept=".pdf" style="display: none;">
                        <i class="fas fa-cloud-upload-alt upload-icon"></i>
                        <div class="upload-text">Drop PDF files here or click to browse</div>
                        <div class="upload-subtext">Supports multiple files • Up to 50 pages each • Fast processing</div>
                    </div>
                    
                    <div id="selectedFiles" class="selected-files" style="display: none;">
                        <i class="fas fa-files"></i> <span id="fileCount">0</span> files selected
                    </div>
                    
                    <button type="submit" class="process-btn" id="processBtn">
                        <span class="btn-text">
                            <i class="fas fa-cogs"></i> Extract Document Structure
                        </span>
                        <div class="loading">
                            <div class="spinner"></div>
                            Processing...
                        </div>
                    </button>
                </form>
            </div>
        </div>
        
        <div id="results" class="results-section"></div>
    </div>
    
    <script>
        const form = document.getElementById('uploadForm');
        const fileInput = document.getElementById('fileInput');
        const results = document.getElementById('results');
        const uploadZone = document.querySelector('.upload-zone');
        const selectedFiles = document.getElementById('selectedFiles');
        const fileCount = document.getElementById('fileCount');
        const processBtn = document.getElementById('processBtn');
        const btnText = processBtn.querySelector('.btn-text');
        const loading = processBtn.querySelector('.loading');
        
        // Enhanced drag and drop functionality
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('dragover');
        });
        
        uploadZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            if (!uploadZone.contains(e.relatedTarget)) {
                uploadZone.classList.remove('dragover');
            }
        });
        
        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
            fileInput.files = e.dataTransfer.files;
            updateFileList();
        });
        
        fileInput.addEventListener('change', updateFileList);
        
        function updateFileList() {
            const files = fileInput.files;
            if (files.length > 0) {
                const fileNames = Array.from(files).map(f => f.name);
                fileCount.textContent = files.length;
                selectedFiles.style.display = 'block';
                
                // Update upload zone appearance
                uploadZone.innerHTML = `
                    <i class="fas fa-check-circle upload-icon" style="color: #10b981;"></i>
                    <div class="upload-text" style="color: #10b981;">Files Selected</div>
                    <div class="upload-subtext">${fileNames.join(', ')}</div>
                `;
            } else {
                selectedFiles.style.display = 'none';
                uploadZone.innerHTML = `
                    <i class="fas fa-cloud-upload-alt upload-icon"></i>
                    <div class="upload-text">Drop PDF files here or click to browse</div>
                    <div class="upload-subtext">Supports multiple files • Up to 50 pages each • Fast processing</div>
                `;
            }
        }
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            if (fileInput.files.length === 0) {
                results.innerHTML = '<div class="alert alert-error"><i class="fas fa-exclamation-triangle"></i> Please select at least one PDF file.</div>';
                return;
            }
            
            // Show loading state
            processBtn.disabled = true;
            btnText.style.display = 'none';
            loading.style.display = 'flex';
            
            const formData = new FormData();
            for (let file of fileInput.files) {
                formData.append('files', file);
            }
            
            results.innerHTML = `
                <div class="alert" style="background: linear-gradient(135deg, #e0f2fe 0%, #b3e5fc 100%); color: #0277bd; border-left: 4px solid #03a9f4;">
                    <i class="fas fa-spinner fa-spin"></i> Processing ${fileInput.files.length} PDF file(s)...
                </div>
            `;
            
            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                displayResults(data);
            } catch (error) {
                results.innerHTML = `<div class="alert alert-error"><i class="fas fa-exclamation-triangle"></i> Error: ${error.message}</div>`;
            } finally {
                // Reset button state
                processBtn.disabled = false;
                btnText.style.display = 'flex';
                loading.style.display = 'none';
            }
        });
        
        function displayResults(data) {
            if (data.error) {
                results.innerHTML = `<div class="alert alert-error"><i class="fas fa-exclamation-triangle"></i> ${data.error}</div>`;
                return;
            }
            
            let html = '<div class="alert alert-success"><i class="fas fa-check-circle"></i> Processing completed successfully!</div>';
            
            // Calculate statistics
            let totalFiles = data.results.length;
            let totalHeadings = data.results.reduce((sum, result) => sum + (result.data.outline ? result.data.outline.length : 0), 0);
            let successfulFiles = data.results.filter(result => !result.error).length;
            
            html += `
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">${successfulFiles}</div>
                        <div class="stat-label">Files Processed</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${totalHeadings}</div>
                        <div class="stat-label">Headings Found</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${Math.round(totalHeadings/successfulFiles) || 0}</div>
                        <div class="stat-label">Avg per Document</div>
                    </div>
                </div>
            `;
            
            data.results.forEach(result => {
                html += `<div class="result-card">`;
                html += `<div class="result-header">`;
                html += `<div class="result-title"><i class="fas fa-file-pdf"></i> ${result.filename}</div>`;
                html += `</div>`;
                html += `<div class="result-body">`;
                
                if (result.error) {
                    html += `<div class="alert alert-error"><i class="fas fa-exclamation-triangle"></i> ${result.error}</div>`;
                } else {
                    html += `<div class="document-title">`;
                    html += `<strong><i class="fas fa-heading"></i> Document Title:</strong> ${result.data.title}`;
                    html += `</div>`;
                    
                    if (result.data.outline && result.data.outline.length > 0) {
                        html += `<h4 style="margin-bottom: 1rem; color: #1e293b;"><i class="fas fa-list"></i> Document Structure (${result.data.outline.length} headings)</h4>`;
                        result.data.outline.forEach(item => {
                            const level = item.level.toLowerCase();
                            html += `<div class="heading-item ${level}">`;
                            html += `<div class="heading-level">${item.level}</div>`;
                            html += `<div class="heading-text">${item.text}</div>`;
                            html += `<div class="heading-page"><i class="fas fa-bookmark"></i> Page ${item.page}</div>`;
                            html += `</div>`;
                        });
                    } else {
                        html += `<div class="alert alert-error"><i class="fas fa-info-circle"></i> No headings detected in this document.</div>`;
                    }
                    
                    html += `<div class="json-section">`;
                    html += `<div class="json-header">`;
                    html += `<span><i class="fas fa-code"></i> JSON Output</span>`;
                    html += `</div>`;
                    html += `<pre>${JSON.stringify(result.data, null, 2)}</pre>`;
                    html += `</div>`;
                }
                
                html += `</div></div>`;
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