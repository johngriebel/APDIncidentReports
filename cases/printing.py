import math
from django.utils import timezone
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from textwrap import wrap
from cases.models import Incident, Offense, IncidentInvolvedParty
from cases.constants import (VICTIM,
                             SUSPECT,
                             PAGE_WIDTH,
                             PAGE_CENTER_X,
                             COLUMN_X_POSITION_MAP,
                             LEFT_ALIGN_X,
                             TOP_ALIGN_Y,
                             MAX_TEXT_LINE_WIDTH,
                             MIN_Y_POSITION,
                             COLOR_RGB_VALUES)


# Note: there is some hard coded stuff in here to make the printing example for one specific report
# look nice. It needs to be actually fixed.
class IncidentReportPDFGenerator:
    def __init__(self, file_name: str, incident_id: int, default_font_size: int = 12) -> None:
        """
        Given an Incident ID, this class handles the generation of a PDF document according
        to specifications provided by APD
        :param file_name: The name given to the generated PDF.
        :param incident_id: Integer ID of the incident to generate a PDF for.
        :param default_font_size: Font size, in points, to be used when nothing else is specified.
        """
        self.incident = Incident.objects.get(id=incident_id)
        self.pdf = Canvas(filename=file_name)
        self.row_number = 1
        self.page_number = 1
        self.default_font_size = default_font_size
        self.draw_func = self.pdf.drawString

    def _set_font_color_rgb(self, red: int, green: int, blue: int) -> None:
        """
        Simply a wrapper around the setFillColorRGB method to allow use of the
        more commonly know 0 - 255 scale instead of 0 - 1.
        :param red: Integer between 0 and 255.
        :param green: Integer between 0 and 255.
        :param blue: Integer between 0 and 255.
        :return: None
        """
        red_val = red / 256
        green_val = green / 256
        blue_val = blue / 256
        self.pdf.setFillColorRGB(red_val, green_val, blue_val)

    def _reset_font_color(self) -> None:
        """Convenience method for setting the font color to black."""
        self._set_font_color_rgb(red=0, green=0, blue=0)

    def _determine_y_position(self, row: int) -> int:
        """
        Given the current row being drawn in the PDF document, determine
        the integer value corresponding to the Y coordinate of said row.
        If necessary, begin a new page.
        :param row: Integer specifying which row is being drawn.
        :return: The Y position that the canvas should draw the provided row at.
        """
        # Can this line fit on the current page?
        y_position = TOP_ALIGN_Y - ((row - 1) * self.default_font_size)
        if y_position < MIN_Y_POSITION:
            self._add_new_page()
            row = self.row_number
            y_position = TOP_ALIGN_Y - ((row - 1) * self.default_font_size)

        return y_position

    def _determine_x_position(self, column: int, centered: bool = False) -> int:
        """
        Given a column number (as defined in cases/constants.py), determine the integer
        value corresponding to the appropriate X coordinate on the canvas.
        :param column: Integer specifying the desired column.
        :param centered: If true, any value for `column` will be overriden, and PAGE_CENTER_X will be used.
        :return: The X position that the canvas should move itself to.
        """
        if column not in COLUMN_X_POSITION_MAP:
            x_position = LEFT_ALIGN_X
        else:
            x_position = COLUMN_X_POSITION_MAP[column]

        if centered:
            x_position = PAGE_CENTER_X
            self.draw_func = self.pdf.drawCentredString

        return x_position

    def _draw_label(self, label: str, data: str = None, row: int = None,
                    column: int = 0, centered: bool = False, color: str = "blue") -> None:
        """
        Draws a label and possibly associated data on the canvas.
        :param label: Text to be displayed by the label itself.
        :param data: Information that should follow the label.
        :param row: Which row in the canvas the label should be drawn at.
        :param column: Which column in the canvas the label should be drawn at.
        :param centered: Dictates if the label should be center aligned. Overrides column.
        :param color: A string defining what color the label's text should be.
                      See constants.py::COLOR_RGB_VALUES for choices.
        :return: None
        """

        if row is None:
            row = self.row_number
            self.row_number += 1

        y_position = self._determine_y_position(row=row)
        x_position = self._determine_x_position(column=column, centered=centered)

        # Why tf is this done this way?
        red, green, blue = COLOR_RGB_VALUES.get(color, (0, 0, 0,))
        self._set_font_color_rgb(red, green, blue)
        self.draw_func(x_position, y_position, label)

        if data is not None:
            label_width = stringWidth(label,
                                      fontName="Courier",
                                      fontSize=10)
            data_x_pos = x_position + label_width
            self._reset_font_color()
            self.pdf.drawString(data_x_pos, y_position, f" {data}")

        self._reset_font_color()

    @property
    def current_y_position(self) -> int:
        """Get the current Y coordinate on the canvas."""
        return TOP_ALIGN_Y - ((self.row_number - 1) * self.default_font_size)

    def _draw_page_header(self) -> None:
        """Draws header information that will be the same for every page of a given incident report."""
        self.pdf.setFont("Courier", 10)
        self._draw_label("Printed By:",
                         color="blue")
        today = timezone.now().date()
        us_format_date_string = today.strftime("%m/%d/%Y")
        self._draw_label(label="Print Date:",
                         data=us_format_date_string)
        self.row_number += 1
        self._draw_label("ATLANTA POLICE DEPARTMENT",
                         centered=True)
        self._draw_label("Offense Report",
                         centered=True)
        self._draw_label(f"INCIDENT NUMBER: {self.incident.incident_number}",
                         centered=True)
        self.pdf.drawString(525, TOP_ALIGN_Y, f"PAGE: {self.page_number}")

    def _draw_incident_information(self) -> None:
        """Draws the general incident information such as time of occurrence, location, and so on."""
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

    def _draw_offenses(self) -> None:
        """Draws offenses being reported as part of the incident."""
        self._draw_label("------------ OFFENSES ------------",
                         centered=True,
                         color="red")

        for offense in self.incident.offenses.all():
            self._draw_offense(offense=offense)
            self.row_number += 1

        self.row_number += 2

    def _draw_attachments(self) -> None:
        """Draws a list of attachments, e.g. photos or audio files, associated with the incident."""
        self._draw_label("------------ ATTACHMENTS ------------",
                         centered=True,
                         color="red")
        self.row_number += 2

    def _draw_victims(self, victims) -> None:
        """
        Draws IncidentInvoledParty information for all parties reporting to be a victim of the incident.
        :param victims: A QuerySet of IncidentInvolvedParty objects where party_type = VICTIM.
        :return: None
        """
        self._draw_label("------------ VICTIM ------------",
                         centered=True,
                         color="red")

        victim_count = 1
        for victim in victims:
            self._draw_party(count=victim_count,
                             party=victim)
            victim_count += 1

        self.row_number += 2

    def _draw_suspects(self, suspects) -> None:
        """
        Draws IncidentInvoledParty information for all parties reported as suspects in the incident.
        :param suspects: A QuerySet of IncidentInvolvedParty objects where party_type = SUSPECT.
        :return: None
        """
        self._draw_label("------------ SUSPECT ------------",
                         centered=True,
                         color="red")

        suspect_count = 1
        for suspect in suspects:
            self._draw_party(count=suspect_count,
                             party=suspect)
            suspect_count += 1
        self.row_number += 2

    def _draw_parties(self) -> None:
        """Draws information for all IncidentInvolvedParty objects related to the incident."""
        all_parties = self.incident.incidentinvolvedparty_set.all()

        victims = all_parties.filter(party_type=VICTIM)
        self._draw_victims(victims=victims)

        suspects = all_parties.filter(party_type=SUSPECT)
        self._draw_suspects(suspects=suspects)

    def _draw_labels(self) -> None:
        """Perhaps misnamed, this method essentially draws the entire document."""
        self._draw_page_header()
        self.row_number += 1
        self._draw_incident_information()
        self._draw_offenses()
        self._draw_attachments()
        self._draw_parties()
        self._draw_narrative()
        self.row_number += 4
        self._draw_signature_lines()

    def _draw_offense(self, offense: Offense) -> None:
        """
        Draws information regarding one specific offense being reported as part of the incident.
        :param offense: Offense object to be drawn
        :return: None
        """
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

    def _draw_party(self, count: int, party: IncidentInvolvedParty) -> None:
        """
        Draws information regarding one specific party involved in the incident.
        :param count: Sequence number of the specified partym given its type, e.g. Victim #3
        :param party: The party about which to draw information
        :return: None
        """
        self._draw_label(label=f"{party.party_type.title()} #{count}",
                         color="red")
        if party.party_type == SUSPECT:
            self._draw_label("Date and Time Last Updated:")
        self._draw_label("Name:",
                         data=party.name)
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
                              x_position: int = LEFT_ALIGN_X,
                              y_position: int = None) -> None:
        """
        Performs the necessary string manipulation in order to
        properly draw a multi-line string on the canvas.
        :param lines: A list of strings where each element in the list corresponds to a line to be drawn.
        :param x_position: X coordinate at which the block of text should begin.
        :param y_position: Y coordinate at which the block of text should begin.
        :return: None
        """
        if y_position is None:
            y_position = self.current_y_position

        wrapped_statement = "\n".join(lines)
        text = self.pdf.beginText(x_position, y_position)
        text.textLines(wrapped_statement)
        self.pdf.drawText(text)

    def _add_new_page(self) -> None:
        """Simply adds a new page to the document, does the necessary bookkeeping,
           and draws header information on the new page.
        """
        self.pdf.showPage()
        self.page_number += 1
        self.row_number = 1
        self._draw_page_header()

    def _draw_narrative(self) -> None:
        """Draws the narrative, i.e. statement of events given by the victim."""
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

    def _draw_signature_lines(self) -> None:
        """Draws all necessary labels and lines for legal signatures required by APD."""
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
        """
        Makes the necessary calls to draw all information related to the incident.
        :return: A Canvas object, which is essentially the PDF itself.
        """
        self._draw_labels()
        self.pdf.showPage()
        self.pdf.save()
        return self.pdf
