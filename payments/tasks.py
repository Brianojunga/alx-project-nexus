from celery import shared_task

from django.core.mail import EmailMessage
from reportlab.pdfgen import canvas
from io import BytesIO

@shared_task
def send_payment_confirmation_email(user_email, reference, amount):
    print(f'Task started: Generating PDF for {reference}...')
    buffer = BytesIO
    pdf = canvas.Canvas(buffer)
    pdf.drawString(100, 800, "Electronic Ticket")
    pdf.drawString(100, 780, ".................")
    pdf.drawString(100, 750, f"Payment_reference: {reference}")
    pdf.drawString(100, 730, f"Amount: sh {amount}")
    pdf.drawString(100, 710, f"Status: Paid")

    pdf.showPage()
    pdf.save()

    pdf_content = buffer.getvalue()
    buffer.close()

    subject = f'Payment Confirmation {reference}'
    body = f'Thank you for your payment. Please find your payment OF reference {reference} in the attached file.'
    email = EmailMessage(subject, body, 'no-reply@yourdomain.com', user_email)
    email.attach(f'Payment_{reference}.pdf', pdf_content, 'application/pdf')

    print('Task finished: PDF generated and email sent')