import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.conf import settings

def generate_customer_pdf(customer):
    try:
        # Define the directory where the PDFs will be stored
        pdf_directory = os.path.join(settings.MEDIA_ROOT, 'pdfs')

        # Ensure the directory exists
        if not os.path.exists(pdf_directory):
            os.makedirs(pdf_directory)

        # Define the PDF file path
        pdf_filename = f"{customer.name}_details.pdf"
        pdf_path = os.path.join(pdf_directory, pdf_filename)

        # Create a PDF
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.drawString(100, 750, f"Customer Name: {customer.name}")
        c.drawString(100, 730, f"Email: {customer.email}")
        c.drawString(100, 710, f"Phone: {customer.phone_number}")
        c.drawString(100, 690, f"Country Code: {customer.country_code}")
        if customer.birthdate:
            c.drawString(100, 670, f"Birthdate: {customer.birthdate}")

        # Save the PDF
        c.showPage()
        c.save()

        # Return the path to the generated PDF
        print(f"PDF generated at: {pdf_path}")  # Debug statement
        return pdf_path

    except Exception as e:
        print(f"Error generating PDF: {e}")  # Debug any exceptions
        return None
