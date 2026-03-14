from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from crewai.tools import tool

import os

@tool("GenerateOfferLetter")
def generate_offer_letter(name: str, ctc: str):
    """Generates a PDF offer letter for the selected candidate."""
    # Ensure directory exists
    output_dir = "offer_letters"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Ensure name is a string and clean it up for filename
    safe_name = str(name).replace(' ', '_')
    file_name = f"Offer_Letter_{safe_name}.pdf"
    file_path = os.path.join(output_dir, file_name)
    
    try:
        c = canvas.Canvas(file_path, pagesize=letter)
        c.drawString(100, 750, "OFFER LETTER")
        c.drawString(100, 700, f"Dear {name},")
        c.drawString(100, 650, "We are pleased to offer you the position of GenAI Software Engineer at Peramatrix.")
        c.drawString(100, 600, f"Your annual CTC will be: {ctc}")
        c.drawString(100, 550, "We look forward to having you on board!")
        c.drawString(100, 500, "Sincerely,")
        c.drawString(100, 480, "Peramatrix Recruitment Team")
        c.save()
        return f"Offer letter generated: {file_path}"
    except Exception as e:
        return f"Failed to generate offer letter: {str(e)}"
