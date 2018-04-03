import random
import pytz
from django.conf import settings
from datetime import datetime
from django.utils import timezone
from django.utils.datastructures import MultiValueDict
from django.test import TestCase
from cases.search import cleanse_filter_key, cleanse_value


class SearchTestCase(TestCase):

    def test_cleanse_filter_key_min(self):
        key = "foo_min"
        expected = "foo__gte"
        result = cleanse_filter_key(key)
        self.assertEqual(result, expected)

    def test_cleanse_filter_key_max(self):
        key = "foo_max"
        expected = "foo__lte"
        result = cleanse_filter_key(key)
        self.assertEqual(result, expected)

    def test_cleanse_filter_key_earliest(self):
        key = "earliest_foo"
        expected = "earliest_foo__gte"
        result = cleanse_filter_key(key)
        self.assertEqual(result, expected)

    def test_cleanse_filter_key_latest(self):
        key = "latest_foo"
        expected = "latest_foo__lte"
        result = cleanse_filter_key(key)
        self.assertEqual(result, expected)

    def test_cleanse_filter_key_offenses(self):
        key = "offenses"
        expected = "offenses__id__in"
        result = cleanse_filter_key(key)
        self.assertEqual(result, expected)

    def test_cleanse_filter_key_generic(self):
        key = "foo"
        expected = "foo__icontains"
        result = cleanse_filter_key(key)
        self.assertEqual(result, expected)

    def test_cleanse_filter_key_reporting_officer(self):
        key = "reporting_officer"
        expected = "reporting_officer__id"
        result = cleanse_filter_key(key)
        self.assertEqual(result, expected)

    def test_cleanse_value_datetime(self):
        year = random.randint(1900, 2018)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        date_string = f"{year}-{month}-{day} {hour}:{minute}"
        key = "foo_date"
        data = {key: date_string}
        expected = datetime(year=year,
                            month=month,
                            day=day,
                            hour=hour,
                            minute=minute,
                            tzinfo=pytz.timezone(settings.TIME_ZONE))
        result = cleanse_value(key, data)
        self.assertEqual(result, expected)

    def test_cleanse_value_offenses(self):
        data = MultiValueDict({'offenses': ["1", "2", "3"]})
        expected = ["1", "2", "3"]
        key = "offenses"
        result = cleanse_value(key, data)
        self.assertListEqual(result, expected)

    def test_cleans_value_generic(self):
        data = {'my_key': 14}
        key = 'my_key'
        result = cleanse_value(key, data)
        expected = 14
        self.assertEqual(result, expected)
