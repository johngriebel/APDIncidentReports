import logging
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from faker import Faker
from djmoney.money import Money
from cases.tests.factories import (OfficerFactory,
                                   OffenseFactory,
                                   IncidentFactory,
                                   AddressFactory)
from cases.tests.utils import IncidentDataFaker
logger = logging.getLogger('cases')


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
        offenses = [OffenseFactory().id,
                    OffenseFactory().id]

        data = {'incident_number': "FOO123",
                'report_datetime': report_dt,
                'reporting_officer': {'officer_number': reporting_officer.officer_number},
                'investigating_officer': {'officer_number': reporting_officer.officer_number},
                'officer_making_report': {'officer_number': reporting_officer.officer_number},
                'reviewed_by_officer': {'officer_number': supervisor.officer_number},
                'supervisor': {'officer_number': supervisor.officer_number},
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
        logger.debug(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_incident(self):
        location = AddressFactory()
        offense = OffenseFactory()
        incident = IncidentFactory(location=location)
        incident.offenses.add(offense)
        url = reverse("incident-detail", kwargs={'pk': incident.id})
        data = {'location': {'street_number': location.street_number,
                             'route': location.route,
                             'city': location.city.name,
                             'state': "GA",
                             'postal_code': location.postal_code}}
        response = self.client.patch(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        incident.refresh_from_db()
        self.assertEqual(incident.location.city.state.abbreviation, "GA")


