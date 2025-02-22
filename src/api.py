from flask import Flask, request, jsonify, send_file, send_from_directory
from pathlib import Path
import os
import logging
from src.main import DocumentProcessor, process_and_fill_document
from src.config import Config
from src.models.letter_of_credit_parser import LetterOfCreditParser
import sys
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('../logs/api.log')
    ]
)

logger = logging.getLogger(__name__)

# Initialize the DocumentProcessor
processor = DocumentProcessor()

# Directory for uploads (defined in Config)
UPLOAD_FOLDER = Config.UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not Config.OPENAI_API_KEY:
    logger.error("❌ OPENAI API Key is missing! Ensure it's set in the .env file.")
    raise ValueError("OPENAI API Key is required for extraction.")

@app.route(f"{Config.UPLOAD_FOLDER}/<path:filename>")
def serve_file(filename):
    try:
        return send_from_directory(Config.UPLOAD_FOLDER, filename)
    except Exception as e:
        logger.error(f"Error serving file {filename}: {str(e)}")
        return jsonify({"error": "File not found."}), 404


@app.route('/files', methods=['GET'])
def list_files():
    files = []
    try:
        for filename in os.listdir(UPLOAD_FOLDER):
            # Get full file path
            file_path = os.path.join(UPLOAD_FOLDER, filename)

            # Skip directories, only process files
            if os.path.isdir(file_path):
                continue

            # Get file statistics (size, modification date, etc.)
            file_stats = os.stat(file_path)

            # Append file information to the list
            files.append({
                'id': str(file_stats.st_ino),
                'name': filename,
                'size': file_stats.st_size,
                'date': file_stats.st_mtime,
                'path': f'{UPLOAD_FOLDER}/{filename}'
            })
        return jsonify(files)
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return jsonify([])  # Return an empty list on error


@app.route('/convert', methods=['POST'])
def convert():
    try:
        # Check if file is in request
        if 'lc_file' not in request.files:
            logger.error("No file provided in request.")
            return jsonify({"error": "No file provided. Please upload a valid .txt file."}), 400

        file = request.files['lc_file']

        # Check for empty file name
        if file.filename == '':
            logger.error("No file selected.")
            return jsonify({"error": "No file selected. Please choose a file to upload."}), 400

        # Validate file type
        if not file.filename.endswith('.txt'):
            logger.error(f"Invalid file type: {file.filename}")
            return jsonify({"error": "Invalid file type. Only .txt files are supported."}), 400

        filename = secure_filename(file.filename)
        lc_file_path = Path(Config.LETTER_OF_CREDIT_FILE)
        file.save(lc_file_path)

        # Read and process Letter of Credit file
        with open(lc_file_path, 'r', encoding='utf-8') as lc_file:
            lc_text = lc_file.read()

        lc_info = processor.process_letter_of_credit(lc_file_path)
        if not lc_info:
            logger.error("Failed to extract information from Letter of Credit.")
            return jsonify({"error": "Processing failed. Unable to extract information."}), 500

        logger.info("Successfully processed Letter of Credit")

        # Extract BOL, verification, and required documents
        result, documents_list, verification_points = None, None, None

        if '46A' in lc_info:
            bol_text = lc_info['46A']['value']
            result = processor.process_bill_of_lading(bol_text)
            documents_list = processor.process_documents(bol_text)

            if result:
                result['Notify name and address'] = result.pop(
                    'Notify name and address (or blank endorsed)', None)
                logger.info("Extracted Bill of Lading data")
            else:
                logger.warning("No Bill of Lading data found")

        if '47A' in lc_info:
            verification_text = lc_info['47A']['value']
            verification_points = processor.process_verification_points(verification_text)

            if verification_points:
                logger.info("Extracted verification points")
            else:
                logger.warning("No verification points extracted")

        output_filename = f"{Path(Config.OUTPUT_FILE1).stem}_{lc_info.get('21', {}).get('value', 'UNKNOWN')}.docx"
        final_output_path = Path(Config.OUTPUT_FILE1).parent / output_filename

        process_and_fill_document(lc_info, result, verification_points, documents_list, {})

        return jsonify({
            "message": "Document processed successfully!",
            "document_filename": output_filename,
            "BOL Extraction": result or "No Bill of Lading data found",
            "Verification Points": verification_points or "No verification points extracted",
            "Required Documents": documents_list or "No required documents extracted"
        }), 200

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred.", "details": str(e)}), 500


@app.route('/download-document', methods=['GET'])
def download_document():
    try:
        # Path to the latest generated document
        document_path = Path(Config.OUTPUT_FILE1).parent
        files = list(document_path.glob("*.docx"))  # Get all .docx files

        if not files:
            return jsonify({"error": "No processed documents found. Please process a Letter of Credit first."}), 404

        # Get the most recent file
        latest_file = max(files, key=lambda f: f.stat().st_mtime)

        # Serve the file for download
        return send_file(latest_file, as_attachment=True)

    except Exception as e:
        logger.error(f"Error while trying to download document: {str(e)}")
        return jsonify({"error": "An unexpected error occurred while retrieving the document.", "details": str(e)}), 500


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
