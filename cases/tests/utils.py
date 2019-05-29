import os
import random
import logging
from typing import (Dict,
                    List,
                    Any,
                    Tuple)
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from rest_framework_jwt.settings import api_settings
from faker import Faker
from cases.models import Incident, Officer
from cases.tests.factories import (IncidentFactory,
                                   OfficerFactory,
                                   OffenseFactory)
from cases.constants import (SHIFT_CHOICES,
                             MALE, FEMALE, RACE_CHOICES,
                             HAIR_COLOR_CHOICES,
                             EYE_COLOR_CHOICES,
                             STATE_CHOICES)


logger = logging.getLogger('cases')
User = get_user_model()
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER


def _get_db_vals_for_choice_list(choices: List[Tuple]) -> List[str]:
    return [c[0] for c in choices]

def generate_jwt_for_tests(user: User):
    payload = jwt_payload_handler(user)
    return jwt_encode_handler(payload)


class IncidentDataFaker:
    def __init__(self, faker: Faker) -> None:
        self.fake = faker

    def _maybe(self, to_return: Any, p_null: float=0.5) -> Any:
        decider = random.random()
        if decider > p_null:
            return to_return
        else:
            return None

    def generate_date_time_dict(self) -> Dict[str, str]:
        date_time_obj = self.fake.date_time_this_month()
        date_time_dict = {'date': date_time_obj.date().strftime("%Y-%m-%d"),
                          'time': date_time_obj.date().strftime("%H:%M")}

        return date_time_dict

    def generate_address(self) -> Dict[str, str]:
        location = {'street_number': self.fake.building_number(),
                    'route': self.fake.street_name(),
                    'city': self.fake.city(),
                    'postal_code': self.fake.postalcode(),
                    'state': self.fake.state_abbr()[:5]}
        return location

    def generate_beat(self) -> int:
        return self.fake.random_int(min=1, max=1000)

    def generate_shift(self) -> str:
        shifts = [choice[0] for choice in SHIFT_CHOICES
                  if choice[0]]
        return random.choice(shifts)

    def generate_currency(self) -> int:
        return random.randint(0, 100000000)

    def generate_narrative(self) -> str:
        return self.fake.paragraph()

    def generate_involved_party(self, party_type: str,
                                incident: Incident,
                                officer_signed: Officer) -> Dict:

        party_data = {'first_name': self.fake.first_name(),
                      'last_name': self.fake.last_name(),
                      'incident': incident.id,
                      'officer_signed': officer_signed.id,
                      'party_type': party_type,
                      'juvenile': self.fake.pybool(),
                      'home_address': self._maybe(to_return=self.generate_address()),
                      'date_of_birth': self.fake.past_date(),
                      'sex': random.choice([MALE, FEMALE]),
                      'race': random.choice(_get_db_vals_for_choice_list(choices=RACE_CHOICES)),
                      'height': random.randint(24, 90),
                      'weight': random.randint(2, 400),
                      'hair_color': random.choice(_get_db_vals_for_choice_list(choices=HAIR_COLOR_CHOICES)),
                      'eye_color': random.choice(_get_db_vals_for_choice_list(choices=EYE_COLOR_CHOICES)),
                      'build': self.fake.text(max_nb_chars=25),
                      'tattoos': self.fake.text(max_nb_chars=30),
                      'scars': self._maybe(to_return=self.fake.text(max_nb_chars=30)),
                      'hairstyle': self._maybe(to_return=self.fake.text(max_nb_chars=30))}

        drivers_license = self._maybe(to_return=self.fake.text(max_nb_chars=100))

        if drivers_license:
            dl_state = random.choice(_get_db_vals_for_choice_list(choices=STATE_CHOICES))
            party_data['drivers_license'] = drivers_license
            party_data['drivers_license_state'] = dl_state

        employer = self._maybe(to_return=self.fake.company())

        if employer:
            employer_address = self.generate_address()
            party_data['employer'] = employer
            party_data['employer_address'] = employer_address

        return party_data

    def generate_entire_incident_data(self) -> Dict:
        """
        Combines all the various other generation methods defined on the class
        to generate a complete dict defining an Incident object.
        :return: Python dict containing randomized incident data
        """
        supervisor = OfficerFactory()
        reporting_officer = OfficerFactory(supervisor=supervisor)
        data = {'incident_number': self.fake.pyint(),
                'report_datetime': self.generate_date_time_dict(),
                'reporting_officer': reporting_officer.id,
                'investigating_officer': reporting_officer.id,
                'officer_making_report': reporting_officer.id,
                'reviewed_by_officer': supervisor.id,
                'supervisor': supervisor.id,
                'earliest_occurrence_datetime': self.generate_date_time_dict(),
                'latest_occurrence_datetime': self.generate_date_time_dict(),
                'location': self.generate_address(),
                'beat': self.generate_beat(),
                'shift': self.generate_shift(),
                'stolen_amount': self.generate_currency(),
                'damaged_amount': self.generate_currency(),
                'offenses': [OffenseFactory().id, OffenseFactory().id],
                'narrative': self.generate_narrative()}
        return data


def generate_random_file_content(suffix: str,
                                 num_kb: int = 2,
                                 base_path: str = None) -> SimpleUploadedFile:
    fname = "test_file_" + str(suffix)
    full_path = os.path.join(base_path or "/tmp/", fname)
    if os.path.isfile(full_path):
        os.remove(full_path)
    fout = open(full_path, "wb")
    fout.write(os.urandom(1024 * num_kb))
    fout.close()
    fin = open(full_path, "rb")
    uploaded_file = SimpleUploadedFile(fname,
                                       fin.read(),
                                       content_type="multipart/form-data")
    return uploaded_file
