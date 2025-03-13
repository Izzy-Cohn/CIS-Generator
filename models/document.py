import os
import json
from datetime import datetime

class Document:
    """
    Represents a legal document with its content and metadata.
    """
    
    def __init__(self, file_path=None):
        """
        Initialize a document object
        
        Args:
            file_path (str, optional): Path to the PDF file
        """
        self.file_path = file_path
        self.filename = os.path.basename(file_path) if file_path else None
        self.content = None
        self.metadata = {
            "created_at": datetime.now().isoformat(),
            "file_path": file_path,
            "filename": self.filename,
            "document_type": None,
            "processed": False
        }
        self.extracted_data = {}
        
    def set_content(self, content):
        """
        Set the text content of the document
        
        Args:
            content (str): The extracted text content
        """
        self.content = content
        self.metadata["processed"] = True
        self.metadata["processed_at"] = datetime.now().isoformat()
        
    def set_document_type(self, doc_type):
        """
        Set the document type (e.g., lease, mortgage, contract)
        
        Args:
            doc_type (str): The document type
        """
        self.metadata["document_type"] = doc_type
        
    def add_extracted_data(self, key, value):
        """
        Add a key-value pair to the extracted data
        
        Args:
            key (str): The data field name
            value: The extracted value
        """
        self.extracted_data[key] = value
        
    def update_extracted_data(self, data_dict):
        """
        Update the extracted data with a dictionary
        
        Args:
            data_dict (dict): Dictionary of extracted data
        """
        self.extracted_data.update(data_dict)
        
    def get_extracted_data(self):
        """
        Get the extracted data
        
        Returns:
            dict: The extracted data dictionary
        """
        return self.extracted_data
        
    def to_dict(self):
        """
        Convert the document to a dictionary
        
        Returns:
            dict: Dictionary representation of the document
        """
        return {
            "metadata": self.metadata,
            "extracted_data": self.extracted_data
        }
        
    def to_json(self):
        """
        Convert the document to a JSON string
        
        Returns:
            str: JSON string representation of the document
        """
        return json.dumps(self.to_dict(), indent=4)
        
    def save_extraction_results(self, output_path):
        """
        Save the extraction results to a JSON file
        
        Args:
            output_path (str): Path to save the JSON file
        """
        with open(output_path, 'w') as f:
            f.write(self.to_json())
            
    @classmethod
    def from_json(cls, json_path):
        """
        Create a document from a JSON file
        
        Args:
            json_path (str): Path to the JSON file
            
        Returns:
            Document: A new Document instance
        """
        with open(json_path, 'r') as f:
            data = json.load(f)
            
        doc = cls(data.get("metadata", {}).get("file_path"))
        doc.metadata = data.get("metadata", {})
        doc.extracted_data = data.get("extracted_data", {})
        
        return doc 