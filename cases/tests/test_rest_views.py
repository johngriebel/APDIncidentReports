from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from faker import Faker
from cases.tests.factories import OfficerFactory, OffenseFactory
from cases.tests.utils import IncidentDataFaker


class IncidentsTestCase(APITestCase):
    def setUp(self):
        self.faker = IncidentDataFaker(faker=Faker())

    def test_create_incident(self):
        url = reverse("incident-list")
        report_dt = self.faker.generate_date_time_dict()
        supervisor = OfficerFactory()
        reporting_officer = OfficerFactory(supervisor=supervisor)

        earliest_dt = self.faker.generate_date_time_dict()
        latest_dt = self.faker.generate_date_time_dict()
        location = self.faker.generate_address()
        offenses = [{'id': OffenseFactory().id},
                    {'id': OffenseFactory().id}]

        data = {'incident_number': "FOO123",
                'report_datetime': report_dt,
                'reporting_officer': {'id': reporting_officer.id},
                'investigating_officer': {'id': reporting_officer.id},
                'officer_making_report': {'id': reporting_officer.id},
                'reviewed_by_officer': {'id': supervisor.id},
                'supervisor': {'id': supervisor.id},
                'earliest_occurrence_datetime': earliest_dt,
                'latest_occurrence_datetime': latest_dt,
                'location': location,
                'beat': self.faker.generate_beat(),
                'shift': self.faker.generate_shift(),
                **self.faker.generate_currency(prefix="damaged"),
                **self.faker.generate_currency(prefix="stolen"),
                'offenses': offenses,
                'narrative': self.faker.generate_narrative()}
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

