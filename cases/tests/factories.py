import factory
import random

from pytz import timezone
from faker import Faker
from django.conf import settings
from django.contrib.auth import get_user_model
from cases.models import (Officer, Offense,
                          Incident, IncidentInvolvedParty,
                          Address, State, City)
from cases.constants import (SEX_CHOICES, RACE_CHOICES,
                             HAIR_COLOR_CHOICES,
                             EYE_COLOR_CHOICES)
User = get_user_model()
this_timezone = timezone(settings.TIME_ZONE)


def get_random_state():
    state_ids = State.objects.all().values_list('id', flat=True)
    if not state_ids:
        return StateFactory()
    id_to_use = random.choice(state_ids)
    return State.objects.get(id=id_to_use)


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")


class StateFactory(factory.DjangoModelFactory):
    class Meta:
        model = State

    name = factory.Faker("state")
    abbreviation = factory.Faker("state_abbr")


class CityFactory(factory.DjangoModelFactory):
    class Meta:
        model = City

    name = factory.Faker("city")
    state = factory.LazyFunction(get_random_state)


class AddressFactory(factory.DjangoModelFactory):
    class Meta:
        model = Address
    street_number = factory.Faker("building_number")
    route = factory.Faker("street_name")
    city = factory.SubFactory(CityFactory)
    postal_code = factory.Faker("postalcode")


class OfficerFactory(factory.DjangoModelFactory):
    class Meta:
        model = Officer

    user = factory.SubFactory(UserFactory)
    officer_number = factory.Sequence(lambda n: f"{n}")
    supervisor = None


class OffenseFactory(factory.DjangoModelFactory):
    class Meta:
        model = Offense
    ucr_name_classification = factory.Faker("sentence")
    ucr_subclass_description = factory.Faker("sentence")
    gcic_code = factory.LazyFunction(lambda: Faker().word()[:8])
    ucr_code = factory.LazyFunction(lambda: Faker().word()[:8])
    ucr_rank = factory.Faker("random_int")
    ucr_alpha = factory.LazyFunction(lambda: Faker().word()[:10])


class IncidentFactory(factory.DjangoModelFactory):
    class Meta:
        model = Incident

    incident_number = factory.Sequence(lambda n: f"incident_{n}")
    report_datetime = factory.Faker("date_time_this_month", tzinfo=this_timezone)
    reporting_officer = factory.SubFactory(OfficerFactory)
    reviewed_by_officer = factory.SubFactory(OfficerFactory)
    reviewed_datetime = factory.Faker("date_time_this_month", tzinfo=this_timezone)
    investigating_officer = factory.SubFactory(OfficerFactory)
    officer_making_report = factory.SubFactory(OfficerFactory)
    supervisor = factory.SubFactory(OfficerFactory)
    approved_datetime = factory.Faker("date_time_this_month", tzinfo=this_timezone)
    earliest_occurrence_datetime = factory.Faker("date_time_this_month", tzinfo=this_timezone)
    latest_occurrence_datetime = factory.Faker("date_time_this_month", tzinfo=this_timezone)
    location = factory.SubFactory(AddressFactory)
    beat = factory.Faker("random_int")
    shift = "E"
    damaged_amount = None
    stolen_amount = None
    narrative = factory.Faker("paragraph")


class VictimFactory(factory.DjangoModelFactory):
    class Meta:
        model = IncidentInvolvedParty

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    incident = factory.SubFactory(IncidentFactory)
    officer_signed = factory.SubFactory(OfficerFactory)
    party_type = "VICTIM"
    juvenile = factory.Faker("pybool")
    home_address = None
    date_of_birth = factory.Faker("date")
    sex = factory.LazyFunction(lambda: Faker().random_element([c[0] for c in SEX_CHOICES]))
    race = factory.LazyFunction(lambda: Faker().random_element([c[0] for c in RACE_CHOICES]))
    height = factory.Faker("pyint")
    weight = factory.Faker("pyint")
    hair_color = factory.LazyFunction(lambda: Faker().random_element([c[0]
                                                                      for c in HAIR_COLOR_CHOICES]))
    eye_color = factory.LazyFunction(lambda: Faker().random_element([c[0]
                                                                     for c in EYE_COLOR_CHOICES]))
    drivers_license = None
    drivers_license_state = None
    employer = None
    employer_address = None
    build = factory.Faker("word")
    tattoos = factory.Faker("word")
    scars = factory.Faker("word")
    hairstyle = factory.Faker("word")


class SuspectFactory(factory.DjangoModelFactory):
    class Meta:
        model = IncidentInvolvedParty

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    incident = factory.SubFactory(IncidentFactory)
    officer_signed = factory.SubFactory(OfficerFactory)
    party_type = "SUSPECT"
    juvenile = factory.Faker("pybool")
    home_address = None
    date_of_birth = factory.Faker("date")
    sex = factory.LazyFunction(lambda: Faker().random_element([c[0] for c in SEX_CHOICES]))
    race = factory.LazyFunction(lambda: Faker().random_element([c[0] for c in RACE_CHOICES]))
    height = factory.Faker("pyint")
    weight = factory.Faker("pyint")
    hair_color = factory.LazyFunction(lambda: Faker().random_element([c[0]
                                                                      for c in HAIR_COLOR_CHOICES]))
    eye_color = factory.LazyFunction(lambda: Faker().random_element([c[0]
                                                                     for c in EYE_COLOR_CHOICES]))
    drivers_license = None
    drivers_license_state = None
    employer = None
    employer_address = None
    build = factory.Faker("word")
    tattoos = factory.Faker("word")
    scars = factory.Faker("word")
    hairstyle = factory.Faker("word")
