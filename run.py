#!/usr/bin/env python3
"""
Run script for CIS-Generator
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create required directories
required_dirs = [
    os.getenv('UPLOAD_FOLDER', 'uploads'),
    os.getenv('TEMP_FOLDER', 'temp'),
    os.getenv('RESULT_FOLDER', 'results'),
    os.getenv('CONFIG_FOLDER', 'config')
]

for directory in required_dirs:
    os.makedirs(directory, exist_ok=True)
    print(f"Ensured directory exists: {directory}")

# Check if config file exists, create if not
config_file = os.path.join(os.getenv('CONFIG_FOLDER', 'config'), 'extraction_config.json')
if not os.path.exists(config_file):
    from utils.config_loader import ConfigLoader
    config = ConfigLoader()
    config.save_config(config_file)
    print(f"Created default configuration file: {config_file}")

# Check for required NLP models
try:
    import spacy
    spacy_model = os.getenv('SPACY_MODEL', 'en_core_web_sm')
    try:
        nlp = spacy.load(spacy_model)
        print(f"Loaded spaCy model: {spacy_model}")
    except OSError:
        print(f"Downloading spaCy model: {spacy_model}")
        spacy.cli.download(spacy_model)
        print(f"Downloaded spaCy model: {spacy_model}")
except ImportError:
    print("Warning: spaCy not installed. NLP features will not work.")

# Check for NLTK resources
try:
    import nltk
    nltk_resources = ['punkt', 'stopwords', 'wordnet']
    for resource in nltk_resources:
        try:
            nltk.data.find(f'tokenizers/{resource}' if resource == 'punkt' else f'corpora/{resource}')
            print(f"Found NLTK resource: {resource}")
        except LookupError:
            print(f"Downloading NLTK resource: {resource}")
            nltk.download(resource)
            print(f"Downloaded NLTK resource: {resource}")
except ImportError:
    print("Warning: NLTK not installed. Some NLP features may not work.")

# Run the application
if __name__ == "__main__":
    from app import app
    
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')
    
    print(f"Starting CIS-Generator on {host}:{port} (debug={debug})")
    app.run(host=host, port=port, debug=debug) 