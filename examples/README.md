# CIS-Generator Examples

This directory contains example files for use with the CIS-Generator tool.

## Templates

The `templates` directory contains example template files that can be used with the CIS-Generator:

- `real_estate_template.json`: A JSON template for real estate transaction documents

### JSON Template Format

JSON templates should follow this structure:

```json
{
    "template_name": "Template Name",
    "document_type": "document_type",
    "version": "1.0",
    "fields": [
        "field1",
        "field2",
        "..."
    ],
    "field_schema": {
        "field1": {
            "type": "string|date|currency|percentage|number",
            "description": "Description of the field"
        },
        "..."
    },
    "structure": {
        "sections": [
            {
                "title": "Section Title",
                "fields": ["field1", "field2", "..."]
            },
            "..."
        ]
    },
    "mapping": {
        "template_field": "extracted_data_field",
        "..."
    }
}
```

### DOCX Template Format

DOCX templates should use the Jinja2 templating syntax with the `docxtpl` format:

- Use `{{ field_name }}` to insert a field value
- Fields should match the names in the extraction output or be mapped appropriately

## Documents

The `documents` directory is where you can place sample PDF documents for testing the CIS-Generator. 

### Supported Document Types

- Real estate purchase agreements
- Mortgage documents
- Lease agreements
- Closing statements
- Property disclosures
- Deeds and titles

## Usage

To use these examples:

1. Start the CIS-Generator application
2. Upload a PDF document from the `documents` directory
3. Select a template from the `templates` directory
4. Process the document to generate a form 