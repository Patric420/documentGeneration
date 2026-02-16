import logging
from typing import List
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

logger = logging.getLogger(__name__)

def save_text_as_pdf(text: str, output_path: str) -> None:
    """
    Save text content as a PDF file using ReportLab.
    
    Args:
        text: Text content to save
        output_path: Path for output PDF file
    """
    logger.info(f"Saving text as PDF: {output_path}")
    try:
        doc = SimpleDocTemplate(output_path)
        styles = getSampleStyleSheet()
        elements: List = []

        for line in text.split("\n"):
            if line.strip() == "":
                elements.append(Spacer(1, 10))
            else:
                # Escape HTML special characters for ReportLab
                safe_text = (line.replace("&", "&amp;")
                                .replace("<", "&lt;")
                                .replace(">", "&gt;"))
                elements.append(Paragraph(safe_text, styles["Normal"]))

        doc.build(elements)
        logger.info(f"PDF successfully saved: {output_path}")
    except Exception as e:
        logger.error(f"Error saving PDF: {str(e)}", exc_info=True)
        raise
