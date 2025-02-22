import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


class Config:
    # Base paths
    BASE_PATH = Path(__file__).resolve().parent.parent  # Automatically detects backend folder

    # API Keys (loaded from .env)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-default-api-key")

    # Model configurations
    MAX_EXAMPLE_TOKENS = int(os.getenv("MAX_EXAMPLE_TOKENS", 1024))
    SPACY_MODEL = os.getenv("SPACY_MODEL", "en_core_web_sm")

    # File paths (relative, for better portability)
    EXAMPLES_FILE = BASE_PATH / "data/examples/bol-examples.txt"
    LETTER_OF_CREDIT_FILE = BASE_PATH / "data/input/letters_of_credit/letter_of_credit.txt"
    LC_CODES = BASE_PATH / "data/config/lc-codes.json"
    REQUIREMENTS_FILE = BASE_PATH / "requirements.txt"

    # Document templates
    TEMPLATE_FILES = {
        "bill_of_lading": BASE_PATH / "data/input/templates/bill_of_lading_temp.docx",
        "certificate_of_origin": BASE_PATH / "data/input/templates/DRAFT_COO_MAP_MV_CLARA_SAFTCO_temp.docx",
        "bank_letter": BASE_PATH / "data/input/templates/LETTRE_D_ENVOI_BANQUE_RAS_GHUMAYS_DAP_temp.docx"
    }

    # Output files
    OUTPUT_FILES = {
        "bill_of_lading": BASE_PATH / "data/output/Bill_of_Lading.docx",
        "certificate_of_origin": BASE_PATH / "data/output/Certificat_d_Origine.docx",
        "bank_letter": BASE_PATH / "data/output/Lettre_d_envoi.docx"
    }

    # Folder for uploads
    UPLOAD_FOLDER = BASE_PATH / "data/output"

    # Reference paragraphs
    BL_REFERENCE_PARAGRAPHS = [
        "FULL SET OF ORIGINAL CLEAN ON BOARD OCEAN BILLS OF LADING MARKED FREIGHT PAYABLE AS PER CHARTER PARTY MADE OUT TO THE ORDER OF HDFC BANK LTD.,E-13/29, 2ND FLOOR, HARSHA BHAVAN, MIDDLE CIRCLE, CONNAUGHT PLACE, NEW DELHI 110001, INDIA AND NOTIFYING APPLICANT WITH COMPLETE ADDRESS."
    ]

    # Extraction keys
    EXTRACTION_KEYS = [
        "negotiable_copies",
        "non_negotiable_copies",
        "consignee_name",
        "consignee_address",
        "freight_payment_type"
    ]
