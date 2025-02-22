import openai
import logging
from typing import Optional
from src.config import Config

logger = logging.getLogger(__name__)


class VerificationExtraction:
    """
    A class for extracting verification points from a Letter of Credit (LC) text using GPT-4o-mini API.
    """

    def __init__(self):
        """Initialize the VerificationExtraction class with the OpenAI API key."""
        openai.api_key = Config.OPENAI_API_KEY  # Ensure this is set in your config

    def extract_verification_points(self, paragraph: str) -> Optional[str]:
        """
        Extracts key verification points from a Letter of Credit (LC) text for Bill of Lading (BL) validation.

        Args:
            paragraph (str): The Letter of Credit text to analyze.

        Returns:
            Optional[str]: A string containing bullet points with verification points.
        """
        prompt = (
            "Extract the specific points that must be verified in the Bill of Lading (BL) document "
            "from the following Letter of Credit (LC) text. "
            "Format the output as a bullet-point list with clear and concise points, "
            "excluding instructions about misspellings or discrepancies.\n\n"
            f"LC Text:\n{paragraph}\n\n"
            "Provide the output as a simple bullet-point list."
        )

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": "You are an assistant for structured document verification."},
                          {"role": "user", "content": prompt}],
                max_tokens=300
            )

            # Extract the generated text
            verification_points = response["choices"][0]["message"]["content"].strip()

            return verification_points

        except Exception as e:
            logger.error(f"Error generating verification points: {str(e)}")
            return None
