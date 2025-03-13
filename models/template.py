import os
import json
from datetime import datetime
from docxtpl import DocxTemplate

class Template:
    """
    Represents a template for generating documents from extracted data.
    """
    
    def __init__(self, file_path=None):
        """
        Initialize a template object
        
        Args:
            file_path (str, optional): Path to the template file (DOCX or JSON)
        """
        self.file_path = file_path
        self.filename = os.path.basename(file_path) if file_path else None
        self.extension = os.path.splitext(file_path)[1].lower() if file_path else None
        self.template_type = 'docx' if self.extension == '.docx' else 'json'
        self.fields = []
        self.metadata = {
            "created_at": datetime.now().isoformat(),
            "file_path": file_path,
            "filename": self.filename,
            "template_type": self.template_type
        }
        
        if file_path and os.path.exists(file_path):
            self._load_template()
    
    def _load_template(self):
        """
        Load the template based on its type
        """
        if self.template_type == 'docx':
            self._load_docx_template()
        elif self.template_type == 'json':
            self._load_json_template()
    
    def _load_docx_template(self):
        """
        Load a DOCX template and extract its fields
        """
        try:
            self.docx_template = DocxTemplate(self.file_path)
            # Extract variables from the template
            # This is a simplified approach - in a real system, you might need
            # to parse the XML of the DOCX to find all variables
            self.fields = self._extract_docx_fields()
        except Exception as e:
            print(f"Error loading DOCX template: {str(e)}")
            self.docx_template = None
    
    def _extract_docx_fields(self):
        """
        Attempt to extract fields from a DOCX template
        
        Returns:
            list: List of field names
        """
        # This is a simplified implementation
        # In a real system, you would parse the DOCX XML to find all Jinja2 variables
        # For now, we'll return a default set of fields for real estate documents
        return [
            "property_address",
            "property_description",
            "transaction_date",
            "transaction_amount",
            "buyer_name",
            "seller_name",
            "lender_name",
            "loan_amount",
            "interest_rate",
            "term_years",
            "monthly_payment",
            "closing_date"
        ]
    
    def _load_json_template(self):
        """
        Load a JSON template
        """
        try:
            with open(self.file_path, 'r') as f:
                template_data = json.load(f)
            
            self.json_template = template_data
            self.fields = template_data.get('fields', [])
            self.template_structure = template_data.get('structure', {})
            self.document_type = template_data.get('document_type', 'generic')
            
            # Update metadata
            self.metadata.update({
                "document_type": self.document_type,
                "field_count": len(self.fields)
            })
            
        except Exception as e:
            print(f"Error loading JSON template: {str(e)}")
            self.json_template = None
    
    def get_fields(self):
        """
        Get the list of fields in the template
        
        Returns:
            list: List of field names
        """
        return self.fields
    
    def get_field_schema(self):
        """
        Get the schema of fields with their expected types
        
        Returns:
            dict: Dictionary mapping field names to their expected types/formats
        """
        if self.template_type == 'json' and hasattr(self, 'json_template'):
            return self.json_template.get('field_schema', {})
        return {}
    
    def create_document(self, data, output_path):
        """
        Create a document from the template using the provided data
        
        Args:
            data (dict): The data to fill into the template
            output_path (str): The path to save the output document
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.template_type == 'docx' and hasattr(self, 'docx_template'):
                self.docx_template.render(data)
                self.docx_template.save(output_path)
                return True
            elif self.template_type == 'json' and hasattr(self, 'json_template'):
                # For JSON templates, we would implement custom document generation logic
                # This would depend on the specific format of your JSON template
                print("JSON template rendering not fully implemented")
                return False
        except Exception as e:
            print(f"Error creating document from template: {str(e)}")
            return False
            
        return False
    
    def to_dict(self):
        """
        Convert the template to a dictionary
        
        Returns:
            dict: Dictionary representation of the template
        """
        return {
            "metadata": self.metadata,
            "fields": self.fields
        }
        
    def to_json(self):
        """
        Convert the template to a JSON string
        
        Returns:
            str: JSON string representation of the template
        """
        return json.dumps(self.to_dict(), indent=4)
        
    @classmethod
    def from_json(cls, json_path):
        """
        Create a template from a JSON file
        
        Args:
            json_path (str): Path to the JSON file
            
        Returns:
            Template: A new Template instance
        """
        with open(json_path, 'r') as f:
            data = json.load(f)
            
        template = cls(data.get("metadata", {}).get("file_path"))
        template.metadata = data.get("metadata", {})
        template.fields = data.get("fields", [])
        
        return template 