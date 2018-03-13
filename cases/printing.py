import math
from django.utils import timezone
from django.http import HttpResponse
from reportlab.pdfgen.canvas import Canvas
from reportlab.rl_config import defaultPageSize
from reportlab.pdfbase.pdfmetrics import stringWidth
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
# i.e. the lowest point on a page that we want a line of text to be drawn
MIN_Y_POSITION = PAGE_HEIGHT - TOP_ALIGN_Y
COLOR_RGB_VALUES = {'red': (255, 0, 0),
                    'blue': (0, 38, 150),
                    'black': (0, 0, 0)}


# Note: there is some hard coded stuff in here to make the printing example for one specific report
# look nice. It needs to be actually fixed.
class IncidentReportPDFGenerator:
    def __init__(self, response: HttpResponse, incident_id: int):
        self.response = response
        self.incident = Incident.objects.get(id=incident_id)
        self.pdf = Canvas(response)
        self.row_number = 1
        self.page_number = 1

    def _set_font_color_rgb(self, red: int, green: int, blue: int):
        red_val = red / 256
        green_val = green / 256
        blue_val = blue / 256
        self.pdf.setFillColorRGB(red_val, green_val, blue_val)

    def _draw_label(self, label: str, data: str=None, row: int=None,
                    column: int=0, centered=False, color: str="blue") -> None:
        """
        Draws a standard (i.e. evenly spaced rows) label on the PDF
        :param row_number: The row, one indexed, that the label should be drawn on.
        :param label: The text the label should disply.
        :return: None
        """
        draw_func = self.pdf.drawString
        if row is None:
            row = self.row_number
            self.row_number += 1

        # Can this line fit on the current page?
        y_position = TOP_ALIGN_Y - ((row - 1) * 12)
        print((y_position, MIN_Y_POSITION))
        if y_position < MIN_Y_POSITION:
            self._add_new_page()
            row = self.row_number
            y_position = TOP_ALIGN_Y - ((row - 1) * 12)

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

        red, green, blue = COLOR_RGB_VALUES.get(color, (0, 0, 0,))
        self._set_font_color_rgb(red, green, blue)
        draw_func(x_position, y_position, label)

        if data is not None:
            label_width = stringWidth(label,
                                      fontName="Courier",
                                      fontSize=10)
            data_x_pos = x_position + label_width
            self._set_font_color_rgb(0, 0, 0)
            self.pdf.drawString(data_x_pos, y_position, f" {data}")

        self._set_font_color_rgb(0, 0, 0)


    @property
    def current_y_position(self):
        return TOP_ALIGN_Y - ((self.row_number - 1) * 12)

    def _draw_page_header(self):
        self.pdf.setFont("Courier", 10)
        self._draw_label("Printed By:",
                         color="blue")
        today = timezone.now().date()
        us_format_date_string = today.strftime("%m/%d/%Y")
        self._draw_label(label="Print Date:",
                         data=us_format_date_string)
        self.row_number += 1
        self._draw_label("ATLANTA POLICE DEPARTMENT",
                         centered=True,
                         color="blue")
        self._draw_label("Offense Report",
                         centered=True,
                         color="blue")
        self._draw_label(f"INCIDENT NUMBER: {self.incident.incident_number}",
                         centered=True,
                         color="blue")
        self.pdf.drawString(525, TOP_ALIGN_Y, f"PAGE: {self.page_number}")

    def _draw_labels(self):
        self._draw_page_header()
        self.row_number += 1
        self._draw_label("------------ INCIDENT INFORMATION ------------",
                         centered=True,
                         color="red")
        self.row_number += 1
        self._draw_label(label="Report Date:",
                         data=self.incident.report_datetime.date())
        self._draw_label(label="Time:",
                         data=self.incident.report_datetime.time(),
                         row=self.row_number - 1,
                         column=3)
        self._draw_label(label="Reporting Officer:",
                         data=self.incident.reporting_officer)
        self._draw_label(label="Reviewed by Officer:", 
                         data=self.incident.reviewed_by_officer)
        self._draw_label(label="Investigating Officer:", 
                         data=self.incident.investigating_officer)
        self._draw_label(label="Officer Making Rpt", 
                         data=self.incident.officer_making_report)
        self._draw_label(label="Supervisor:", 
                         data=self.incident.supervisor)
        self._draw_label(label="Occur/Earliest Date / Time:", 
                         data=self.incident.earliest_occurrence_datetime)
        self._draw_label(label="Location:", 
                         data=str(self.incident.location))
        self._draw_label(label="Latest Poss Date / Time:",
                         data=self.incident.latest_occurrence_datetime)
        self._draw_label(label="Assoc Offense #:")
        self._draw_label(label="RD:")
        self._draw_label(label="Beat:",
                         data=self.incident.beat,
                         row=self.row_number - 1,
                         column=2)
        self._draw_label(label="Shift:",
                         data=self.incident.shift,
                         row=self.row_number - 1,
                         column=4)
        self._draw_label(label="Damaged Amount:",
                         data=self.incident.damaged_amount)
        self._draw_label(label=f"Stolen Amount:",
                         data=self.incident.stolen_amount,
                         row=self.row_number - 1,
                         column=2)
        self._draw_label("Disposition:")
        self._draw_label(label="Dispo Date:",
                         row=self.row_number - 1,
                         column=2)
        self.row_number += 2
        self._draw_label("------------ OFFENSES ------------",
                         centered=True,
                         color="red")
        for offense in self.incident.offenses.all():
            self._draw_offense(offense=offense)
            self.row_number += 1

        self.row_number += 2
        self._draw_label("------------ ATTACHMENTS ------------",
                         centered=True,
                         color="red")
        self.row_number += 2
        self._draw_label("------------ VICTIM ------------",
                         centered=True,
                         color="red")
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
                         centered=True,
                         color="red")

        suspect_count = 1
        for suspect in suspects:
            self._draw_party(count=suspect_count,
                             party=suspect)
            suspect_count += 1
        self.row_number += 2

        self._draw_narrative()
        self.row_number += 4

        self._draw_signature_lines()

    def _draw_offense(self, offense: Offense):
        self._draw_label(label="Offense:",
                         data=f"{offense.ucr_name_classification} - "
                              f"{offense.ucr_subclass_description}")
        self._draw_label(label=f"GCIC:",
                         data=offense.gcic_code,
                         row=self.row_number,
                         column=1)
        self._draw_label(label=f"UCR:",
                         data=offense.ucr_code,
                         row=self.row_number,
                         column=3)

    def _draw_party(self, count: int, party: IncidentInvolvedParty):
        self._draw_label(label=f"{party.party_type.title()} #{count}",
                         color="red")
        if party.party_type == SUSPECT:
            self._draw_label("Date and Time Last Updated:")
        self._draw_label("Name:")
        self._draw_label(label="Juvenile?",
                         data=str(party.juvenile))
        self._draw_label(label="Home Address:",
                         data=str(party.home_address) or '')
        self._draw_label(label="SSN:",
                         data=party.social_security_number)
        this_row = self.row_number - 1
        self._draw_label(label="DOB:",
                         data=party.date_of_birth or '',
                         row=this_row,
                         column=2)
        self._draw_label(label="Sex:",
                         data=party.sex or '',
                         row=this_row,
                         column=3)
        self._draw_label(label="Race:",
                         data=party.race or '',
                         row=this_row,
                         column=4)
        self._draw_label(label="Hgt:",
                         data=str(party.height))

        this_row = self.row_number - 1
        self._draw_label(label="Wgt:",
                         data=str(party.weight),
                         row=this_row,
                         column=2)
        self._draw_label(label="Hair:",
                         data=party.hair_color,
                         row=this_row,
                         column=3)
        self._draw_label(label="Eye:",
                         data=party.eye_color,
                         row=this_row,
                         column=4)

        self._draw_label(label="Driver's License:",
                         data=party.drivers_license)
        this_row = self.row_number - 1
        self._draw_label(label="State:",
                         data=party.drivers_license_state or '',
                         row=this_row,
                         column=3)
        self._draw_label("Employer:",
                         data=party.employer)
        self._draw_label("Emp Address:",
                         data=str(party.employer_address) or '')

    def _wrap_and_write_lines(self, lines: list,
                              x_position: int=LEFT_ALIGN_X,
                              y_position: int=None):
        if y_position is None:
            y_position = self.current_y_position

        wrapped_statement = "\n".join(lines)
        text = self.pdf.beginText(x_position, y_position)
        text.textLines(wrapped_statement)
        self.pdf.drawText(text)

    def _add_new_page(self):
        self.pdf.showPage()
        self.page_number += 1
        self.row_number = 1
        self._draw_page_header()

    def _draw_narrative(self):
        self._draw_label(label="Incident Narrative",
                         centered=True,
                         color="red")
        lines = wrap(self.incident.narrative,
                     MAX_TEXT_LINE_WIDTH)
        # Each line has length 12
        narrative_final_y = self.current_y_position - (len(lines) * 12)
        if narrative_final_y < MIN_Y_POSITION:
            # Assuming that a narrative will fit on no more than two pages is a bit brittle,
            # But it is very unlikely that a narrative will require so much space.
            num_lines_fit_current_page = math.floor((self.current_y_position - MIN_Y_POSITION) / 12)
            this_page_lines = lines[:num_lines_fit_current_page]
            self._wrap_and_write_lines(lines=this_page_lines)
            self._add_new_page()
            next_page_lines = lines[num_lines_fit_current_page:]
            self.row_number += 1
            self._draw_label(label="Incident Narrative",
                             centered=True,
                             color="red")
            self._wrap_and_write_lines(lines=next_page_lines)
            self.row_number += len(next_page_lines)
        else:
            self._wrap_and_write_lines(lines)
            self.row_number += len(lines)

    def _draw_signature_lines(self):
        self._add_new_page()
        self.row_number += 2
        reviewed_str = (f"OFFENSE REPORT REVIEWED BY {self.incident.reviewed_by_officer} "
                        f"ON {self.incident.reviewed_datetime}")
        reviewed_length = stringWidth(reviewed_str,
                                      fontName="Courier",
                                      fontSize=10)
        review_x_pos = PAGE_WIDTH - 40 - reviewed_length
        review_line = self.pdf.beginPath()
        review_line.moveTo(review_x_pos, self.current_y_position + 15)
        review_line.lineTo(review_x_pos + reviewed_length, self.current_y_position + 15)
        review_line.close()
        self.pdf.drawPath(review_line)
        self.pdf.drawString(review_x_pos, self.current_y_position, reviewed_str)
        self.row_number += 4
        approved_str = (f"OFFENSE REPORT APPROVED BY {self.incident.supervisor} "
                        f"ON {self.incident.reviewed_datetime}")
        approved_length = stringWidth(approved_str,
                                      fontName="Courier",
                                      fontSize=10)
        approved_x_pos = PAGE_WIDTH - 40 - approved_length
        approved_line = self.pdf.beginPath()
        approved_line.moveTo(approved_x_pos, self.current_y_position + 15)
        approved_line.lineTo(approved_x_pos + approved_length, self.current_y_position + 15)
        approved_line.close()
        self.pdf.drawPath(approved_line)
        self.pdf.drawString(approved_x_pos, self.current_y_position, approved_str)

    def generate(self) -> Canvas:
        self._draw_labels()
        self.pdf.showPage()
        self.pdf.save()
        return self.pdf
