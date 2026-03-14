import docx2txt
from pypdf import PdfReader

def get_pdf_text(pdf_path):
    text = ""
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            text += page.extract_text()
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
    return text

def get_docx_text(docx_path):
    try:
        return docx2txt.process(docx_path)
    except Exception as e:
        print(f"Error reading DOCX {docx_path}: {e}")
        return ""
