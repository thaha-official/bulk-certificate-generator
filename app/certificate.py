from reportlab.pdfgen import canvas
import os


def generate_certificate(
    recipient_name,
    event_name,
    certificate_title,
    issue_date,
    certificate_id
):
    os.makedirs("certificates", exist_ok=True)

    file_path = f"certificates/certificate_{certificate_id}.pdf"

    c = canvas.Canvas(file_path)

    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(
        300,
        700,
        certificate_title
    )

    c.setFont("Helvetica", 16)
    c.drawCentredString(
        300,
        620,
        "This certificate is presented to"
    )

    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(
        300,
        570,
        recipient_name
    )

    c.setFont("Helvetica", 14)
    c.drawCentredString(
        300,
        500,
        f"For participating in {event_name}"
    )

    c.drawCentredString(
        300,
        450,
        f"Date: {issue_date}"
    )

    c.save()

    return file_path