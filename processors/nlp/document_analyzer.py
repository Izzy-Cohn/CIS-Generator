import re
import spacy
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
import json
import os
from datetime import datetime

# Download required NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class DocumentAnalyzer:
    """
    Class for analyzing legal documents using NLP techniques to extract structured data
    """
    
    def __init__(self, config=None):
        """
        Initialize the document analyzer
        
        Args:
            config (dict): Configuration dictionary with extraction patterns and settings
        """
        self.config = config or {}
        
        # Load spaCy model
        self.nlp = None
        self.load_spacy_model()
        
        # Load extraction patterns
        self.patterns = self.config.get('extraction_patterns', {})
        
        # Compile regex patterns
        self.compiled_patterns = self._compile_patterns()
        
        # Load entity extraction rules
        self.entity_rules = self.config.get('entity_rules', {})
        
        # Common real estate terms dictionary
        self.real_estate_terms = self._load_real_estate_terms()
        
    def load_spacy_model(self):
        """
        Load the spaCy NLP model
        """
        model_name = self.config.get('spacy_model', 'en_core_web_sm')
        try:
            self.nlp = spacy.load(model_name)
            print(f"Loaded spaCy model: {model_name}")
        except OSError:
            print(f"Downloading spaCy model: {model_name}")
            spacy.cli.download(model_name)
            self.nlp = spacy.load(model_name)
    
    def _compile_patterns(self):
        """
        Compile regex patterns for field extraction
        
        Returns:
            dict: Dictionary of compiled patterns
        """
        compiled = {}
        
        for field, pattern_info in self.patterns.items():
            try:
                if isinstance(pattern_info, str):
                    # Simple pattern string
                    compiled[field] = re.compile(pattern_info, re.IGNORECASE | re.MULTILINE)
                elif isinstance(pattern_info, dict):
                    # Pattern with options
                    pattern = pattern_info.get('pattern', '')
                    flags = 0
                    if pattern_info.get('case_insensitive', True):
                        flags |= re.IGNORECASE
                    if pattern_info.get('multiline', True):
                        flags |= re.MULTILINE
                    compiled[field] = re.compile(pattern, flags)
            except re.error as e:
                print(f"Error compiling pattern for '{field}': {str(e)}")
                
        return compiled
    
    def _load_real_estate_terms(self):
        """
        Load common real estate terms
        
        Returns:
            dict: Dictionary of real estate terms by category
        """
        # This would typically load from a file, but for this example, we'll define basic terms
        return {
            "property_types": [
                "apartment", "condo", "condominium", "house", "townhouse", "duplex", 
                "triplex", "commercial property", "retail space", "office space", 
                "industrial property", "land", "lot", "plot"
            ],
            "document_types": [
                "lease", "mortgage", "deed", "title", "agreement", "contract", 
                "promissory note", "closing statement", "disclosure", "amendment",
                "addendum", "extension", "assignment", "purchase agreement", 
                "sales contract"
            ],
            "parties": [
                "buyer", "seller", "purchaser", "vendor", "lessor", "lessee", 
                "landlord", "tenant", "mortgagor", "mortgagee", "borrower", "lender",
                "grantor", "grantee", "assignor", "assignee", "trustor", "trustee"
            ]
        }
    
    def analyze(self, document):
        """
        Analyze a document and extract structured data
        
        Args:
            document: Document object containing text content
            
        Returns:
            dict: Extracted data
        """
        if not document.content:
            return {}
            
        # Extract data using various methods
        extracted_data = {}
        
        # Basic document classification
        doc_type = self._classify_document(document.content)
        document.set_document_type(doc_type)
        extracted_data['document_type'] = doc_type
        
        # Extract data using regex patterns
        regex_data = self._extract_with_regex(document.content)
        extracted_data.update(regex_data)
        
        # Extract entities using spaCy
        entity_data = self._extract_entities(document.content)
        # Merge entity data - don't overwrite regex results
        for key, value in entity_data.items():
            if key not in extracted_data or not extracted_data[key]:
                extracted_data[key] = value
        
        # Extract structured sections
        sections = self._extract_sections(document.content)
        extracted_data['sections'] = sections
        
        # Special case for parties
        parties = self._extract_parties(document.content)
        extracted_data['parties'] = parties
        
        # Extract dates
        dates = self._extract_dates(document.content)
        extracted_data['dates'] = dates
        
        # Extract monetary amounts
        monetary = self._extract_monetary_amounts(document.content)
        extracted_data['monetary_values'] = monetary
        
        # Extract property information
        property_info = self._extract_property_info(document.content)
        extracted_data['property'] = property_info
        
        # Update the document with extracted data
        document.update_extracted_data(extracted_data)
        
        return extracted_data
    
    def _classify_document(self, text):
        """
        Classify the document type
        
        Args:
            text (str): Document text content
            
        Returns:
            str: Document type
        """
        # Simple keyword-based classification
        text_lower = text.lower()
        
        doc_types = {
            "lease_agreement": ["lease agreement", "rental agreement", "tenancy agreement"],
            "mortgage": ["mortgage", "deed of trust", "security deed"],
            "purchase_agreement": ["purchase agreement", "sales contract", "contract of sale", "real estate contract"],
            "deed": ["warranty deed", "quitclaim deed", "special warranty deed", "grant deed"],
            "promissory_note": ["promissory note", "loan note"],
            "disclosure": ["disclosure statement", "property disclosure"],
            "title_insurance": ["title insurance", "title policy"],
            "closing_statement": ["closing statement", "settlement statement", "hud-1"]
        }
        
        # Count matches for each document type
        matches = {}
        for doc_type, keywords in doc_types.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            matches[doc_type] = count
        
        # Get the type with the most matches
        if matches:
            max_count = max(matches.values())
            if max_count > 0:
                # Get all types with the max count
                top_types = [t for t, c in matches.items() if c == max_count]
                return top_types[0]  # Return the first matching type
        
        return "unknown"
    
    def _extract_with_regex(self, text):
        """
        Extract data using regex patterns
        
        Args:
            text (str): Document text content
            
        Returns:
            dict: Extracted data
        """
        extracted = {}
        
        for field, pattern in self.compiled_patterns.items():
            try:
                match = pattern.search(text)
                if match:
                    # Get value from first group or full match
                    if match.groups():
                        extracted[field] = match.group(1).strip()
                    else:
                        extracted[field] = match.group(0).strip()
            except Exception as e:
                print(f"Error extracting '{field}' with regex: {str(e)}")
        
        return extracted
    
    def _extract_entities(self, text):
        """
        Extract named entities using spaCy
        
        Args:
            text (str): Document text content
            
        Returns:
            dict: Extracted entities
        """
        if not self.nlp:
            return {}
            
        entities = {
            "people": [],
            "organizations": [],
            "locations": [],
            "dates": []
        }
        
        # Process text in chunks to avoid memory issues with large documents
        chunk_size = 5000  # characters
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        for chunk in chunks:
            try:
                doc = self.nlp(chunk)
                
                for ent in doc.ents:
                    if ent.label_ == "PERSON":
                        if ent.text not in entities["people"]:
                            entities["people"].append(ent.text)
                    elif ent.label_ == "ORG":
                        if ent.text not in entities["organizations"]:
                            entities["organizations"].append(ent.text)
                    elif ent.label_ in ["GPE", "LOC"]:
                        if ent.text not in entities["locations"]:
                            entities["locations"].append(ent.text)
                    elif ent.label_ == "DATE":
                        if ent.text not in entities["dates"]:
                            entities["dates"].append(ent.text)
            except Exception as e:
                print(f"Error processing chunk with spaCy: {str(e)}")
        
        return entities
    
    def _extract_sections(self, text):
        """
        Extract document sections
        
        Args:
            text (str): Document text content
            
        Returns:
            dict: Extracted sections
        """
        sections = {}
        
        # Split by page markers first
        pages = re.split(r'---\s*Page\s+\d+\s*---', text)
        
        # Common section headers in legal documents
        section_patterns = [
            (r'(?i)(?:\n|\r|\A)\s*(?:[IVX0-9]+\.)?\s*(?:RECITALS|WITNESSETH)[\s:]*', "recitals"),
            (r'(?i)(?:\n|\r|\A)\s*(?:[IVX0-9]+\.)?\s*(?:DEFINITIONS|DEFINED TERMS)[\s:]*', "definitions"),
            (r'(?i)(?:\n|\r|\A)\s*(?:[IVX0-9]+\.)?\s*(?:PROPERTY DESCRIPTION|LEGAL DESCRIPTION)[\s:]*', "property_description"),
            (r'(?i)(?:\n|\r|\A)\s*(?:[IVX0-9]+\.)?\s*(?:PURCHASE PRICE|CONSIDERATION|PAYMENT)[\s:]*', "payment_terms"),
            (r'(?i)(?:\n|\r|\A)\s*(?:[IVX0-9]+\.)?\s*(?:REPRESENTATIONS|WARRANTIES)[\s:]*', "representations"),
            (r'(?i)(?:\n|\r|\A)\s*(?:[IVX0-9]+\.)?\s*(?:COVENANTS)[\s:]*', "covenants"),
            (r'(?i)(?:\n|\r|\A)\s*(?:[IVX0-9]+\.)?\s*(?:CONDITIONS PRECEDENT|CONDITIONS)[\s:]*', "conditions"),
            (r'(?i)(?:\n|\r|\A)\s*(?:[IVX0-9]+\.)?\s*(?:TERM|DURATION)[\s:]*', "term"),
            (r'(?i)(?:\n|\r|\A)\s*(?:[IVX0-9]+\.)?\s*(?:TERMINATION)[\s:]*', "termination"),
            (r'(?i)(?:\n|\r|\A)\s*(?:[IVX0-9]+\.)?\s*(?:DEFAULT|BREACH)[\s:]*', "default"),
            (r'(?i)(?:\n|\r|\A)\s*(?:[IVX0-9]+\.)?\s*(?:REMEDIES)[\s:]*', "remedies"),
            (r'(?i)(?:\n|\r|\A)\s*(?:[IVX0-9]+\.)?\s*(?:GOVERNING LAW|APPLICABLE LAW)[\s:]*', "governing_law"),
            (r'(?i)(?:\n|\r|\A)\s*(?:[IVX0-9]+\.)?\s*(?:NOTICES)[\s:]*', "notices"),
            (r'(?i)(?:\n|\r|\A)\s*(?:[IVX0-9]+\.)?\s*(?:MISCELLANEOUS|GENERAL PROVISIONS)[\s:]*', "miscellaneous")
        ]
        
        # Extract sections from each page
        for page in pages:
            if not page.strip():
                continue
                
            for pattern, section_name in section_patterns:
                section_matches = re.split(pattern, page)
                if len(section_matches) > 1:
                    # The section content is after the section header
                    section_content = section_matches[1].strip()
                    
                    # Find the end of the section (next section)
                    for p, _ in section_patterns:
                        end_match = re.search(p, section_content)
                        if end_match:
                            section_content = section_content[:end_match.start()].strip()
                    
                    # Add or append to existing section
                    if section_name in sections:
                        sections[section_name] += "\n\n" + section_content
                    else:
                        sections[section_name] = section_content
        
        return sections
    
    def _extract_parties(self, text):
        """
        Extract parties involved in the agreement
        
        Args:
            text (str): Document text content
            
        Returns:
            dict: Extracted parties
        """
        parties = {
            "buyer": None,
            "seller": None,
            "lender": None,
            "borrower": None,
            "lessor": None,
            "lessee": None,
            "landlord": None,
            "tenant": None
        }
        
        # Common party patterns
        party_patterns = {
            "buyer": [
                r"(?i)buyer:?\s*([^,\n\r\.]{3,50})",
                r"(?i)purchaser:?\s*([^,\n\r\.]{3,50})",
                r"(?i)HEREINAFTER\s+(?:called|referred to as)[^,\n\r]*\"?(?:buyer|purchaser)\"?[^,\n\r]*,\s*([^,\n\r\.]{3,50})"
            ],
            "seller": [
                r"(?i)seller:?\s*([^,\n\r\.]{3,50})",
                r"(?i)vendor:?\s*([^,\n\r\.]{3,50})",
                r"(?i)HEREINAFTER\s+(?:called|referred to as)[^,\n\r]*\"?(?:seller|vendor)\"?[^,\n\r]*,\s*([^,\n\r\.]{3,50})"
            ],
            "lender": [
                r"(?i)lender:?\s*([^,\n\r\.]{3,50})",
                r"(?i)mortgagee:?\s*([^,\n\r\.]{3,50})",
                r"(?i)HEREINAFTER\s+(?:called|referred to as)[^,\n\r]*\"?(?:lender|mortgagee)\"?[^,\n\r]*,\s*([^,\n\r\.]{3,50})"
            ],
            "borrower": [
                r"(?i)borrower:?\s*([^,\n\r\.]{3,50})",
                r"(?i)mortgagor:?\s*([^,\n\r\.]{3,50})",
                r"(?i)HEREINAFTER\s+(?:called|referred to as)[^,\n\r]*\"?(?:borrower|mortgagor)\"?[^,\n\r]*,\s*([^,\n\r\.]{3,50})"
            ],
            "lessor": [
                r"(?i)lessor:?\s*([^,\n\r\.]{3,50})",
                r"(?i)landlord:?\s*([^,\n\r\.]{3,50})",
                r"(?i)HEREINAFTER\s+(?:called|referred to as)[^,\n\r]*\"?(?:lessor|landlord)\"?[^,\n\r]*,\s*([^,\n\r\.]{3,50})"
            ],
            "lessee": [
                r"(?i)lessee:?\s*([^,\n\r\.]{3,50})",
                r"(?i)tenant:?\s*([^,\n\r\.]{3,50})",
                r"(?i)HEREINAFTER\s+(?:called|referred to as)[^,\n\r]*\"?(?:lessee|tenant)\"?[^,\n\r]*,\s*([^,\n\r\.]{3,50})"
            ]
        }
        
        # Extract parties
        for party, patterns in party_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text)
                if match and not parties[party]:
                    parties[party] = match.group(1).strip()
        
        # Map redundant fields
        if parties["lessor"] and not parties["landlord"]:
            parties["landlord"] = parties["lessor"]
        elif parties["landlord"] and not parties["lessor"]:
            parties["lessor"] = parties["landlord"]
            
        if parties["lessee"] and not parties["tenant"]:
            parties["tenant"] = parties["lessee"]
        elif parties["tenant"] and not parties["lessee"]:
            parties["lessee"] = parties["tenant"]
        
        return parties
    
    def _extract_dates(self, text):
        """
        Extract important dates from the document
        
        Args:
            text (str): Document text content
            
        Returns:
            dict: Extracted dates
        """
        dates = {
            "agreement_date": None,
            "effective_date": None,
            "closing_date": None,
            "execution_date": None,
            "other_dates": []
        }
        
        # Date patterns
        date_patterns = {
            "agreement_date": [
                r"(?i)(?:THIS\s+AGREEMENT|THIS\s+CONTRACT)[^.]*?dated\s+(?:as of\s+)?([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4})",
                r"(?i)(?:THIS\s+AGREEMENT|THIS\s+CONTRACT)[^.]*?dated\s+(?:as of\s+)?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"(?i)DATED:?\s*([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4})",
                r"(?i)DATED:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"(?i)dated\s+(?:as of\s+)?(?:the\s+)?(\d{1,2}(?:st|nd|rd|th)?\s+day\s+of\s+[A-Za-z]+,?\s+\d{4})"
            ],
            "effective_date": [
                r"(?i)effective\s+(?:date|as of)(?:\s+the)?\s+(?:date\s+of\s+)?([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4})",
                r"(?i)effective\s+(?:date|as of)(?:\s+the)?\s+(?:date\s+of\s+)?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"(?i)effective\s+(?:date|as of)(?:\s+the)?\s+(?:date\s+of\s+)?(?:the\s+)?(\d{1,2}(?:st|nd|rd|th)?\s+day\s+of\s+[A-Za-z]+,?\s+\d{4})"
            ],
            "closing_date": [
                r"(?i)closing\s+date:?\s*([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4})",
                r"(?i)closing\s+date:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"(?i)date\s+of\s+closing:?\s*([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4})",
                r"(?i)date\s+of\s+closing:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
            ],
            "execution_date": [
                r"(?i)executed\s+(?:on|as of)(?:\s+the)?\s+(?:date\s+of\s+)?([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4})",
                r"(?i)executed\s+(?:on|as of)(?:\s+the)?\s+(?:date\s+of\s+)?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"(?i)executed\s+(?:on|as of)(?:\s+the)?\s+(?:date\s+of\s+)?(?:the\s+)?(\d{1,2}(?:st|nd|rd|th)?\s+day\s+of\s+[A-Za-z]+,?\s+\d{4})"
            ]
        }
        
        # Extract specific dates
        for date_type, patterns in date_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text)
                if match and not dates[date_type]:
                    dates[date_type] = match.group(1).strip()
        
        # Extract all dates using spaCy
        if self.nlp:
            try:
                # Process in chunks
                chunk_size = 5000
                chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
                
                all_dates = []
                for chunk in chunks:
                    doc = self.nlp(chunk)
                    for ent in doc.ents:
                        if ent.label_ == "DATE":
                            date_text = ent.text.strip()
                            # Filter out common non-specific dates
                            if not re.match(r"(?i)(today|now|current|present|annually|monthly|yearly|daily)", date_text):
                                all_dates.append(date_text)
                
                # Add unique dates not already captured
                dates["other_dates"] = list(set([d for d in all_dates if d not in dates.values()]))
            except Exception as e:
                print(f"Error extracting dates with spaCy: {str(e)}")
        
        return dates
    
    def _extract_monetary_amounts(self, text):
        """
        Extract monetary amounts from the document
        
        Args:
            text (str): Document text content
            
        Returns:
            dict: Extracted monetary amounts
        """
        monetary = {
            "purchase_price": None,
            "loan_amount": None,
            "deposit_amount": None,
            "monthly_payment": None,
            "interest_rate": None,
            "other_amounts": []
        }
        
        # Money patterns
        money_patterns = {
            "purchase_price": [
                r"(?i)purchase\s+price:?\s*\$?([0-9,]+\.[0-9]{2})",
                r"(?i)purchase\s+price:?\s*\$?([0-9,]+)",
                r"(?i)total\s+consideration:?\s*\$?([0-9,]+\.[0-9]{2})",
                r"(?i)total\s+consideration:?\s*\$?([0-9,]+)",
                r"(?i)sales\s+price:?\s*\$?([0-9,]+\.[0-9]{2})",
                r"(?i)sales\s+price:?\s*\$?([0-9,]+)"
            ],
            "loan_amount": [
                r"(?i)loan\s+amount:?\s*\$?([0-9,]+\.[0-9]{2})",
                r"(?i)loan\s+amount:?\s*\$?([0-9,]+)",
                r"(?i)principal\s+(?:sum|amount):?\s*\$?([0-9,]+\.[0-9]{2})",
                r"(?i)principal\s+(?:sum|amount):?\s*\$?([0-9,]+)",
                r"(?i)mortgage\s+amount:?\s*\$?([0-9,]+\.[0-9]{2})",
                r"(?i)mortgage\s+amount:?\s*\$?([0-9,]+)"
            ],
            "deposit_amount": [
                r"(?i)deposit:?\s*\$?([0-9,]+\.[0-9]{2})",
                r"(?i)deposit:?\s*\$?([0-9,]+)",
                r"(?i)earnest\s+money:?\s*\$?([0-9,]+\.[0-9]{2})",
                r"(?i)earnest\s+money:?\s*\$?([0-9,]+)"
            ],
            "monthly_payment": [
                r"(?i)monthly\s+payment:?\s*\$?([0-9,]+\.[0-9]{2})",
                r"(?i)monthly\s+payment:?\s*\$?([0-9,]+)",
                r"(?i)monthly\s+rent:?\s*\$?([0-9,]+\.[0-9]{2})",
                r"(?i)monthly\s+rent:?\s*\$?([0-9,]+)"
            ],
            "interest_rate": [
                r"(?i)interest\s+rate:?\s*([0-9\.]+)%",
                r"(?i)interest\s+rate:?\s*([0-9\.]+)\s+percent",
                r"(?i)at\s+(?:the\s+)?(?:annual\s+)?(?:rate\s+)?(?:of\s+)?([0-9\.]+)%\s+(?:interest|per\s+annum)",
                r"(?i)at\s+(?:the\s+)?(?:annual\s+)?(?:rate\s+)?(?:of\s+)?([0-9\.]+)\s+percent\s+(?:interest|per\s+annum)"
            ]
        }
        
        # Extract specific monetary amounts
        for money_type, patterns in money_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text)
                if match and not monetary[money_type]:
                    value = match.group(1).strip()
                    # Remove commas from numbers
                    value = value.replace(',', '')
                    if money_type != "interest_rate":
                        # Format as currency
                        monetary[money_type] = f"${value}"
                    else:
                        # Format as percentage
                        monetary[money_type] = f"{value}%"
        
        # Extract all monetary amounts using regex
        all_money_pattern = r'\$([0-9,]+(?:\.[0-9]{2})?)'
        all_money_matches = re.findall(all_money_pattern, text)
        
        # Remove commas and convert to float for sorting
        all_money = []
        for m in all_money_matches:
            try:
                amount = float(m.replace(',', ''))
                formatted = f"${m}"
                # Only add if not already in specific categories
                if formatted not in monetary.values():
                    all_money.append((amount, formatted))
            except ValueError:
                pass
                
        # Sort by amount (descending) and take top 5
        all_money.sort(reverse=True)
        monetary["other_amounts"] = [m[1] for m in all_money[:5]]
        
        return monetary
    
    def _extract_property_info(self, text):
        """
        Extract property information from the document
        
        Args:
            text (str): Document text content
            
        Returns:
            dict: Extracted property information
        """
        property_info = {
            "address": None,
            "legal_description": None,
            "property_type": None,
            "parcel_number": None,
            "square_footage": None
        }
        
        # Property patterns
        property_patterns = {
            "address": [
                r"(?i)property\s+address:?\s*([^,\n\r\.]{3,100}(?:,\s*[^,\n\r\.]{3,50}){1,3})",
                r"(?i)real\s+property\s+located\s+at:?\s*([^,\n\r\.]{3,100}(?:,\s*[^,\n\r\.]{3,50}){1,3})",
                r"(?i)premises\s+located\s+at:?\s*([^,\n\r\.]{3,100}(?:,\s*[^,\n\r\.]{3,50}){1,3})",
                r"(?i)property\s+commonly\s+known\s+as:?\s*([^,\n\r\.]{3,100}(?:,\s*[^,\n\r\.]{3,50}){1,3})"
            ],
            "legal_description": [
                r"(?i)legal\s+description:?\s*\n*((?:[^\n\r]{3,200}\n*){1,10})"
            ],
            "property_type": [
                r"(?i)property\s+type:?\s*([^,\n\r\.]{3,50})",
                r"(?i)type\s+of\s+property:?\s*([^,\n\r\.]{3,50})"
            ],
            "parcel_number": [
                r"(?i)(?:parcel|tax|assessor(?:'s)?)\s+(?:id|identification|number):?\s*([^,\n\r\.]{3,50})",
                r"(?i)APN:?\s*([^,\n\r\.]{3,50})"
            ],
            "square_footage": [
                r"(?i)(?:square\s+feet|sq\.\s*ft\.|sf):?\s*([0-9,]+)",
                r"(?i)(?:approximately|approx\.)\s+([0-9,]+)\s+(?:square\s+feet|sq\.\s*ft\.|sf)"
            ]
        }
        
        # Extract property information
        for prop_type, patterns in property_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text)
                if match and not property_info[prop_type]:
                    property_info[prop_type] = match.group(1).strip()
        
        return property_info 