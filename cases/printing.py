from django.utils import timezone
from django.http import HttpResponse
from reportlab.pdfgen.canvas import Canvas
from reportlab.rl_config import defaultPageSize
from textwrap import wrap
from .models import Incident, Offense, IncidentInvolvedParty
from .constants import VICTIM, SUSPECT


PAGE_WIDTH = defaultPageSize[0]
PAGE_HEIGHT = defaultPageSize[1]
PAGE_CENTER_X = PAGE_WIDTH / 2.0

LEFT_ALIGN_X = 25
COLUMN_ONE_X = 100
COLUMN_TWO_X = 200
COLUMN_THREE_X = 300
COLUMN_FOUR_X = 400
TOP_ALIGN_Y = 800

MAX_TEXT_LINE_WIDTH = 90


class IncidentReportPDFGenerator:
    def __init__(self, response: HttpResponse, incident_id: int):
        print(("WIDTH", PAGE_WIDTH, "HEIGHT", PAGE_HEIGHT))
        self.response = response
        self.incident = Incident.objects.get(id=incident_id)
        self.pdf = Canvas(response)
        self.row_number = 1
        self.page_number = 1

    def _draw_label(self, label_text: str, row: int=None, column: int=0, centered=False) -> None:
        """
        Draws a standard (i.e. evenly spaced rows) label on the PDF
        :param row_number: The row, one indexed, that the label should be drawn on.
        :param label_text: The text the label should disply.
        :return: None
        """
        draw_func = self.pdf.drawString
        if row is None:
            row = self.row_number
            self.row_number += 1
        if centered:
            x_position = PAGE_CENTER_X
            draw_func = self.pdf.drawCentredString
        elif column == 1:
            x_position = COLUMN_ONE_X
        elif column == 2:
            x_position = COLUMN_TWO_X
        elif column == 3:
            x_position = COLUMN_THREE_X
        elif column == 4:
            x_position = COLUMN_FOUR_X
        else:
            x_position = LEFT_ALIGN_X
        y_position = TOP_ALIGN_Y - ((row - 1) * 12)
        draw_func(x_position, y_position, label_text)

    @property
    def current_y_position(self):
        return TOP_ALIGN_Y - ((self.row_number - 1) * 12)

    def _draw_page_header(self):
        self.pdf.setFont("Courier", 10)
        self._draw_label("Printed By:")
        today = timezone.now().date()
        us_format_date_string = today.strftime("%m/%d/%Y")
        self._draw_label(f"Print Date: {us_format_date_string}")
        self._draw_label("ATLANTA POLICE DEPARTMENT", centered=True)
        self._draw_label("Offense Report", centered=True)
        self._draw_label(f"INCIDENT NUMBER: {self.incident.incident_number}",
                         centered=True)
        self.pdf.drawString(525, TOP_ALIGN_Y, f"Page: {self.page_number}")

    def _draw_labels(self):
        self._draw_page_header()
        self.row_number += 1
        self._draw_label("------------ INCIDENT INFORMATION ------------",
                         centered=True)
        self.row_number += 1
        self._draw_label(f"Report Date: {self.incident.report_datetime.date()}")
        self._draw_label(label_text=f"Time: {self.incident.report_datetime.time()}",
                         row=self.row_number - 1,
                         column=3)
        self._draw_label(f"Reporting Officer: {self.incident.reporting_officer}")
        self._draw_label(f"Reviewed by Officer: {self.incident.reviewed_by_officer}")
        self._draw_label(f"Investigating Officer: {self.incident.investigating_officer}")
        self._draw_label(f"Officer Making Rpt: {self.incident.officer_making_report}")
        self._draw_label(f"Supervisor: {self.incident.supervisor}")
        self._draw_label(f"Occur/Earliest Date / Time: "
                                  f"{self.incident.earliest_occurrence_datetime}")
        self._draw_label(f"Location: {str(self.incident.location)}")
        self._draw_label(f"Latest Poss Date / Time: "
                                  f"{self.incident.latest_occurrence_datetime}")
        self._draw_label(f"Assoc Offense #:")
        self._draw_label(f"RD:")
        self._draw_label(label_text="Beat:",
                         row=self.row_number - 1,
                         column=2)
        self._draw_label(label_text="Shift:",
                         row=self.row_number - 1,
                         column=4)
        self._draw_label(f"Damaged Amount: {self.incident.damaged_amount}")
        self._draw_label(label_text=f"Stolen Amount: {self.incident.stolen_amount}",
                         row=self.row_number - 1,
                         column=2)
        self._draw_label("Disposition:")
        self._draw_label(label_text="Dispo Date:",
                         row=self.row_number - 1,
                         column=2)
        self.row_number += 2
        self._draw_label("------------ OFFENSES ------------",
                         centered=True)
        for offense in self.incident.offenses.all():
            self._draw_offense(offense=offense)

        self.row_number += 2
        self._draw_label("------------ ATTACHMENTS ------------",
                         centered=True)
        self.row_number += 2
        self._draw_label("------------ VICTIM ------------",
                         centered=True)
        # self.row_number += 8
        all_parties = self.incident.incidentinvolvedparty_set.all()
        victims = all_parties.filter(party_type=VICTIM)
        suspects = all_parties.filter(party_type=SUSPECT)

        victim_count = 1
        for victim in victims:
            self._draw_party(count=victim_count,
                              party=victim)
            victim_count += 1

        self.row_number += 2
        self._draw_label("------------ SUSPECT ------------",
                         centered=True)

        suspect_count = 1
        for suspect in suspects:
            self._draw_party(count=suspect_count,
                             party=suspect)
            suspect_count += 1

        self.row_number += 2
        # TODO: Start new page when necessary
        self._draw_label("Incident Narrative",
                         centered=True)
        wrapped_statement = "\n".join(wrap(self.incident.narrative,
                                           MAX_TEXT_LINE_WIDTH))
        text = self.pdf.beginText(LEFT_ALIGN_X, self.current_y_position)
        text.textLines(wrapped_statement)
        self.pdf.drawText(text)

    def _draw_offense(self, offense: Offense):
        self._draw_label(f"Offense: {offense.ucr_name_classification} - "
                                  f"{offense.ucr_subclass_description}")
        self._draw_label(label_text=f"GCIC: {offense.gcic_code}",
                         row=self.row_number,
                         column=1)
        self._draw_label(label_text=f"UCR: {offense.ucr_code}",
                         row=self.row_number,
                         column=3)

    def _draw_party(self, count: int, party: IncidentInvolvedParty):
        self._draw_label(f"{party.party_type.title()} #{count}")
        if party.party_type == SUSPECT:
            self._draw_label("Date and Time Last Updated:")
        self._draw_label("Name:")
        self._draw_label(f"Juvenile? {party.juvenile}")
        self._draw_label(f"Home Address: {str(party.home_address) or ''}")
        self._draw_label(f"SSN: {party.social_security_number}")
        this_row = self.row_number - 1
        self._draw_label(label_text=f"DOB: {party.date_of_birth or ''}",
                         row=this_row,
                         column=2)
        self._draw_label(label_text=f"Sex: {party.sex or ''}",
                         row=this_row,
                         column=3)
        self._draw_label(label_text=f"Race: {party.race or ''}",
                         row=this_row,
                         column=4)
        self._draw_label(f"Hgt: {party.height}")

        this_row = self.row_number - 1
        self._draw_label(label_text=f"Wgt: {party.weight}",
                         row=this_row,
                         column=2)
        self._draw_label(label_text=f"Hair: {party.hair_color}",
                         row=this_row,
                         column=3)
        self._draw_label(label_text=f"Eye: {party.eye_color}",
                         row=this_row,
                         column=4)

        self._draw_label(f"Driver's License: {party.drivers_license}")
        this_row = self.row_number - 1
        self._draw_label(label_text=f"State: {party.drivers_license_state or ''}",
                         row=this_row,
                         column=3)
        self._draw_label(f"Employer: {party.employer}")
        self._draw_label(f"Emp Address: {str(party.employer_address) or ''}")

    def generate(self) -> Canvas:
        self._draw_labels()
        self.pdf.showPage()
        self.pdf.save()
        return self.pdf
