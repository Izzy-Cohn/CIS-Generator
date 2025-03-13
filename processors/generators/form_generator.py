import os
import json
from docxtpl import DocxTemplate
import pandas as pd
import openpyxl
from datetime import datetime

class FormGenerator:
    """
    Class for generating documents from templates using extracted data
    """
    
    def __init__(self, config=None):
        """
        Initialize the form generator
        
        Args:
            config (dict): Configuration for the form generator
        """
        self.config = config or {}
    
    def generate(self, data, template, output_path):
        """
        Generate a document from a template using extracted data
        
        Args:
            data (dict): Extracted data
            template: Template object
            output_path (str): Path to save the generated document
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Determine template type and call appropriate method
        if template.template_type == 'docx':
            return self._generate_docx(data, template, output_path)
        elif template.template_type == 'json':
            return self._generate_from_json_template(data, template, output_path)
        else:
            print(f"Unsupported template type: {template.template_type}")
            return False
    
    def _generate_docx(self, data, template, output_path):
        """
        Generate a document from a DOCX template
        
        Args:
            data (dict): Extracted data
            template: Template object
            output_path (str): Path to save the generated document
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Flatten the nested data structure
            flat_data = self._flatten_data(data)
            
            # Get template fields
            template_fields = template.get_fields()
            
            # Check if we need to format any fields
            field_formats = self.config.get('field_formats', {})
            for field, format_info in field_formats.items():
                if field in flat_data and flat_data[field]:
                    flat_data[field] = self._format_field(flat_data[field], format_info)
            
            # Create a clean context with only fields that exist in the template
            context = {}
            
            # First add all template fields that we have data for
            for field in template_fields:
                if field in flat_data:
                    context[field] = flat_data[field]
                else:
                    # Handle missing fields
                    context[field] = self._get_default_value(field)
            
            # Add metadata fields
            context['generation_date'] = datetime.now().strftime('%Y-%m-%d')
            context['generation_time'] = datetime.now().strftime('%H:%M:%S')
            
            # Load and render the template
            docx_template = DocxTemplate(template.file_path)
            docx_template.render(context)
            docx_template.save(output_path)
            
            return True
            
        except Exception as e:
            print(f"Error generating document: {str(e)}")
            return False
    
    def _generate_from_json_template(self, data, template, output_path):
        """
        Generate a document from a JSON template
        
        Args:
            data (dict): Extracted data
            template: Template object
            output_path (str): Path to save the generated document
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Since JSON templates can define any format, we'd implement custom logic
            # based on the template structure. This is a simplified example.
            if not hasattr(template, 'json_template'):
                print("Invalid JSON template")
                return False
                
            # Determine output format from the output path
            output_format = os.path.splitext(output_path)[1].lower().replace('.', '')
            
            if output_format == 'json':
                # Simply save the extracted data as JSON
                with open(output_path, 'w') as f:
                    json.dump(data, f, indent=4)
                return True
                
            elif output_format == 'docx':
                # For JSON templates that define a DOCX output,
                # we would generate a DOCX file based on the template structure
                print("JSON to DOCX generation not fully implemented")
                return False
                
            elif output_format in ['xlsx', 'xls']:
                # Generate Excel file
                return self._generate_excel(data, template, output_path)
                
            else:
                print(f"Unsupported output format: {output_format}")
                return False
                
        except Exception as e:
            print(f"Error generating document from JSON template: {str(e)}")
            return False
    
    def _generate_excel(self, data, template, output_path):
        """
        Generate an Excel file from extracted data
        
        Args:
            data (dict): Extracted data
            template: Template object
            output_path (str): Path to save the generated Excel file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Flatten the nested data structure for easier Excel generation
            flat_data = self._flatten_data(data)
            
            # Convert to DataFrame
            df = pd.DataFrame([flat_data])
            
            # Save to Excel
            df.to_excel(output_path, index=False)
            
            return True
            
        except Exception as e:
            print(f"Error generating Excel file: {str(e)}")
            return False
    
    def _flatten_data(self, data, parent_key='', sep='_'):
        """
        Flatten a nested dictionary
        
        Args:
            data (dict): The nested dictionary to flatten
            parent_key (str): The parent key
            sep (str): Separator for nested keys
            
        Returns:
            dict: Flattened dictionary
        """
        items = []
        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
            if isinstance(v, dict):
                items.extend(self._flatten_data(v, new_key, sep).items())
            elif isinstance(v, list):
                # For lists, we'll create keys with indices
                if all(isinstance(x, dict) for x in v):
                    # List of dictionaries - flatten each one
                    for i, item in enumerate(v):
                        items.extend(self._flatten_data(item, f"{new_key}{sep}{i}", sep).items())
                else:
                    # Simple list - join with commas
                    items.append((new_key, ', '.join(str(x) for x in v)))
            else:
                items.append((new_key, v))
                
        return dict(items)
    
    def _format_field(self, value, format_info):
        """
        Format a field value based on format information
        
        Args:
            value: The value to format
            format_info (dict): Format information
            
        Returns:
            Formatted value
        """
        if not value:
            return value
            
        format_type = format_info.get('type', 'text')
        
        if format_type == 'date':
            try:
                # Try to parse and format the date
                # This is simplified - would need more robust date parsing
                from dateutil.parser import parse
                date_obj = parse(str(value))
                date_format = format_info.get('format', '%Y-%m-%d')
                return date_obj.strftime(date_format)
            except:
                return value
                
        elif format_type == 'currency':
            try:
                # Format as currency
                if isinstance(value, str) and value.startswith('$'):
                    value = value[1:]
                amount = float(value.replace(',', ''))
                currency_symbol = format_info.get('symbol', '$')
                return f"{currency_symbol}{amount:,.2f}"
            except:
                return value
                
        elif format_type == 'number':
            try:
                # Format as number
                if isinstance(value, str):
                    value = value.replace(',', '')
                num = float(value)
                decimal_places = format_info.get('decimal_places', 2)
                return f"{num:,.{decimal_places}f}"
            except:
                return value
                
        elif format_type == 'percentage':
            try:
                # Format as percentage
                if isinstance(value, str) and value.endswith('%'):
                    value = value[:-1]
                pct = float(value)
                decimal_places = format_info.get('decimal_places', 2)
                return f"{pct:.{decimal_places}f}%"
            except:
                return value
                
        elif format_type == 'phone':
            # Format as phone number (US format)
            try:
                # Remove non-numeric characters
                phone = ''.join(c for c in str(value) if c.isdigit())
                if len(phone) == 10:
                    return f"({phone[0:3]}) {phone[3:6]}-{phone[6:]}"
                return value
            except:
                return value
                
        elif format_type == 'boolean':
            # Format as Yes/No
            try:
                if isinstance(value, bool):
                    return "Yes" if value else "No"
                elif isinstance(value, str):
                    return "Yes" if value.lower() in ['true', 'yes', 'y', '1'] else "No"
                return "Yes" if value else "No"
            except:
                return value
                
        # Default - return as is
        return value
    
    def _get_default_value(self, field):
        """
        Get a default value for a field
        
        Args:
            field (str): Field name
            
        Returns:
            Default value for the field
        """
        # Check if we have a default value configuration
        defaults = self.config.get('default_values', {})
        if field in defaults:
            return defaults[field]
            
        # Common default values for field types
        if 'date' in field.lower():
            return ""
        elif 'amount' in field.lower() or 'price' in field.lower() or 'payment' in field.lower():
            return "$0.00"
        elif 'rate' in field.lower() or 'percentage' in field.lower():
            return "0%"
            
        # Default empty string
        return "" 