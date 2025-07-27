# PDF Document Structure Extractor

A high-performance PDF document structure extraction tool optimized for competition requirements. Extract hierarchical document structure including titles and headings (H1-H3) from PDF documents with high accuracy and speed.

## Features

- 🔍 **Document Structure Extraction**: Automatically identifies titles and hierarchical headings (H1, H2, H3)
- ⚡ **High Performance**: Processing time <0.03 seconds for complex documents
- 🎯 **Competition Optimized**: Meets all competition constraints (≤10s for 50-page PDFs, CPU-only, no internet)
- 📁 **Batch Processing**: Process multiple PDFs simultaneously
- 🌐 **Web Interface**: Optional web interface for testing and development
- 📋 **Structured Output**: Clean JSON output with titles and hierarchical headings
- 🔧 **Robust Detection**: Advanced heading detection beyond simple font size analysis

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key (optional, for AI summaries)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd pdf-document-extractor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (optional):
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### Usage

#### Web Interface

Start the web server:
```bash
python server.py
```

Open your browser to `http://localhost:5000` and upload PDF files through the drag-and-drop interface.

#### Batch Processing

Place PDF files in the `input/` directory and run:
```bash
python main.py
```

Processed JSON files will be saved to the `output/` directory.

#### Programmatic Usage

```python
from pdf_extractor import PDFExtractor

extractor = PDFExtractor()
result = extractor.extract_structure("document.pdf", include_summary=True)

print(f"Title: {result['title']}")
print(f"Summary: {result['summary']}")
for heading in result['outline']:
    print(f"{heading['level']}: {heading['text']} (Page {heading['page']})")
```

## API Endpoints

- `GET /` - Web interface
- `POST /upload` - Upload and process PDF files
- `GET /batch` - Process PDFs from input directory
- `GET /health` - Health check

## Output Format

```json
{
  "title": "Document Title",
  "summary": "AI-generated or text-based summary of the document content...",
  "outline": [
    {
      "level": "H1",
      "text": "Chapter 1: Introduction",
      "page": 1
    },
    {
      "level": "H2", 
      "text": "1.1 Overview",
      "page": 1
    }
  ]
}
```

## Architecture

- **PDF Processing**: PyMuPDF (fitz) for fast, reliable PDF text extraction
- **Heading Detection**: Rule-based classification with adaptive thresholding
- **AI Integration**: OpenAI GPT-4o for intelligent content summarization
- **Web Framework**: Flask for the web interface
- **Fallback System**: Text analysis when AI is unavailable

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: OpenAI API key for AI-powered summaries (optional)

### Processing Limits

- Maximum pages per document: 50
- Supported formats: PDF only
- Text truncation for AI: 50,000 characters

## Performance

- Typical processing time: <0.02 seconds per document
- Memory efficient streaming processing
- CPU-only operation (no GPU required)

## Error Handling

The system includes comprehensive error handling:
- Graceful degradation when AI is unavailable
- Continues processing if individual PDFs fail
- Detailed error messages in JSON output
- Automatic fallback to text-based summaries

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check existing issues on GitHub
2. Create a new issue with detailed description
3. Include sample PDF files if relevant

## Recent Updates

- Added AI-powered text summarization with OpenAI integration
- Implemented fallback text summarization for when AI is unavailable
- Enhanced web interface with drag-and-drop file upload
- Added real-time processing with visual results display
- Improved error handling and graceful degradation# DocOutline
