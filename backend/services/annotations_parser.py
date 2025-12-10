# backend/services/annotations_parser.py
import re

class AnnotationsParser:

    def __init__(self):
        # Example pattern for Unique IDs; adjust as needed
        self.unique_id_pattern = re.compile(r"[A-Z0-9]{10,}")

    def get_unique_ids(self, annotations):
        """
        Extract unique IDs from Google OCR annotations.
        """
        text_blocks = [a.description for a in annotations] if annotations else []

        unique_ids = []
        for block in text_blocks:
            matches = self.unique_id_pattern.findall(block)
            for match in matches:
                unique_ids.append((match, block))
        return unique_ids
