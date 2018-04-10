import logging
import shutil
import pytz
from datetime import datetime, timedelta, date
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
                'reporting_officer': reporting_officer.id,
                'investigating_officer': reporting_officer.id,
                'officer_making_report': reporting_officer.id,
                'reviewed_by_officer': supervisor.id,
                'supervisor': supervisor.id,
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
        reponse = self.client.put(url, data=data)
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


class VictimTestCase(JWTAuthAPIBaseTestCase):

    fixtures = ["states.json"]

    def test_create_victim(self):
        incident = IncidentFactory()
        data = self.faker.generate_involved_party(party_type=VICTIM,
                                                  incident=incident)
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
                                                  incident=incident)
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
        url = reverse("file-list", kwargs={'incidents_pk':
                                               self.incident.pk})
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


class SearchTestCase(JWTAuthAPIBaseTestCase):

    fixtures = ["states.json"]

    def test_basic_incident_number_search(self):
        incident = IncidentFactory()
        url = reverse("search")
        data = {'incident_number': incident.incident_number[:5]}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], incident.id)

    def test_report_date_time_search(self):
        tzinfo = pytz.timezone(settings.TIME_ZONE)
        first_date = datetime(year=2014,
                              month=6,
                              day=15,
                              tzinfo=tzinfo)
        second_date = datetime(year=2015,
                               month=7,
                               day=23,
                               tzinfo=tzinfo)
        first_incident = IncidentFactory(report_datetime=first_date)
        second_incident = IncidentFactory(report_datetime=second_date)

        divider_datetime = datetime(year=2015,
                                    month=1,
                                    day=1,
                                    tzinfo=tzinfo)

        url = reverse("search")
        data = {'report_datetime_min': {'date': divider_datetime.strftime("%Y-%m-%d"),
                                        'time': divider_datetime.strftime("%H:%M")}}
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], second_incident.id)

    def test_reporting_officer_search(self):
        incident = IncidentFactory()
        reporting_officer = incident.reporting_officer
        url = reverse("search")
        data = {'reporting_officer': reporting_officer.id}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data[0]['id'], incident.id)

    def test_occurrence_range(self):
        tzinfo = pytz.timezone(settings.TIME_ZONE)
        first_date = datetime(year=2014,
                              month=6,
                              day=15,
                              tzinfo=tzinfo)
        second_date = datetime(year=2015,
                               month=7,
                               day=23,
                               tzinfo=tzinfo)
        third_date = datetime(year=2016,
                              month=10,
                              day=11,
                              tzinfo=tzinfo)
        IncidentFactory(earliest_occurrence_datetime=first_date - timedelta(days=1),
                        latest_occurrence_datetime=first_date + timedelta(days=1))
        expected_incident = IncidentFactory(earliest_occurrence_datetime=second_date - timedelta(days=1),
                                            latest_occurrence_datetime=second_date + timedelta(days=1))
        IncidentFactory(earliest_occurrence_datetime=third_date - timedelta(days=1),
                        latest_occurrence_datetime=third_date + timedelta(days=1))

        url = reverse("search")
        early = (second_date - timedelta(days=7))
        late = (second_date + timedelta(days=7))
        data = {'earliest_occurrence_datetime': {'date': early.strftime("%Y-%m-%d"),
                                                 'time': early.strftime("%H:%M")},
                'latest_occurrence_datetime': {'date': late.strftime("%Y-%m-%d"),
                                               'time': late.strftime("%H:%M")}}
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], expected_incident.id)

    def test_location_route_search(self):
        incident = IncidentFactory()
        route = incident.location.route
        url = reverse("search")
        data = {'location': {'route': route}}
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data[0]['id'], incident.id)

    def test_location_city_name_search(self):
        incident = IncidentFactory()
        city_name = incident.location.city.name
        url = reverse("search")
        data = {'location': {'city': city_name}}
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data[0]['id'], incident.id)

    def test_location_state_search(self):
        incident = IncidentFactory()
        state_abbr = incident.location.city.state.abbreviation
        url = reverse("search")
        data = {'location': {'state': state_abbr}}
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data[0]['id'], incident.id)

    def test_offenses_lookup(self):
        incident = IncidentFactory()
        offenses = OffenseFactory.create_batch(4)

        for off in offenses:
            incident.offenses.add(off)

        url = reverse("search")
        data = {'offenses': [offenses[0].id, offenses[2].id]}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data[0]['id'], incident.id)

    def test_involved_party_juvenile_lookup(self):
        incident = IncidentFactory()
        VictimFactory(incident=incident,
                      juvenile=True)
        url = reverse("search")
        data = {'victim': {'juvenile': True}}
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data[0]['id'], incident.id)

    def test_involved_party_date_of_birth_range(self):
        exp_incident = IncidentFactory()
        one_dob = date(year=1980,
                       month=6,
                       day=15)
        suspect_one = SuspectFactory(incident=exp_incident,
                                     date_of_birth=one_dob)

        other_inc = IncidentFactory()
        two_dob = date(year=1990,
                       month=4,
                       day=22)
        suspect_two = SuspectFactory(incident=other_inc,
                                     date_of_birth=two_dob)
        url = reverse("search")
        data = {'suspect': {'date_of_birth_min': (one_dob -
                                                  timedelta(days=365)).strftime("%Y-%m-%d"),
                            'date_of_birth_max': (one_dob +
                                                  timedelta(days=365)).strftime("%Y-%m-%d")
                            }
                }
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data[0]['id'], exp_incident.id)


