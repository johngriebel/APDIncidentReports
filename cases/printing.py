from django.utils import timezone
from django.http import HttpResponse
from reportlab.pdfgen.canvas import Canvas
from .models import Incident


class IncidentReportPDFGenerator:
    def __init__(self, response: HttpResponse, incident_id: int):
        self.response = response
        self.incident = Incident.objects.get(id=incident_id)
        self.pdf = Canvas(response)

    def _draw_labels(self):
        self.pdf.setFont("Courier", 10)
        self.pdf.drawString(15, 750, "Print Date:")

    def generate(self) -> Canvas:
        self._draw_labels()
        today = timezone.now().date()
        us_format_date_string = today.strftime("%m/%d/%Y")
        # Draw things on the PDF. Here's where the PDF generation happens.
        # See the ReportLab documentation for the full list of functionality.
        self.pdf.drawString(87, 750, us_format_date_string)
        self.pdf.showPage()
        self.pdf.save()
        return self.pdf
