import logging
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from faker import Faker
from cases.models import Incident
from cases.tests.factories import (OfficerFactory,
                                   OffenseFactory,
                                   IncidentFactory,
                                   AddressFactory,
                                   UserFactory)
from cases.tests.utils import IncidentDataFaker, generate_jwt_for_tests
from cases.constants import (VICTIM, SUSPECT)
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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_partial_update_incident(self):
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

    def test_put_update_incident_returns_not_allowed(self):
        location = AddressFactory()
        offense = OffenseFactory()
        incident = IncidentFactory(location=location)
        incident.offenses.add(offense)
        url = reverse("incident-detail", kwargs={'pk': incident.id})
        data = {'stolen_amount': 125.00}
        reponse = self.client.post(url, data=data)
        self.assertEqual(reponse.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_incident(self):
        location = AddressFactory()
        offense = OffenseFactory()
        incident = IncidentFactory(location=location)
        inc_number = incident.incident_number
        incident.offenses.add(offense)
        url = reverse("incident-detail", kwargs={'pk': incident.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        inc = Incident.objects.filter(incident_number=inc_number).first()
        self.assertIsNone(inc)


class VictimTestCase(APITestCase):
    def setUp(self):
        self.user = OfficerFactory().user
        token = generate_jwt_for_tests(self.user)
        self.client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')
        self.faker = IncidentDataFaker(faker=Faker())

    def test_create_victim(self):
        incident = IncidentFactory()
        data = self.faker.generate_involved_party(party_type=VICTIM,
                                                  incident=incident)
        logger.debug(f"Victim data: {data}")
        url = reverse("victim-list", kwargs={'incidents_pk': str(incident.pk)})
        response = self.client.post(url, data=data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
