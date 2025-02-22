import json, re
from typing import Dict, List, Tuple
from src.preprocessor import TextPreprocessor
from src.config import Config

list_codes = ["59", "50", "44E", "44F", "45A", "20", "21", "31C"]

class LetterOfCreditParser:
    def __init__(self):
        self.preprocessor = TextPreprocessor()
        self.lc_codes = self._load_lc_codes()

    @staticmethod
    def _load_lc_codes() -> Dict[str, str]:
        try:
            with open(Config.LC_CODES, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading LC codes: {str(e)}")
            return {}

    def extract_lc_info(self, text: str) -> Dict[str, dict]:
        tokens = self.preprocessor.preprocess_with_spacy(text)
        return self._extract_from_tokens(tokens)

    def _extract_from_tokens(self, tokens: List[str]) -> Dict[str, dict]:
        extracted_info = {}
        i = 0
        while i < len(tokens):
            if self._is_valid_code(tokens, i):
                code = tokens[i]
                value, next_i = self._extract_value(tokens, i + 2)
                extracted_info[code] = {
                    "description": self.lc_codes.get(code, ""),
                    "value": value
                }
                i = next_i
            else:
                i += 1
        return extracted_info

    def _is_valid_code(self, tokens: List[str], i: int) -> bool:
        return (not self._is_reference(tokens, i) and
                tokens[i] in self.lc_codes and
                i + 1 < len(tokens) and
                tokens[i + 1] == ":")

    @staticmethod
    def _is_reference(tokens: List[str], i: int) -> bool:
        if i >= 2:
            prev_tokens = ' '.join(tokens[i - 2:i]).upper()
            return "REFER FIELD" in prev_tokens
        return False

    def _extract_value(self, tokens: List[str], start_idx: int) -> Tuple[str, int]:
        value_tokens = []
        i = start_idx

        while i < len(tokens):
            if self._is_valid_code(tokens, i):
                break
            value_tokens.append(tokens[i])
            i += 1

        value = ' '.join(value_tokens).strip()
        if value.endswith(':'):
            value = value[:-1]
        return value.strip(), i

    import re

    import re

    def List_information_gen(lc_dict):
        result_dict = {}

        # Refined regular expressions with precise matching
        text_to_remove = {
            "45A": r"(?i)\bDescription\s+of\s+Goods\s+and/or\s+Services\b",
            "44F": r"(?i)\bPort\s+of\s+Discharge\s*/\s*Airport\s+of\s+Destination\b",
            "44E": r"(?i)\bPort\s+of\s+Loading\s*/\s*Airport\s+of\s+Departure\b",
            "50": r"(?i)\bApplicant\b",
            "59": r"(?i)\bBeneficiary\b",
            "20": r"(?i)\bSender\s*'?s\s+Reference\b",  # Handles both "Sender's Reference" and "Sender 's Reference"
            "21": r"(?i)\bDocumentary\s+Credit\s+Number\b",
            "31C": r"(?i)\bDate\s+of\s+Issue\b"
        }

        for code in text_to_remove:
            try:
                text = lc_dict[code]['value']

                # Normalize spaces before processing
                text = re.sub(r"\s+", " ", text).strip()  # Remove extra spaces

                # Remove unnecessary labels
                text = re.sub(text_to_remove[code], '', text, flags=re.IGNORECASE).strip()

                # Special handling for "45A" to extract Gross Weight
                if code == "45A":
                    match = re.search(r"^(.*?)\s*MT\s*(.*)", text, flags=re.IGNORECASE)
                    if match:
                        result_dict["gross weight"] = match.group(1).strip()  # Everything before "MT"
                        text = match.group(2).strip()  # Everything after "MT" remains in "45A"

                result_dict[code] = text

            except KeyError:
                result_dict[code] = ""

        return result_dict

