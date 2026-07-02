"""
cv_parser.py
------------
Extracts plain text from uploaded CV files (PDF or DOCX).
Supports both file paths and in-memory file objects (from Streamlit uploader).
"""

import pdfplumber
import docx
import io


def extract_text_from_pdf(file) -> str:
    """Extract all text from a PDF file or file-like object."""
    text_blocks = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_blocks.append(page_text)
    return "\n".join(text_blocks)


def extract_text_from_docx(file) -> str:
    """Extract all text from a DOCX file or file-like object."""
    doc = docx.Document(file)
    paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
    return "\n".join(paragraphs)


def parse_cv(uploaded_file) -> str:
    """
    Main entry point. Accepts a Streamlit UploadedFile object.
    Detects file type and returns extracted text.
    
    Args:
        uploaded_file: Streamlit UploadedFile (has .name and .read() attributes)
    
    Returns:
        Extracted text as a string
    
    Raises:
        ValueError: If file type is not supported
    """
    filename = uploaded_file.name.lower()
    file_bytes = io.BytesIO(uploaded_file.read())

    if filename.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif filename.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {filename}. Please upload a PDF or DOCX.")
