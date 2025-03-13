import os
import json

class ConfigLoader:
    """
    Utility class for loading and managing configuration files
    """
    
    def __init__(self, config_path=None):
        """
        Initialize the config loader
        
        Args:
            config_path (str, optional): Path to the configuration file
        """
        self.config_path = config_path
        self.config = {}
        
        if config_path and os.path.exists(config_path):
            self.load_config()
        else:
            # Load default configuration
            self.load_default_config()
    
    def load_config(self):
        """
        Load configuration from file
        
        Returns:
            dict: The loaded configuration
        """
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            print(f"Loaded configuration from {self.config_path}")
        except Exception as e:
            print(f"Error loading configuration: {str(e)}")
            # Load default configuration as fallback
            self.load_default_config()
            
        return self.config
    
    def load_default_config(self):
        """
        Load default configuration
        
        Returns:
            dict: The default configuration
        """
        self.config = {
            "extraction_patterns": {
                "property_address": {
                    "pattern": r"(?i)property\s+address:?\s*([^,\n\r\.]{3,100}(?:,\s*[^,\n\r\.]{3,50}){1,3})",
                    "case_insensitive": True,
                    "multiline": True
                },
                "purchase_price": {
                    "pattern": r"(?i)purchase\s+price:?\s*\$?([0-9,]+(?:\.[0-9]{2})?)",
                    "case_insensitive": True,
                    "multiline": True
                },
                "closing_date": {
                    "pattern": r"(?i)closing\s+date:?\s*([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}|(?:\d{1,2}[/-]){2}\d{2,4})",
                    "case_insensitive": True,
                    "multiline": True
                }
            },
            "entity_rules": {
                "people": ["PERSON"],
                "organizations": ["ORG"],
                "locations": ["GPE", "LOC"],
                "dates": ["DATE"]
            },
            "spacy_model": "en_core_web_sm",
            "field_formats": {
                "purchase_price": {
                    "type": "currency",
                    "symbol": "$"
                },
                "loan_amount": {
                    "type": "currency",
                    "symbol": "$"
                },
                "closing_date": {
                    "type": "date",
                    "format": "%B %d, %Y"
                },
                "interest_rate": {
                    "type": "percentage",
                    "decimal_places": 3
                }
            },
            "default_values": {
                "property_address": "N/A",
                "purchase_price": "$0.00",
                "closing_date": "",
                "buyer_name": "N/A",
                "seller_name": "N/A"
            }
        }
        
        print("Loaded default configuration")
        return self.config
    
    def get_config(self):
        """
        Get the full configuration
        
        Returns:
            dict: The configuration dictionary
        """
        return self.config
    
    def get_extraction_patterns(self):
        """
        Get extraction patterns
        
        Returns:
            dict: Extraction patterns
        """
        return self.config.get('extraction_patterns', {})
    
    def get_entity_rules(self):
        """
        Get entity extraction rules
        
        Returns:
            dict: Entity rules
        """
        return self.config.get('entity_rules', {})
    
    def get_nlp_config(self):
        """
        Get NLP configuration
        
        Returns:
            dict: NLP configuration
        """
        return {
            'spacy_model': self.config.get('spacy_model', 'en_core_web_sm'),
            'extraction_patterns': self.get_extraction_patterns(),
            'entity_rules': self.get_entity_rules()
        }
    
    def get_field_formats(self):
        """
        Get field format configurations
        
        Returns:
            dict: Field formats
        """
        return self.config.get('field_formats', {})
    
    def get_default_values(self):
        """
        Get default values for fields
        
        Returns:
            dict: Default values
        """
        return self.config.get('default_values', {})
    
    def save_config(self, config_path=None):
        """
        Save the current configuration to file
        
        Args:
            config_path (str, optional): Path to save the configuration file
        
        Returns:
            bool: True if successful, False otherwise
        """
        save_path = config_path or self.config_path
        
        if not save_path:
            print("No configuration path specified")
            return False
            
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
            
            with open(save_path, 'w') as f:
                json.dump(self.config, f, indent=4)
                
            print(f"Configuration saved to {save_path}")
            return True
            
        except Exception as e:
            print(f"Error saving configuration: {str(e)}")
            return False
    
    def update_config(self, new_config):
        """
        Update the configuration with new values
        
        Args:
            new_config (dict): New configuration values
            
        Returns:
            dict: The updated configuration
        """
        self.config.update(new_config)
        return self.config 