import re
import io


def clean_text(text):
    text = re.sub(r'<[^>]*?>', '', text)
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
    text = re.sub(r'\s{2,}', ' ', text)
    text = text.strip()
    text = ' '.join(text.split())
    return text


def export_to_pdf(email_text: str, role: str = "Job Application") -> bytes:
    """Generate a PDF from email text. Returns bytes."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.enums import TA_LEFT

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2.5 * cm,
            leftMargin=2.5 * cm,
            topMargin=2.5 * cm,
            bottomMargin=2.5 * cm,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "Title",
            parent=styles["Heading1"],
            fontSize=16,
            spaceAfter=12,
        )
        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontSize=11,
            leading=16,
            alignment=TA_LEFT,
        )

        story = []
        story.append(Paragraph(f"Cold Email — {role}", title_style))
        story.append(Spacer(1, 0.3 * cm))

        for line in email_text.split("\n"):
            line = line.strip()
            if line:
                story.append(Paragraph(line, body_style))
                story.append(Spacer(1, 0.15 * cm))

        doc.build(story)
        return buffer.getvalue()

    except ImportError:
        # Fallback: plain text PDF-like bytes if reportlab not installed
        return email_text.encode("utf-8")


def export_to_docx(email_text: str, role: str = "Job Application") -> bytes:
    """Generate a DOCX from email text. Returns bytes."""
    try:
        from docx import Document
        from docx.shared import Pt, Cm
        from docx.enum.text import WD_ALIGN_PARAGRAPH

        doc = Document()

        # Page margins
        for section in doc.sections:
            section.top_margin = Cm(2.5)
            section.bottom_margin = Cm(2.5)
            section.left_margin = Cm(2.5)
            section.right_margin = Cm(2.5)

        # Title
        title = doc.add_heading(f"Cold Email — {role}", level=1)
        title.alignment = WD_ALIGN_PARAGRAPH.LEFT

        doc.add_paragraph()  # spacer

        for line in email_text.split("\n"):
            line = line.strip()
            if line:
                p = doc.add_paragraph(line)
                p.runs[0].font.size = Pt(11)
            else:
                doc.add_paragraph()

        buffer = io.BytesIO()
        doc.save(buffer)
        return buffer.getvalue()

    except ImportError:
        return email_text.encode("utf-8")
