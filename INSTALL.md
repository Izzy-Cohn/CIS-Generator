# Installation Guide for CIS-Generator

This guide will help you set up and run the CIS-Generator tool on your system.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/CIS-Generator.git
cd CIS-Generator
```

### 2. Create and Activate a Virtual Environment

#### On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

#### On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download NLP Models

```bash
python -m spacy download en_core_web_sm
python -m nltk.downloader punkt stopwords wordnet
```

### 5. Configure Environment Variables

Copy the example environment file and edit it as needed:

```bash
cp .env.example .env
```

Edit the `.env` file to set your configuration options.

## Running the Application

### Using the Run Script

The easiest way to run the application is using the provided run script:

```bash
./run.py
```

This will:
1. Create necessary directories
2. Check for required NLP models and download them if needed
3. Start the Flask application

### Manual Start

Alternatively, you can start the application manually:

```bash
flask run
```

or

```bash
python app.py
```

## Accessing the Application

Once running, access the application in your web browser at:

```
http://localhost:5000
```

## Testing

To test the document extraction functionality:

```bash
cd tests
./test_extraction.py path/to/your/document.pdf
```

## Troubleshooting

### Missing Dependencies

If you encounter errors about missing dependencies, try reinstalling the requirements:

```bash
pip install -r requirements.txt
```

### NLP Model Issues

If you encounter errors related to spaCy or NLTK models:

```bash
python -m spacy download en_core_web_sm
python -m nltk.downloader punkt stopwords wordnet
```

### Permission Issues

If you encounter permission issues with the run script:

```bash
chmod +x run.py
chmod +x tests/test_extraction.py
``` 