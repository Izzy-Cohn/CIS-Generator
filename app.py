import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import uuid
import json
from datetime import datetime

# Import local modules
from processors.extractors.pdf_extractor import PDFExtractor
from processors.nlp.document_analyzer import DocumentAnalyzer
from processors.generators.form_generator import FormGenerator
from utils.config_loader import ConfigLoader
from models.document import Document
from models.template import Template

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev_key_for_development')

# Configure upload folders
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
TEMP_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
RESULT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
TEMPLATE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

# Ensure directories exist
for folder in [UPLOAD_FOLDER, TEMP_FOLDER, RESULT_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# Setup file restrictions
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf'}
ALLOWED_TEMPLATE_EXTENSIONS = {'docx', 'json'}

# Initialize components
config = ConfigLoader('config/extraction_config.json')
pdf_extractor = PDFExtractor()
document_analyzer = DocumentAnalyzer(config.get_nlp_config())
form_generator = FormGenerator()

def allowed_document_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_DOCUMENT_EXTENSIONS

def allowed_template_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_TEMPLATE_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'documents' not in request.files:
        flash('No document files selected', 'error')
        return redirect(request.url)
    
    if 'template' not in request.files:
        flash('No template file selected', 'error')
        return redirect(request.url)
    
    documents = request.files.getlist('documents')
    template_file = request.files['template']
    
    # Validate template file
    if template_file.filename == '':
        flash('No template file selected', 'error')
        return redirect(request.url)
    
    if not allowed_template_file(template_file.filename):
        flash(f'Template file must be one of: {", ".join(ALLOWED_TEMPLATE_EXTENSIONS)}', 'error')
        return redirect(request.url)
    
    # Save template
    template_filename = secure_filename(template_file.filename)
    template_path = os.path.join(TEMP_FOLDER, f"{uuid.uuid4()}_{template_filename}")
    template_file.save(template_path)
    
    # Load template
    template = Template(template_path)
    
    # Process each document
    processed_docs = []
    job_id = str(uuid.uuid4())
    result_folder = os.path.join(RESULT_FOLDER, job_id)
    os.makedirs(result_folder, exist_ok=True)
    
    for document_file in documents:
        if document_file.filename == '':
            continue
            
        if not allowed_document_file(document_file.filename):
            flash(f'Document file must be PDF: {document_file.filename}', 'warning')
            continue
            
        try:
            # Save document
            doc_filename = secure_filename(document_file.filename)
            doc_path = os.path.join(TEMP_FOLDER, f"{uuid.uuid4()}_{doc_filename}")
            document_file.save(doc_path)
            
            # Process document
            document = Document(doc_path)
            
            # Extract text
            extracted_text = pdf_extractor.extract_text(doc_path)
            document.set_content(extracted_text)
            
            # Analyze with NLP
            extracted_data = document_analyzer.analyze(document)
            
            # Generate form
            output_filename = os.path.join(result_folder, f"processed_{doc_filename.rsplit('.', 1)[0]}.docx")
            form_generator.generate(extracted_data, template, output_filename)
            
            processed_docs.append({
                'filename': doc_filename,
                'result_path': output_filename,
                'extracted_data': extracted_data
            })
            
        except Exception as e:
            flash(f'Error processing {doc_filename}: {str(e)}', 'error')
    
    # Save extraction result summary
    summary_file = os.path.join(result_folder, 'extraction_summary.json')
    with open(summary_file, 'w') as f:
        json.dump({
            'job_id': job_id,
            'timestamp': datetime.now().isoformat(),
            'documents': [doc['filename'] for doc in processed_docs],
            'results': processed_docs
        }, f, indent=4)
    
    return render_template('results.html', job_id=job_id, documents=processed_docs)

@app.route('/download/<job_id>/<path:filename>')
def download_file(job_id, filename):
    result_path = os.path.join(RESULT_FOLDER, job_id, filename)
    if os.path.exists(result_path):
        return send_file(result_path, as_attachment=True)
    else:
        flash('File not found', 'error')
        return redirect(url_for('index'))

@app.route('/templates')
def template_management():
    return render_template('templates.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

if __name__ == '__main__':
    app.run(debug=True) 