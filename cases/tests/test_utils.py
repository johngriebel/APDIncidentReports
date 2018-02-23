import random
from datetime import datetime
from django.test import TestCase
from cases.utils import convert_date_string_to_object


class UtilsTestCase(TestCase):

    def test_dashed_date_no_time(self):
        year = random.randint(1900, 2018)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        date_string = f"{year}-{month}-{day}"
        converted = convert_date_string_to_object(date_string=date_string)
        expected = datetime(year=year,
                            month=month,
                            day=day)
        self.assertEqual(converted, expected)

    def test_slashed_date_no_time(self):
        year = random.randint(1900, 2018)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        date_string = f"{month}/{day}/{year}"
        converted = convert_date_string_to_object(date_string=date_string)
        expected = datetime(year=year,
                            month=month,
                            day=day)
        self.assertEqual(converted, expected)

    def test_dashed_date_with_time(self):
        year = random.randint(1900, 2018)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        hour = random.randint(0, 23)
        minute = random.randint(0,59)
        date_string = f"{year}-{month}-{day} {hour}:{minute}"
        converted = convert_date_string_to_object(date_string=date_string)
        expected = datetime(year=year,
                            month=month,
                            day=day,
                            hour=hour,
                            minute=minute)
        self.assertEqual(converted, expected)
