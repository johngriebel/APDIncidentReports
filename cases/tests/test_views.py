import logging
import shutil
from pathlib import Path
from django.urls import reverse
from django.conf import settings
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from faker import Faker
from cases.models import (Incident, IncidentInvolvedParty,
                          IncidentFile)
from cases.tests.factories import (OfficerFactory,
                                   OffenseFactory,
                                   IncidentFactory,
                                   AddressFactory,
                                   VictimFactory,
                                   SuspectFactory)
from cases.tests.utils import (IncidentDataFaker,
                               generate_jwt_for_tests,
                               generate_random_file_content)
from cases.constants import (VICTIM, SUSPECT)
logger = logging.getLogger('cases')


class JWTAuthAPIBaseTestCase(APITestCase):
    def setUp(self):
        self.user = OfficerFactory().user
        token = generate_jwt_for_tests(self.user)
        self.client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')
        self.faker = IncidentDataFaker(faker=Faker())


class IncidentsTestCase(JWTAuthAPIBaseTestCase):

    fixtures = ["states.json"]

    def test_create_incident(self):
        url = reverse("incident-list")
        data = self.faker.generate_entire_incident_data()

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
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

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


class VictimTestCase(JWTAuthAPIBaseTestCase):

    fixtures = ["states.json"]

    def test_create_victim(self):
        incident = IncidentFactory()
        data = self.faker.generate_involved_party(party_type=VICTIM,
                                                  incident=incident,
                                                  officer_signed=OfficerFactory())
        url = reverse("victim-list", kwargs={'incidents_pk': str(incident.pk)})
        response = self.client.post(url, data=data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        victims = IncidentInvolvedParty.objects.filter(incident=incident,
                                                       party_type=VICTIM)
        self.assertEqual(victims.count(), 1)
        self.assertEqual(victims.first().first_name, data['first_name'])
        self.assertEqual(victims.first().last_name, data['last_name'])

    def test_partial_update_victim_basic_happy_path(self):
        victim = VictimFactory()
        data = {'first_name': self.faker.fake.first_name()}
        url = reverse("victim-detail", kwargs={'incidents_pk': victim.incident.id,
                                               'pk': victim.id})
        response = self.client.patch(url, data=data,
                                     format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        victim.refresh_from_db()
        self.assertEqual(victim.first_name, data['first_name'])

    def test_put_update_not_allowed(self):
        victim = VictimFactory()
        data = {'first_name': self.faker.fake.first_name()}
        url = reverse("victim-detail", kwargs={'incidents_pk': victim.incident.id,
                                               'pk': victim.id})
        response = self.client.put(url, data=data,
                                   format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_victim(self):
        victim = VictimFactory()
        incident = victim.incident
        url = reverse("victim-detail", kwargs={'incidents_pk': victim.incident.id,
                                               'pk': victim.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        victims = IncidentInvolvedParty.objects.filter(incident=incident,
                                                       party_type=VICTIM)
        self.assertEqual(victims.count(), 0)


class SuspectTestCase(JWTAuthAPIBaseTestCase):

    fixtures = ["states.json"]

    def test_create_suspect(self):
        incident = IncidentFactory()
        data = self.faker.generate_involved_party(party_type=SUSPECT,
                                                  incident=incident,
                                                  officer_signed=OfficerFactory())
        url = reverse("suspect-list", kwargs={'incidents_pk': str(incident.pk)})
        response = self.client.post(url, data=data,
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        suspects = IncidentInvolvedParty.objects.filter(incident=incident,
                                                        party_type=SUSPECT)
        self.assertEqual(suspects.count(), 1)
        self.assertEqual(suspects.first().first_name, data['first_name'])
        self.assertEqual(suspects.first().last_name, data['last_name'])

    def test_partial_update_victim_basic_happy_path(self):
        suspect = SuspectFactory()
        data = {'first_name': self.faker.fake.first_name()}
        url = reverse("suspect-detail", kwargs={'incidents_pk': suspect.incident.id,
                                                'pk': suspect.id})
        response = self.client.patch(url, data=data,
                                     format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        suspect.refresh_from_db()
        self.assertEqual(suspect.first_name, data['first_name'])

    def test_put_update_not_allowed(self):
        suspect = SuspectFactory()
        data = {'first_name': self.faker.fake.first_name()}
        url = reverse("suspect-detail", kwargs={'incidents_pk': suspect.incident.id,
                                                'pk': suspect.id})
        response = self.client.put(url, data=data,
                                   format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_suspect(self):
        suspect = SuspectFactory()
        incident = suspect.incident
        url = reverse("suspect-detail", kwargs={'incidents_pk': suspect.incident.id,
                                                'pk': suspect.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        suspects = IncidentInvolvedParty.objects.filter(incident=incident,
                                                        party_type=SUSPECT)
        self.assertEqual(suspects.count(), 0)


@override_settings(MEDIA_ROOT="/tmp/APD/")
class IncidentFileTestCase(JWTAuthAPIBaseTestCase):

    fixtures = ["states.json"]

    def setUp(self):
        super(IncidentFileTestCase, self).setUp()
        self.incident = IncidentFactory()

    def tearDown(self):
        shutil.rmtree(self.incident.upload_directory)

    def test_create_single_file_upload(self):
        upload_file = generate_random_file_content(suffix="foo.txt")
        data = {'files': [upload_file]}
        url = reverse("file-list", kwargs={'incidents_pk': self.incident.pk})
        response = self.client.post(url, data=data,
                                    format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected_file = Path(f"{settings.MEDIA_ROOT}/"
                             f"{self.incident.incident_number}"
                             f"/test_file_foo.txt")
        self.assertTrue(expected_file.is_file())

    def test_delete_incident_file_removes_from_db_and_disk(self):
        upload_file = generate_random_file_content(suffix="foo.txt")
        inc_file = IncidentFile(incident=self.incident,
                                file=upload_file)
        inc_file.save()
        file_path = inc_file.file.path
        url = reverse("file-detail", kwargs={'incidents_pk': self.incident.pk,
                                             'pk': inc_file.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        inc_files = IncidentFile.objects.filter(incident=self.incident)
        self.assertEqual(inc_files.count(), 0)
        deleted_file = Path(file_path)
        self.assertFalse(deleted_file.is_file())
