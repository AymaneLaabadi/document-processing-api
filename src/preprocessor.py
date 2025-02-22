import spacy
import re
import unicodedata
from typing import List
from src.config import Config


class TextPreprocessor:
    def __init__(self):
        self.nlp = spacy.load(Config.SPACY_MODEL)

    def preprocess_with_spacy(self, text: str) -> List[str]:
        doc = self.nlp(text)
        tokens = self._tokenize_with_custom_logic(doc)
        return self._clean_tokens(tokens)

    def _tokenize_with_custom_logic(self, doc) -> List[str]:
        tokens = []
        i = 0
        while i < len(doc):
            token_text = doc[i].text

            # Ensure numbers followed by uppercase words are kept correctly (e.g., "40000 MT")
            if self._is_number_letter_combination(doc, i):
                token_text += " " + doc[i + 1].text  # Preserve space instead of merging
                i += 1  # Skip next token since it's already merged
                tokens.append(token_text)
                i += 1
                continue  # Prevent duplicate addition

            # Ensure colons are properly spaced (e.g., "45A : Description")
            elif self._is_colon_separated(token_text):
                token_text = re.sub(r'(\w)(:)(\w)', r'\1 : \3', token_text)  # Add spaces around ':'
                tokens.append(token_text)

            # Preserve line breaks correctly (so text doesn't collapse into one line)
            elif "\n" in token_text:
                split_lines = token_text.split("\n")
                tokens.extend([line.strip() for line in split_lines if line.strip()])

            else:
                tokens.append(token_text)

            i += 1  # Move to the next token

        return tokens

    @staticmethod
    def separate_paragraphs(text: str) -> list[str]:
        text = ' '.join(text.split())
        pattern = r'(?:\s*\d+\s*\.)(?![0-9])(?:\s+|\b)|(?:[A-Za-z]+\.\d+\.)|(?:\.\s*\d+\s*\.)(?:\s+|\b)'
        sections = re.split(pattern, text)

        paragraphs = []
        for section in sections:
            if section and section.strip():
                section = re.sub(r'\s+', ' ', section.strip())
                paragraphs.append(section)
        return paragraphs

    @staticmethod
    def _is_number_letter_combination(doc, i: int) -> bool:
        return (doc[i].text.isdigit() and
                i + 1 < len(doc) and
                doc[i + 1].text.isalpha() and
                doc[i + 1].text.isupper())

    @staticmethod
    def _is_colon_separated(text: str) -> bool:
        return bool(re.match(r'^\w+:\w+', text))

    @staticmethod
    def _clean_tokens(tokens: List[str]) -> List[str]:
        return [token.strip() for token in tokens if token.strip()]

    @staticmethod
    def preprocess_text(text: str) -> str:
        text = unicodedata.normalize('NFKD', text)
        text = TextPreprocessor._preserve_special_codes(text)
        text = TextPreprocessor._normalize_formatting(text)
        return text.strip()

    @staticmethod
    def _preserve_special_codes(text: str) -> str:
        code_patterns = [
            r'(HS\s*CODE)\s*:\s*([A-Z0-9]+)',
            r'(GST\s*NO\.?)\s*:\s*([A-Z0-9]+)',
            r'(IEC\s*NO\.?)\s*:\s*([A-Z0-9]+)'
        ]

        for pattern in code_patterns:
            text = re.sub(pattern, lambda m: f"{m.group(1)} : {m.group(2)}", text, flags=re.IGNORECASE)
        return text

    @staticmethod
    def _normalize_formatting(text: str) -> str:
        replacements = [
            (r'(?<!\w)(\d+)([A-Za-z]+)(?!\w)', r'\1 \2'),
            (r'(?<!\w)([A-Za-z]+)(\d+)(?!\w)', r'\1 \2'),
            (r'\(\s*', '( '),
            (r'\s*\)', ' )'),
            (r'\b([A-Z])\.', r'\1 .'),
            (r'\b([A-Z]{2,})\.', r'\1 .'),
            (r'\s*-\s*', ' - '),
            (r'\s+', ' ')
        ]

        for pattern, replacement in replacements:
            text = re.sub(pattern, replacement, text)
        return text
