import os
import re
import PyPDF2
import pdfplumber
from tqdm import tqdm

class PDFExtractor:
    """
    Class for extracting text and data from PDF documents
    """
    
    def __init__(self, ocr_enabled=False):
        """
        Initialize the PDF Extractor
        
        Args:
            ocr_enabled (bool): Whether to use OCR for text extraction
        """
        self.ocr_enabled = ocr_enabled
    
    def extract_text(self, pdf_path, pages=None):
        """
        Extract all text from a PDF file
        
        Args:
            pdf_path (str): Path to the PDF file
            pages (list, optional): List of page numbers to extract (0-indexed)
            
        Returns:
            str: The extracted text
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        # Try extraction with pdfplumber first (better formatting)
        try:
            return self._extract_with_pdfplumber(pdf_path, pages)
        except Exception as e:
            print(f"pdfplumber extraction failed: {str(e)}")
            print("Falling back to PyPDF2...")
            
            # Fallback to PyPDF2
            try:
                return self._extract_with_pypdf2(pdf_path, pages)
            except Exception as e:
                print(f"PyPDF2 extraction failed: {str(e)}")
                return ""
    
    def _extract_with_pdfplumber(self, pdf_path, pages=None):
        """
        Extract text using pdfplumber
        
        Args:
            pdf_path (str): Path to the PDF file
            pages (list, optional): List of page numbers to extract
            
        Returns:
            str: The extracted text
        """
        text = []
        
        with pdfplumber.open(pdf_path) as pdf:
            # If pages is None, extract all pages
            if pages is None:
                pages = range(len(pdf.pages))
                
            # Convert page numbers to 0-indexed if needed
            pages = [p if p < len(pdf.pages) else p % len(pdf.pages) for p in pages]
            
            # Extract text from each page
            for i in tqdm(pages, desc="Extracting text"):
                try:
                    page = pdf.pages[i]
                    page_text = page.extract_text() or ""
                    text.append(f"--- Page {i+1} ---\n{page_text}")
                except Exception as e:
                    print(f"Error extracting text from page {i+1}: {str(e)}")
                    text.append(f"--- Page {i+1} ---\n[Error: Could not extract text]")
        
        return "\n\n".join(text)
    
    def _extract_with_pypdf2(self, pdf_path, pages=None):
        """
        Extract text using PyPDF2
        
        Args:
            pdf_path (str): Path to the PDF file
            pages (list, optional): List of page numbers to extract
            
        Returns:
            str: The extracted text
        """
        text = []
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            
            # If pages is None, extract all pages
            if pages is None:
                pages = range(total_pages)
                
            # Convert page numbers to 0-indexed if needed
            pages = [p if p < total_pages else p % total_pages for p in pages]
            
            # Extract text from each page
            for i in tqdm(pages, desc="Extracting text"):
                try:
                    page = pdf_reader.pages[i]
                    page_text = page.extract_text() or ""
                    text.append(f"--- Page {i+1} ---\n{page_text}")
                except Exception as e:
                    print(f"Error extracting text from page {i+1}: {str(e)}")
                    text.append(f"--- Page {i+1} ---\n[Error: Could not extract text]")
        
        return "\n\n".join(text)
    
    def extract_tables(self, pdf_path, pages=None):
        """
        Extract tables from PDF
        
        Args:
            pdf_path (str): Path to the PDF file
            pages (list, optional): List of page numbers to extract tables from
            
        Returns:
            dict: Dictionary mapping page numbers to lists of tables
        """
        tables_by_page = {}
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # If pages is None, extract all pages
                if pages is None:
                    pages = range(len(pdf.pages))
                    
                # Convert page numbers to 0-indexed if needed
                pages = [p if p < len(pdf.pages) else p % len(pdf.pages) for p in pages]
                
                # Extract tables from each page
                for i in tqdm(pages, desc="Extracting tables"):
                    try:
                        page = pdf.pages[i]
                        tables = page.extract_tables()
                        if tables:
                            tables_by_page[i+1] = tables
                    except Exception as e:
                        print(f"Error extracting tables from page {i+1}: {str(e)}")
        except Exception as e:
            print(f"Error extracting tables: {str(e)}")
            
        return tables_by_page
    
    def extract_form_fields(self, pdf_path):
        """
        Extract form fields from a PDF
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            dict: Dictionary of form fields and their values
        """
        form_fields = {}
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                if pdf_reader.is_encrypted:
                    try:
                        pdf_reader.decrypt('')  # Try empty password
                    except:
                        print("PDF is encrypted and could not be decrypted")
                        return form_fields
                
                if '/AcroForm' in pdf_reader.trailer['/Root']:
                    # Get form fields
                    try:
                        fields = pdf_reader.get_fields()
                        
                        if fields:
                            for field_name, field_value in fields.items():
                                # Handle different field types
                                if hasattr(field_value, 'value'):
                                    form_fields[field_name] = field_value.value
                                elif isinstance(field_value, dict) and '/V' in field_value:
                                    form_fields[field_name] = field_value['/V']
                                else:
                                    form_fields[field_name] = None
                    except Exception as e:
                        print(f"Error extracting form fields: {str(e)}")
                        
        except Exception as e:
            print(f"Error processing PDF for form fields: {str(e)}")
            
        return form_fields
    
    def extract_metadata(self, pdf_path):
        """
        Extract metadata from a PDF
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            dict: Dictionary of metadata
        """
        metadata = {}
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                if pdf_reader.metadata:
                    # Map common metadata fields
                    metadata_map = {
                        '/Title': 'title',
                        '/Author': 'author',
                        '/Subject': 'subject',
                        '/Keywords': 'keywords',
                        '/Creator': 'creator',
                        '/Producer': 'producer',
                        '/CreationDate': 'creation_date',
                        '/ModDate': 'modification_date'
                    }
                    
                    # Extract metadata
                    for key, mapped_key in metadata_map.items():
                        if key in pdf_reader.metadata:
                            value = pdf_reader.metadata[key]
                            # Clean up date strings
                            if key in ['/CreationDate', '/ModDate'] and value:
                                value = str(value).replace('D:', '').replace("'", '')
                            metadata[mapped_key] = value
                
                # Add page count
                metadata['page_count'] = len(pdf_reader.pages)
                
        except Exception as e:
            print(f"Error extracting metadata: {str(e)}")
            
        return metadata
    
    def extract_text_by_regions(self, pdf_path, regions):
        """
        Extract text from specific regions of the PDF
        
        Args:
            pdf_path (str): Path to the PDF file
            regions (dict): Dictionary mapping page numbers to lists of region bounding boxes
                            (x0, top, x1, bottom)
        
        Returns:
            dict: Dictionary mapping region identifiers to extracted text
        """
        region_text = {}
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page_regions in regions.items():
                    # Adjust for 0-indexed pages
                    page_idx = page_num - 1
                    
                    if page_idx < 0 or page_idx >= len(pdf.pages):
                        continue
                        
                    page = pdf.pages[page_idx]
                    
                    for region_id, bbox in page_regions.items():
                        try:
                            # Extract the region
                            region = page.crop(bbox)
                            text = region.extract_text() or ""
                            region_text[region_id] = text
                        except Exception as e:
                            print(f"Error extracting region {region_id} from page {page_num}: {str(e)}")
                            region_text[region_id] = ""
        except Exception as e:
            print(f"Error in region extraction: {str(e)}")
            
        return region_text 