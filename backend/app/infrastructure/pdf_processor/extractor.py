"""
PDF text extraction using PyMuPDF and pdfplumber.
"""
import io
from typing import Any

import fitz  # PyMuPDF
import pdfplumber

from app.core.exceptions import PDFExtractionError
from app.core.logging import get_logger

logger = get_logger(__name__)


class PDFExtractor:
    """Extract text and structure from PDF files."""
    
    @staticmethod
    def extract_with_pymupdf(pdf_bytes: bytes) -> dict[str, Any]:
        """
        Extract text using PyMuPDF (fitz).
        
        Args:
            pdf_bytes: PDF file bytes
            
        Returns:
            Extracted data with text, metadata, and structure
        """
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            pages_text = []
            total_text = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                pages_text.append({
                    "page": page_num + 1,
                    "text": text,
                    "blocks": page.get_text("blocks")  # Text blocks with positions
                })
                total_text.append(text)
            
            metadata = doc.metadata
            
            doc.close()
            
            return {
                "text": "\n\n".join(total_text),
                "pages": pages_text,
                "page_count": len(pages_text),
                "metadata": metadata,
                "method": "pymupdf"
            }
        
        except Exception as e:
            logger.error("PyMuPDF extraction failed", extra={"error": str(e)})
            raise PDFExtractionError(f"PyMuPDF extraction failed: {str(e)}")
    
    @staticmethod
    def extract_with_pdfplumber(pdf_bytes: bytes) -> dict[str, Any]:
        """
        Extract text using pdfplumber (better for tables).
        
        Args:
            pdf_bytes: PDF file bytes
            
        Returns:
            Extracted data with text and tables
        """
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                pages_text = []
                total_text = []
                tables = []
                
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    page_tables = page.extract_tables()
                    
                    pages_text.append({
                        "page": page_num + 1,
                        "text": text,
                        "has_tables": len(page_tables) > 0
                    })
                    
                    total_text.append(text)
                    
                    if page_tables:
                        tables.extend([{
                            "page": page_num + 1,
                            "table": table
                        } for table in page_tables])
                
                return {
                    "text": "\n\n".join(total_text),
                    "pages": pages_text,
                    "page_count": len(pages_text),
                    "tables": tables,
                    "method": "pdfplumber"
                }
        
        except Exception as e:
            logger.error("pdfplumber extraction failed", extra={"error": str(e)})
            raise PDFExtractionError(f"pdfplumber extraction failed: {str(e)}")
    
    @staticmethod
    def extract(pdf_bytes: bytes) -> dict[str, Any]:
        """
        Extract text using best available method.
        
        Tries PyMuPDF first, falls back to pdfplumber.
        
        Args:
            pdf_bytes: PDF file bytes
            
        Returns:
            Extracted data
        """
        try:
            # Try PyMuPDF first (faster)
            result = PDFExtractor.extract_with_pymupdf(pdf_bytes)
            
            # If text is empty, try pdfplumber
            if not result["text"].strip():
                logger.info("PyMuPDF returned empty text, trying pdfplumber")
                result = PDFExtractor.extract_with_pdfplumber(pdf_bytes)
            
            return result
        
        except PDFExtractionError:
            # If PyMuPDF fails, try pdfplumber
            logger.info("PyMuPDF failed, trying pdfplumber")
            return PDFExtractor.extract_with_pdfplumber(pdf_bytes)
    
    @staticmethod
    def detect_layout(pdf_bytes: bytes) -> dict[str, Any]:
        """
        Detect PDF layout characteristics.
        
        Args:
            pdf_bytes: PDF file bytes
            
        Returns:
            Layout information
        """
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            if len(doc) == 0:
                return {"columns": 1, "has_images": False}
            
            page = doc[0]  # Analyze first page
            
            # Detect images
            image_list = page.get_images()
            has_images = len(image_list) > 0
            
            # Detect columns (simplified heuristic)
            blocks = page.get_text("blocks")
            if not blocks:
                columns = 1
            else:
                # Sort blocks by vertical position
                sorted_blocks = sorted(blocks, key=lambda b: b[1])
                # Check horizontal clustering
                x_positions = [b[0] for b in sorted_blocks]
                unique_x = len(set(round(x / 10) * 10 for x in x_positions))
                columns = min(unique_x, 3)  # Max 3 columns
            
            doc.close()
            
            return {
                "columns": columns if columns > 0 else 1,
                "has_images": has_images,
                "has_header": False,  # Would need more complex detection
                "has_footer": False
            }
        
        except Exception as e:
            logger.warning("Layout detection failed", extra={"error": str(e)})
            return {"columns": 1, "has_images": False}
