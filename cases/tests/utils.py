import random
import logging
from typing import Dict, Optional, Any
from django.contrib.auth import get_user_model
from rest_framework_jwt.settings import api_settings
from faker import Faker
from cases.models import Incident, Officer
from cases.tests.factories import (IncidentFactory,
                                   OfficerFactory,
                                   AddressFactory)
from cases.constants import (SHIFT_CHOICES,
                             MALE, FEMALE, RACE_CHOICES,
                             HAIR_COLOR_CHOICES,
                             EYE_COLOR_CHOICES,
                             STATES)
logger = logging.getLogger('cases')
User = get_user_model()
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER


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

    def generate_currency(self, prefix: str) -> Dict:
        return {f'{prefix}_amount': random.randint(0, 1000000) / 100,
                f'{prefix}_amount_currency': "USD"}

    def generate_narrative(self) -> str:
        return self.fake.paragraph()

    def generate_involved_party(self, *, party_type: str,
                                incident: Optional[Incident]=None,
                                officer_signed: Optional[Officer]=None) -> Dict:
        party_data = {'first_name': self.fake.first_name(),
                      'last_name': self.fake.last_name(),
                      'incident': incident.id if incident
                                              else IncidentFactory().id,
                      'officer_signed': officer_signed.id if officer_signed
                                                          else OfficerFactory().id,
                      'party_type': party_type,
                      'juvenile': self.fake.pybool(),
                      'home_address': self._maybe(to_return=self.generate_address()),
                      'date_of_birth': self.fake.past_date(),
                      'sex': random.choice([MALE, FEMALE]),
                      'race': random.choice([r[0] for r in RACE_CHOICES]),
                      'height': random.randint(24, 90),
                      'weight': random.randint(2, 400),
                      'hair_color': random.choice([h[0] for h in HAIR_COLOR_CHOICES]),
                      'eye_color': random.choice([e[0] for e in EYE_COLOR_CHOICES]),
                      'build': self.fake.text(max_nb_chars=25),
                      'tattoos': self.fake.text(max_nb_chars=30),
                      'scars': self._maybe(to_return=self.fake.text(max_nb_chars=30)),
                      'hairstyle': self._maybe(to_return=self.fake.text(max_nb_chars=30))}

        drivers_license = self._maybe(to_return=self.fake.text(max_nb_chars=100))
        if drivers_license:
            dl_state = random.choice([state for state in STATES])
            party_data['drivers_license'] = drivers_license
            party_data['drivers_license_state'] = dl_state

        employer = self._maybe(to_return=self.fake.company())
        if employer:
            employer_address = self.generate_address()
            party_data['employer'] = employer
            party_data['employer_address'] = employer_address

        return party_data
