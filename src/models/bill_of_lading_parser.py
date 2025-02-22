import openai
import logging
import json
from typing import Dict, Optional
from src.config import Config

logger = logging.getLogger(__name__)


class BillOfLadingParser:
    """
    A class for extracting information from LC document using GPT-4o-mini API.
    """

    def __init__(self):
        """Initialize the BOLExtractor with API key."""
        openai.api_key = Config.OPENAI_API_KEY  # Ensure this is set in your config

    def extract_information(self, paragraph: str) -> Dict[str, Optional[str]]:
        """
        Extracts required information from a given Bill of Lading paragraph.

        Args:
            paragraph (str): The paragraph containing the Bill of Lading information.

        Returns:
            Dict[str, Optional[str]]: Extracted structured information.
        """
        prompt = (
            "Extract the required information from the following paragraph and return only a valid JSON object. "
            "Do not include any explanations or extra text. The response must strictly follow this format:\n\n"
            f"Paragraph:\n{paragraph}\n\n"
            "Expected JSON structure:\n"
            "```\n"
            "{\n"
            '  "Number of Negotiable copies": "value",\n'
            '  "Number of Non-Negotiable copies": "value",\n'
            '  "Notify name and address (or blank endorsed)": "value",\n'
            '  "Consignee name and address": "value",\n'
            '  "Freight payment type": "value"\n'
            "}\n"
            "```\n"
            "Return only valid JSON, without any extra text or explanations."
        )

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": "You are an assistant for structured information extraction."},
                          {"role": "user", "content": prompt}],
                max_tokens=200
            )

            # Extract and clean the JSON response
            extracted_data = response["choices"][0]["message"]["content"].strip()

            # Ensure JSON output by cleaning extra text
            extracted_data = self._extract_json_from_text(extracted_data)

            try:
                return json.loads(extracted_data)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON. Raw response: {extracted_data}")
                return {}

        except Exception as e:
            logger.error(f"Error generating model output: {str(e)}")
            return {}


    @staticmethod
    def _extract_json_from_text(text: str) -> str:
        """
        Extracts the JSON portion from the model's response in case of extra text.
        """
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end != -1:
                extracted_json = text[start:end].strip()
                if extracted_json.endswith("```"):
                    extracted_json = extracted_json[:-3].strip()
                return extracted_json
            return text  # Fallback in case the format is incorrect
        except Exception as e:
            logger.error(f"Error extracting JSON from text: {str(e)}")
            return text  # Return as-is if extraction fails

