import openai
import logging
from typing import Optional
from src.config import Config

logger = logging.getLogger(__name__)


class RequiredDocumentsExtractor:

    """
    A class for extracting document requirements from a given paragraph using GPT-4o-mini API.
    """

    def __init__(self):
        """Initialize the DocumentsExtractor with OpenAI API key."""
        openai.api_key = Config.OPENAI_API_KEY  # Ensure this is set in your config

    def extract_documents(self, paragraph: str) -> Optional[str]:
        """
        Extracts all required documents mentioned in the given paragraph.

        Args:
            paragraph (str): The paragraph containing document references.

        Returns:
            Optional[str]: A bullet-point list of extracted document names.
        """
        prompt = (
            "Identifiez et extrayez uniquement les documents requis mentionnés dans le paragraphe suivant. "
            "Retournez la liste sous forme de points à puces en écrivant les noms des documents de manière simple et concise, "
            "sans reformulation excessive ni explication. "
            "Ecrivez les noms des documents en francais."
            "Indiquez les quantités d’originaux et de copies de manière claire et courte.\n\n"
            f"Paragraphe :\n{paragraph}\n\n"
            "Format attendu :\n"
            "- [Nom du document] [Nombre d'originaux et/ou copies]\n"
            "- [Nom du document] [Nombre d'originaux et/ou copies]\n"
            "- [Nom du document] [Nombre d'originaux et/ou copies]"
        )

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": "You are an assistant for structured document extraction."},
                          {"role": "user", "content": prompt}],
                max_tokens=200
            )

            # Extract and clean the response
            document_list = response["choices"][0]["message"]["content"].strip()

            return document_list

        except Exception as e:
            logger.error(f"Error extracting documents: {str(e)}")
            return None
