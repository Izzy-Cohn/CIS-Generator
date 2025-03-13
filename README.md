# CIS-Generator

A tool for analyzing legal documents from real estate financing transactions and generating custom information sheets.

## Overview

CIS-Generator is designed to process large sets of legal documents in PDF format, extract relevant data using NLP techniques, and generate structured forms based on user-provided templates. This tool is particularly useful for real estate professionals, lawyers, and financial institutions that need to process large volumes of contracts, leases, mortgages, and other legal documents.

## Features

- **PDF Document Processing**: Extract text and structured data from PDF files
- **Intelligent Data Extraction**: Identify and extract key information from legal documents
- **Template-Based Form Generation**: Generate forms based on customizable templates
- **Batch Processing**: Process multiple documents in a single operation
- **User-Friendly Interface**: Simple web interface for uploading documents and templates

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/CIS-Generator.git
   cd CIS-Generator
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Download the required NLP models:
   ```
   python -m spacy download en_core_web_lg
   python -m nltk.downloader punkt stopwords wordnet
   ```

## Usage

1. Start the application:
   ```
   python app.py
   ```

2. Open your web browser and navigate to `http://localhost:5000`

3. Upload your PDF documents and template files

4. Configure extraction settings

5. Generate forms based on the extracted data

## Project Structure

```
CIS-Generator/
├── app.py                  # Main Flask application
├── config/                 # Configuration files
├── models/                 # Data models
├── processors/             # Document processing modules
│   ├── pdf_extractor.py    # PDF text extraction
│   ├── nlp_processor.py    # NLP processing
│   └── form_generator.py   # Form generation
├── static/                 # Static files (CSS, JS)
├── templates/              # HTML templates
├── utils/                  # Utility functions
└── tests/                  # Unit tests
```

## Template Format

Templates should be provided as DOCX or JSON files with placeholders for the extracted data. See the examples in the `examples/templates/` directory.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
