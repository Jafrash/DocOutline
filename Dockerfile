# Use Python 3.9 slim image for minimal size
FROM --platform=linux/amd64 python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    PyMuPDF==1.23.14 \
    && rm -rf /root/.cache/pip

# Copy application files
COPY main.py /app/
COPY pdf_extractor.py /app/
COPY heading_detector.py /app/

# Create input and output directories
RUN mkdir -p /app/input /app/output

# Make main.py executable
RUN chmod +x /app/main.py

# Set the default command
CMD ["python", "/app/main.py"]
