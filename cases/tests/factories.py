import factory
from faker import Faker
from django.contrib.auth import get_user_model
from cases.models import Officer, Offense
User = get_user_model()


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")


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
