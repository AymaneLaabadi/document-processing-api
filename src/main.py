import logging
from pathlib import Path
import json
import sys
from typing import Dict, Optional, Tuple

from src.config import Config
from src.preprocessor import TextPreprocessor
from src.paragraph_matcher import ParagraphMatcher
from src.models.letter_of_credit_parser import LetterOfCreditParser
from src.models.bill_of_lading_parser import BillOfLadingParser
from src.models.verification_points_extractor import VerificationExtraction
from src.models.required_documents_extractor import RequiredDocumentsExtractor

from src.models.template_document_filler import DocumentFiller

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('../logs/extraction.log')
    ]
)

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Main class for processing Letter of Credit and Bill of Lading documents.
    """

    def __init__(self):
        """Initialize document processor with necessary extractors."""
        self.lc_extractor = LCExtractor()
        self.bol_extractor = BOLExtractor()
        self.verification_extractor = VerificationExtraction()
        self.documents_extractor = DocumentsExtractor()  # New Extractor
        self.preprocessor = TextPreprocessor()
        self.matcher = ParagraphMatcher()

    def process_letter_of_credit(self, file_path: Path) -> Optional[Dict]:
        """
        Process a Letter of Credit document.

        Args:
            file_path (Path): Path to the Letter of Credit file

        Returns:
            Optional[Dict]: Extracted LC information or None if processing fails
        """
        try:
            with open(file_path, "r", encoding='utf-8') as file:
                letter_of_credit = file.read()
                logger.info(f"Successfully read Letter of Credit file: {file_path}")
                return self.lc_extractor.extract_lc_info(letter_of_credit)
        except FileNotFoundError:
            logger.error(f"Letter of Credit file not found at {file_path}")
        except Exception as e:
            logger.error(f"Error processing Letter of Credit: {str(e)}")
        return None

    def process_bill_of_lading(self, bol_text: str) -> Optional[Dict]:
        """
        Process Bill of Lading text.

        Args:
            bol_text (str): Bill of Lading text to process

        Returns:
            Optional[Dict]: Extracted BOL information or None if processing fails
        """
        try:
            # Preprocess the text
            processed_text = self.preprocessor.preprocess_text(bol_text)
            separated_paragraphs = self.preprocessor.separate_paragraphs(processed_text)

            # Find similar paragraphs
            similar_paragraphs = self.matcher.find_similar_paragraphs(
                separated_paragraphs,
                Config.BL_REFERENCE_PARAGRAPHS
            )

            if not similar_paragraphs:
                logger.error("No similar paragraphs found in BOL text")
                return None

            # Get the most similar paragraph
            input_text = similar_paragraphs[0]["most_similar_paragraph"]
            logger.info(f"Found matching paragraph with similarity score: {similar_paragraphs[0]['similarity_score']}")

            # Extract information from the matched paragraph
            return self.bol_extractor.extract_information(input_text)

        except Exception as e:
            logger.error(f"Error processing Bill of Lading: {str(e)}")
            return None

    def process_verification_points(self, verification_text: str) -> Optional[str]:
        """
        Process verification points from LC text.

        Args:
            verification_text (str): Letter of Credit text under field 47A.

        Returns:
            Optional[str]: Extracted verification points as bullet points.
        """
        try:
            return self.verification_extractor.extract_verification_points(verification_text)
        except Exception as e:
            logger.error(f"Error extracting verification points: {str(e)}")
            return None

    def process_documents(self, documents_text: str) -> Optional[str]:
        """
        Process required documents from LC text.

        Args:
            documents_text (str): Letter of Credit text under field 46A.

        Returns:
            Optional[str]: Extracted document list as bullet points.
        """
        try:
            return self.documents_extractor.extract_documents(documents_text)
        except Exception as e:
            logger.error(f"Error extracting required documents: {str(e)}")
            return None


def process_and_fill_document(lc_info: Dict, result: Dict, verification_points: str, documents_list: str, filling_list: Dict) -> None:
    """
    Process the document filling with extracted information.

    Args:
        lc_info (Dict): Extracted LC information
        result (Dict): BOL processing result
        verification_points (str): Extracted verification points
        documents_list (str): Extracted required documents list
        filling_list (Dict): Combined information for filling
    """
    try:
        # Add verification points and document list to filling list
        filling_list["Verification Points"] = verification_points
        filling_list["Required Documents"] = documents_list

        # Initialize document fillers for two templates
        document_filler1 = DocumentFiller(Config.TEMPLATE_FILE1)
        document_filler2 = DocumentFiller(Config.TEMPLATE_FILE2)
        document_filler3 = DocumentFiller(Config.TEMPLATE_FILE3)

        # Fill and save documents
        document_filler1.fill_document(filling_list)
        document_filler2.fill_document(filling_list)
        document_filler3.fill_document(filling_list)

        document_filler1.save_document(Config.OUTPUT_FILE1, filling_list)
        document_filler2.save_document(Config.OUTPUT_FILE2, filling_list)
        document_filler3.save_document(Config.OUTPUT_FILE3, filling_list)

        logger.info("Document filling completed successfully")

    except Exception as e:
        logger.error(f"Error in document filling process: {str(e)}")
        raise


def main():
    """Main function to run the document processing pipeline."""
    try:
        logger.info("Starting document processing")

        # Initialize document processor
        processor = DocumentProcessor()

        # Process Letter of Credit
        lc_info = processor.process_letter_of_credit(Config.LETTER_OF_CREDIT_FILE)
        if not lc_info:
            logger.error("Failed to process Letter of Credit")
            return

        logger.info("Successfully processed Letter of Credit")

        # Generate filling dictionary
        filling_list = LCExtractor.List_information_gen(lc_info)

        # Process Bill of Lading if '46A' field exists
        result = None
        documents_list = None
        if '46A' in lc_info:
            bol_text = lc_info['46A']['value']
            result = processor.process_bill_of_lading(bol_text)
            documents_list = processor.process_documents(bol_text)  # Extract documents

            if result:
                result['Notify name and address'] = result.pop(
                    'Notify name and address (or blank endorsed)', None)
                logger.info("Successfully extracted BOL information")
                for key, value in result.items():
                    filling_list[key] = value
            else:
                logger.error("Failed to extract BOL information")

        else:
            logger.error("No '46A' field found in Letter of Credit")

        # Process Verification Extraction if '47A' field exists
        verification_points = None
        if '47A' in lc_info:
            verification_text = lc_info['47A']['value']
            verification_points = processor.process_verification_points(verification_text)
            if verification_points:
                logger.info("Successfully extracted verification points")
            else:
                logger.error("Failed to extract verification points")
        else:
            logger.error("No '47A' field found in Letter of Credit")

        # Process document filling
        process_and_fill_document(lc_info, result, verification_points, documents_list, filling_list)

        # Print extraction results
        final_output = {
            "BOL Extraction": result,
            "Verification Points": verification_points,
            "Required Documents": documents_list,
            "Filled Document Data": filling_list
        }
        print(final_output)

    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise


if __name__ == "__main__":
    main()