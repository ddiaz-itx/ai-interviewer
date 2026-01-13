"""File upload utilities for handling document uploads."""
import os
import hashlib
from pathlib import Path
from typing import BinaryIO

from fastapi import UploadFile
from PyPDF2 import PdfReader

from app.config import settings


class FileUploadError(Exception):
    """Error during file upload."""

    pass


def ensure_upload_directory() -> Path:
    """
    Ensure upload directory exists.

    Returns:
        Path to upload directory
    """
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def generate_file_hash(file_content: bytes) -> str:
    """
    Generate SHA256 hash of file content.

    Args:
        file_content: File content bytes

    Returns:
        Hex digest of file hash
    """
    return hashlib.sha256(file_content).hexdigest()


async def save_upload_file(upload_file: UploadFile, prefix: str = "") -> str:
    """
    Save uploaded file to disk.

    Args:
        upload_file: FastAPI UploadFile
        prefix: Optional prefix for filename (e.g., 'resume', 'role')

    Returns:
        Relative path to saved file

    Raises:
        FileUploadError: If file save fails
    """
    try:
        # Read file content
        content = await upload_file.read()

        # Generate unique filename using hash
        file_hash = generate_file_hash(content)
        extension = Path(upload_file.filename or "document.pdf").suffix
        filename = f"{prefix}_{file_hash}{extension}" if prefix else f"{file_hash}{extension}"

        # Ensure upload directory exists
        upload_dir = ensure_upload_directory()

        # Save file
        file_path = upload_dir / filename
        with open(file_path, "wb") as f:
            f.write(content)

        # Return relative path
        return str(file_path.relative_to(Path.cwd()))

    except Exception as e:
        raise FileUploadError(f"Failed to save file: {str(e)}") from e


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from PDF file.

    Args:
        file_path: Path to PDF file

    Returns:
        Extracted text content

    Raises:
        FileUploadError: If text extraction fails
    """
    try:
        reader = PdfReader(file_path)
        text_parts = []

        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)

        if not text_parts:
            raise FileUploadError("No text could be extracted from PDF")

        return "\n\n".join(text_parts)

    except Exception as e:
        raise FileUploadError(f"Failed to extract text from PDF: {str(e)}") from e


def validate_file_type(filename: str, allowed_extensions: list[str]) -> bool:
    """
    Validate file extension.

    Args:
        filename: Name of file
        allowed_extensions: List of allowed extensions (e.g., ['.pdf', '.txt'])

    Returns:
        True if valid, False otherwise
    """
    extension = Path(filename).suffix.lower()
    return extension in [ext.lower() for ext in allowed_extensions]


def validate_file_size(file_size: int, max_size_mb: int = 10) -> bool:
    """
    Validate file size.

    Args:
        file_size: File size in bytes
        max_size_mb: Maximum allowed size in MB

    Returns:
        True if valid, False otherwise
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size <= max_size_bytes
