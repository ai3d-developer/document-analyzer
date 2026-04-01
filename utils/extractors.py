import io
import fitz  # PyMuPDF
import docx
import pytesseract
from PIL import Image

def validate_image_format(content: bytes) -> bool:
    """Checks if the file is a valid image"""
    try:
        Image.open(io.BytesIO(content)).verify()
        return True
    except Exception:
        return False

def extract_text_from_pdf(content: bytes) -> str:
    """Extracts text from a PDF file using PyMuPDF"""
    try:
        # Load PDF from memory bytes
        doc = fitz.open(stream=content, filetype="pdf")
        text = []
        for page in doc:
            text.append(page.get_text("text"))
        return "\n".join(text).strip()
    except Exception as e:
        raise ValueError(f"Failed to extract PDF text: {str(e)}")

def extract_text_from_docx(content: bytes) -> str:
    """Extracts text from a DOCX file using python-docx"""
    try:
        doc = docx.Document(io.BytesIO(content))
        text = [paragraph.text for paragraph in doc.paragraphs]
        return "\n".join(text).strip()
    except Exception as e:
        raise ValueError(f"Failed to extract DOCX text: {str(e)}")

def extract_text_from_image(content: bytes) -> str:
    """Extracts text from an Image using PyTesseract"""
    try:
        image = Image.open(io.BytesIO(content))
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to extract text from Image: {str(e)}")

def extract_text(content: bytes, filename: str, content_type: str) -> str:
    """Main routing function to parse document bytes"""
    filename_lower = filename.lower()
    
    # Simple routing based on file extensions and content_type
    if filename_lower.endswith(".pdf") or "pdf" in content_type:
        return extract_text_from_pdf(content)
        
    elif filename_lower.endswith(".docx") or "officedocument" in content_type:
        return extract_text_from_docx(content)
        
    elif filename_lower.endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff")) or "image" in content_type:
        return extract_text_from_image(content)
        
    else:
        # Fallback to Tesseract if the file is an unknown binary but parses as an image
        if validate_image_format(content):
            return extract_text_from_image(content)
            
        raise ValueError(f"Unsupported file format for {filename}")
