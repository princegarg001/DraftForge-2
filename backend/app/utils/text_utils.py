import re
import unicodedata


def clean_extracted_text(text: str) -> str:
    """
    Normalizes unicode characters, standardizes quotes, removes form feeds,
    and strips excess whitespace while preserving line-break structure.
    """
    if not text:
        return ""
    # Normalize unicode
    text = unicodedata.normalize("NFKD", text)
    # Replace smart quotes and dashes
    text = text.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")
    text = text.replace("—", "-").replace("–", "-")
    # Replace vertical tabs and form feeds with newlines
    text = re.sub(r"[\x0c\x0b]", "\n", text)
    # Normalize multiple consecutive empty lines to maximum 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip trailing whitespace on each line
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(lines).strip()