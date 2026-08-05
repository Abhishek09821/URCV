"""
PDF generation using ReportLab and WeasyPrint.
"""
import io
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from app.core.exceptions import PDFGenerationError
from app.core.logging import get_logger
from app.domain.schemas.resume_schema import ResumeJSON

logger = get_logger(__name__)


class PDFGenerator:
    """
    Generate PDF from Resume JSON.
    
    Architectural Decision:
    - Uses ReportLab for simple, ATS-friendly PDFs
    - WeasyPrint for complex template rendering (HTML to PDF)
    - ATS-optimized: no tables, no columns, standard fonts
    """
    
    @staticmethod
    def generate_ats_pdf(resume_json: ResumeJSON) -> bytes:
        """
        Generate ATS-optimized PDF.
        
        Features:
        - Single column layout
        - Standard fonts
        - No images/graphics
        - Clear section headings
        - Bullet points for lists
        
        Args:
            resume_json: Resume data
            
        Returns:
            PDF bytes
        """
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch
            )
            
            # Build content
            story = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            name_style = ParagraphStyle(
                'NameStyle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.black,
                spaceAfter=6,
                alignment=1  # Center
            )
            
            heading_style = ParagraphStyle(
                'HeadingStyle',
                parent=styles['Heading2'],
                fontSize=12,
                textColor=colors.black,
                spaceAfter=6,
                spaceBefore=12,
                borderWidth=1,
                borderColor=colors.black,
                borderPadding=2
            )
            
            normal_style = styles['Normal']
            
            # Personal Info
            story.append(Paragraph(resume_json.personal.fullName, name_style))
            
            contact_parts = []
            if resume_json.personal.email:
                contact_parts.append(resume_json.personal.email)
            if resume_json.personal.phone:
                contact_parts.append(resume_json.personal.phone)
            if resume_json.personal.location:
                if resume_json.personal.location.full:
                    contact_parts.append(resume_json.personal.location.full)
            
            if contact_parts:
                story.append(Paragraph(" | ".join(contact_parts), normal_style))
            
            story.append(Spacer(1, 0.2*inch))
            
            # Summary
            if resume_json.summary:
                story.append(Paragraph("PROFESSIONAL SUMMARY", heading_style))
                story.append(Paragraph(resume_json.summary, normal_style))
                story.append(Spacer(1, 0.1*inch))
            
            # Education
            if resume_json.education:
                story.append(Paragraph("EDUCATION", heading_style))
                for edu in resume_json.education:
                    edu_text = f"<b>{edu.degree or 'Degree'}</b> - {edu.institution}"
                    if edu.field:
                        edu_text += f", {edu.field}"
                    story.append(Paragraph(edu_text, normal_style))
                    
                    date_text = ""
                    if edu.startDate:
                        date_text = edu.startDate.display or str(edu.startDate.year)
                    if edu.endDate:
                        if date_text:
                            date_text += " - "
                        date_text += edu.endDate.display or str(edu.endDate.year)
                    
                    if date_text:
                        story.append(Paragraph(date_text, normal_style))
                    
                    if edu.gpa:
                        story.append(Paragraph(f"GPA: {edu.gpa}", normal_style))
                    
                    story.append(Spacer(1, 0.1*inch))
            
            # Experience
            if resume_json.experience:
                story.append(Paragraph("WORK EXPERIENCE", heading_style))
                for exp in resume_json.experience:
                    exp_text = f"<b>{exp.position}</b> - {exp.company}"
                    story.append(Paragraph(exp_text, normal_style))
                    
                    if exp.startDate or exp.endDate:
                        date_text = ""
                        if exp.startDate:
                            date_text = exp.startDate.display or str(exp.startDate.year)
                        if exp.endDate:
                            if date_text:
                                date_text += " - "
                            date_text += exp.endDate.display or str(exp.endDate.year)
                        elif exp.current:
                            if date_text:
                                date_text += " - "
                            date_text += "Present"
                        story.append(Paragraph(date_text, normal_style))
                    
                    # Responsibilities
                    for resp in exp.responsibilities or []:
                        story.append(Paragraph(f"• {resp}", normal_style))
                    
                    # Achievements
                    for ach in exp.achievements or []:
                        story.append(Paragraph(f"• {ach}", normal_style))
                    
                    story.append(Spacer(1, 0.1*inch))
            
            # Projects
            if resume_json.projects:
                story.append(Paragraph("PROJECTS", heading_style))
                for proj in resume_json.projects:
                    story.append(Paragraph(f"<b>{proj.title}</b>", normal_style))
                    story.append(Paragraph(proj.description, normal_style))
                    
                    if proj.technologies:
                        tech_text = f"Technologies: {', '.join(proj.technologies)}"
                        story.append(Paragraph(tech_text, normal_style))
                    
                    for highlight in proj.highlights or []:
                        story.append(Paragraph(f"• {highlight}", normal_style))
                    
                    story.append(Spacer(1, 0.1*inch))
            
            # Skills
            if resume_json.skills and resume_json.skills.technical:
                story.append(Paragraph("TECHNICAL SKILLS", heading_style))
                for cat in resume_json.skills.technical:
                    skills_text = f"<b>{cat.category}:</b> {', '.join(cat.skills)}"
                    story.append(Paragraph(skills_text, normal_style))
            
            # Certifications
            if resume_json.certifications:
                story.append(Paragraph("CERTIFICATIONS", heading_style))
                for cert in resume_json.certifications:
                    cert_text = f"<b>{cert.name}</b> - {cert.issuer}"
                    story.append(Paragraph(cert_text, normal_style))
                    if cert.issueDate:
                        story.append(Paragraph(cert.issueDate.display or str(cert.issueDate.year), normal_style))
            
            # Achievements
            if resume_json.achievements:
                story.append(Paragraph("ACHIEVEMENTS", heading_style))
                for ach in resume_json.achievements:
                    story.append(Paragraph(f"• {ach.title}", normal_style))
                    if ach.description:
                        story.append(Paragraph(ach.description, normal_style))
            
            # Build PDF
            doc.build(story)
            
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            logger.info("ATS PDF generated successfully")
            return pdf_bytes
        
        except Exception as e:
            logger.error("PDF generation failed", extra={"error": str(e)})
            raise PDFGenerationError(f"Failed to generate PDF: {str(e)}")
    
    @staticmethod
    def generate_simple_pdf(resume_json: ResumeJSON) -> bytes:
        """
        Generate simple PDF (alias for ATS PDF).
        
        Args:
            resume_json: Resume data
            
        Returns:
            PDF bytes
        """
        return PDFGenerator.generate_ats_pdf(resume_json)


# Global generator instance
pdf_generator = PDFGenerator()
