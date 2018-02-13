from django.utils import timezone
from django.http import HttpResponse
from reportlab.pdfgen.canvas import Canvas
from reportlab.rl_config import defaultPageSize
from .models import Incident


PAGE_WIDTH = defaultPageSize[0]
PAGE_HEIGHT = defaultPageSize[1]
PAGE_CENTER_X = PAGE_WIDTH / 2.0

LEFT_ALIGN_X = 15
TOP_ALIGN_Y = 800


class IncidentReportPDFGenerator:
    def __init__(self, response: HttpResponse, incident_id: int):
        self.response = response
        self.incident = Incident.objects.get(id=incident_id)
        self.pdf = Canvas(response)
        self.row_number = 1

    def _draw_standard_label(self, label_text: str, alignment: str="left") -> None:
        """
        Draws a standard (i.e. evenly spaced rows) label on the PDF
        :param row_number: The row, one indexed, that the label should be drawn on.
        :param label_text: The text the label should disply.
        :return: None
        """
        # if alignment == "left":
        x_position = LEFT_ALIGN_X
        y_position = TOP_ALIGN_Y - ((self.row_number - 1) * 12)
        self.pdf.drawString(x_position, y_position, label_text)
        self.row_number += 1

    def _draw_labels(self):
        self.pdf.setFont("Courier", 10)
        self._draw_standard_label("Printed By:")
        self._draw_standard_label("Print Date:")
        self.pdf.drawCentredString(PAGE_CENTER_X, TOP_ALIGN_Y - 35, "ATLANTA POLICE DEPARTMENT")
        self.pdf.drawCentredString(PAGE_CENTER_X, TOP_ALIGN_Y - 50, "Offense Report")
        self.pdf.drawCentredString(PAGE_CENTER_X, TOP_ALIGN_Y - 65,
                                   f"INCIDENT NUMBER: {self.incident.incident_number}")
        self.pdf.drawCentredString(PAGE_CENTER_X, TOP_ALIGN_Y - 85,
                                   "------------ INCIDENT INFORMATION ------------")
        self.row_number = 10
        self._draw_standard_label("Report Date:")
        self._draw_standard_label("Time:")
        self._draw_standard_label("Reporting Officer:")
        self._draw_standard_label("Reviewed by Officer:")
        self._draw_standard_label("Investigating Officer:")
        self._draw_standard_label("Officer Making Rpt:")
        self._draw_standard_label("Supervisor:")
        self._draw_standard_label("Occur/Earliest Date / Time:")
        self._draw_standard_label("Location:")
        self._draw_standard_label("Latest Poss Date / Time:")
        self._draw_standard_label("Assoc Offense #:")
        self._draw_standard_label("RD:")
        self._draw_standard_label("Zone:")
        self._draw_standard_label("Damaged Amount:")
        self._draw_standard_label("Disposition:")

    def _draw_data(self):
        # TODO: There should be some sort of map for data fields and the (x, y) position
        # Each field should be drawn at
        # Should labels and data really be separated?
        today = timezone.now().date()
        us_format_date_string = today.strftime("%m/%d/%Y")
        self.pdf.drawString(87, 788, us_format_date_string)

    def generate(self) -> Canvas:
        self._draw_labels()
        self._draw_data()
        self.pdf.showPage()
        self.pdf.save()
        return self.pdf
