#!/usr/bin/env python3
"""
Test script for document extraction functionality
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from processors.extractors.pdf_extractor import PDFExtractor
from processors.nlp.document_analyzer import DocumentAnalyzer
from utils.config_loader import ConfigLoader
from models.document import Document

def test_pdf_extraction(pdf_path):
    """Test PDF text extraction"""
    print(f"\n=== Testing PDF Extraction on {pdf_path} ===")
    
    extractor = PDFExtractor()
    
    try:
        # Extract text
        text = extractor.extract_text(pdf_path)
        print(f"Extracted {len(text)} characters of text")
        
        # Print a sample
        sample_size = min(500, len(text))
        print(f"\nSample of extracted text ({sample_size} chars):")
        print("-" * 80)
        print(text[:sample_size] + "...")
        print("-" * 80)
        
        # Extract metadata
        metadata = extractor.extract_metadata(pdf_path)
        print("\nMetadata:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")
            
        # Extract tables
        tables = extractor.extract_tables(pdf_path)
        print(f"\nExtracted {len(tables)} tables")
        
        return text
    except Exception as e:
        print(f"Error during extraction: {str(e)}")
        return None

def test_document_analysis(text):
    """Test document analysis with NLP"""
    if not text:
        print("No text to analyze")
        return None
        
    print("\n=== Testing Document Analysis ===")
    
    # Load configuration
    config = ConfigLoader()
    
    # Create document
    document = Document()
    document.set_content(text)
    
    # Create analyzer
    analyzer = DocumentAnalyzer(config.get_nlp_config())
    
    try:
        # Analyze document
        extracted_data = analyzer.analyze(document)
        
        # Print document type
        print(f"Document Type: {extracted_data.get('document_type', 'Unknown')}")
        
        # Print property information
        property_info = extracted_data.get('property', {})
        print("\nProperty Information:")
        for key, value in property_info.items():
            if value:
                print(f"  {key}: {value}")
                
        # Print parties
        parties = extracted_data.get('parties', {})
        print("\nParties:")
        for key, value in parties.items():
            if value:
                print(f"  {key}: {value}")
                
        # Print monetary values
        monetary = extracted_data.get('monetary_values', {})
        print("\nMonetary Values:")
        for key, value in monetary.items():
            if value and key != 'other_amounts':
                print(f"  {key}: {value}")
                
        # Print dates
        dates = extracted_data.get('dates', {})
        print("\nDates:")
        for key, value in dates.items():
            if value and key != 'other_dates':
                print(f"  {key}: {value}")
                
        # Save extraction results
        output_file = "test_extraction_results.json"
        with open(output_file, 'w') as f:
            json.dump(extracted_data, f, indent=4)
        print(f"\nSaved extraction results to {output_file}")
        
        return extracted_data
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        return None

def main():
    """Main function"""
    # Check if PDF path is provided
    if len(sys.argv) < 2:
        print("Usage: python test_extraction.py <pdf_file>")
        return
        
    pdf_path = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return
        
    # Test PDF extraction
    text = test_pdf_extraction(pdf_path)
    
    # Test document analysis
    if text:
        extracted_data = test_document_analysis(text)
        
        if extracted_data:
            print("\n=== Extraction Test Completed Successfully ===")
        else:
            print("\n=== Extraction Test Failed ===")
    else:
        print("\n=== Extraction Test Failed ===")

if __name__ == "__main__":
    main() 