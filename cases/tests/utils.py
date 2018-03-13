import random
from typing import Dict
from faker import Faker
from cases.constants import SHIFT_CHOICES


class IncidentDataFaker:
    def __init__(self, faker: Faker) -> None:
        self.fake = faker

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
                    'state': self.fake.state(),
                    'state_abbreviation': self.fake.state_abbr()}
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
