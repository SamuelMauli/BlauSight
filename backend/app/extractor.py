import docx
from pypdf import PdfReader
import logging

def get_text_from_docx(file_path):
    """Extrai texto bruto de um arquivo .docx."""
    try:
        doc = docx.Document(file_path)
        full_text = [para.text for para in doc.paragraphs]
        return '\n'.join(full_text)
    except Exception as e:
        logging.error(f"Erro ao ler docx {file_path}: {e}")
        return ""

def get_text_from_pdf(file_path):
    """Extrai texto bruto de um arquivo .pdf."""
    try:
        reader = PdfReader(file_path)
        full_text = [page.extract_text() for page in reader.pages]
        return '\n'.join(full_text)
    except Exception as e:
        logging.error(f"Erro ao ler pdf {file_path}: {e}")
        return ""