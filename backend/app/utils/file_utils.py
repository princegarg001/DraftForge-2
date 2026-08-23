import hashlib
from typing import Tuple


def compute_sha256(content: bytes) -> str:
    """Computes a secure SHA-256 checksum hex digest for binary content."""
    sha256_hash = hashlib.sha256()
    sha256_hash.update(content)
    return sha256_hash.hexdigest()


def extract_filename_and_ext(filename: str) -> Tuple[str, str]:
    """Extracts base filename and lowercase extension without the dot."""
    if "." not in filename:
        return filename, ""
    parts = filename.rsplit(".", 1)
    return parts[0], parts[1].lower()