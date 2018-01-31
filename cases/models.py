from django.db import models
from django.contrib.auth import get_user_model
from djmoney.models.fields import MoneyField
User = get_user_model()


class Address(models.Model):
    street = models.CharField(max_length=255)
    street_two = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, default="Atlanta")

    GEORGIA = "GA"
    STATE_CHOICES = [(GEORGIA, "Georgia")]

    state = models.CharField(max_length=2, choices=STATE_CHOICES)
    zip_code = models.CharField(max_length=5)


class Officer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    officer_number = models.IntegerField(unique=True)

    class Meta:
        db_table = "officer"


class Incident(models.Model):
    incident_number = models.CharField(max_length=35, unique=True)
    report_datetime = models.DateTimeField()
    reporting_officer = models.ForeignKey(Officer,
                                          on_delete=models.CASCADE,
                                          related_name="reported_incidents")
    reviewed_by_officer = models.ForeignKey(Officer,
                                            on_delete=models.CASCADE,
                                            related_name="reviewed_incidents")
    investigating_officer = models.ForeignKey(Officer,
                                              on_delete=models.CASCADE,
                                              related_name="investigated_incidents")
    officer_making_report = models.ForeignKey(Officer,
                                              on_delete=models.CASCADE,
                                              related_name="made_report_incidents")
    supervisor = models.ForeignKey(Officer,
                                   on_delete=models.CASCADE,
                                   related_name="supervised_reports")
    earliest_occurrence_datetime = models.DateTimeField()
    latest_occurrence_datetime = models.DateTimeField()
    location = models.ForeignKey(Address, on_delete=models.CASCADE)
    beat = models.IntegerField()

    DAY = "D"
    EVENING = "E"
    NIGHT = "N"

    SHIFT_CHOICES = [(DAY, "Day"),
                     (EVENING, "Evening"),
                     (NIGHT, "Night")]

    shift = models.CharField(max_length=1, choices=SHIFT_CHOICES)
    damaged_amount = MoneyField(max_digits=12, decimal_places=2,
                                default_currency="USD", default=0.0)
    stolen_amount = MoneyField(max_digits=12, decimal_places=2,
                                default_currency="USD", default=0.0)

    offenses = models.ManyToManyField("Offense")
    narrative = models.TextField(null=True)

    class Meta:
        db_table = "incident"


    # TODO Fields
    # associated_offense_number
    # disposition


class Offense(models.Model):
    gcic_code = models.IntegerField()
    ucr_code = models.IntegerField()
    ucr_rank = models.IntegerField(null=True)
    code_group = models.CharField(max_length=4, null=True)
    ucr_alpha = models.CharField(max_length=10)
    description = models.CharField(max_length=50)

    class Meta:
        db_table = "offense"


class IncidentInvolvedParty(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE)
    officer_signed = models.ForeignKey(Officer, null=True, on_delete=models.CASCADE)
    VICTIM = "VICTIM"
    SUSPECT = "SUSPECT"

    TYPE_CHOICES = [(VICTIM, "Victim"),
                    (SUSPECT, "Suspect")]

    party_type = models.CharField(max_length=7, choices=TYPE_CHOICES)
    juvenile = models.BooleanField(default=False)
    home_address = models.ForeignKey(Address, null=True,
                                     on_delete=models.CASCADE,
                                     related_name="incident_party_address")
    # THis is a todo field. I haven't arrived at a good solution for storing these safely yet.
    social_security_number = None
    # entire physical description- height, weight, build, tattoos, scars, hairstyle, eye color so that these may be a searchable field
    date_of_birth = models.DateField(null=True)
    MALE = "M"
    FEMALE = "F"
    SEX_CHOICES = [(MALE, "Male"),
                   (FEMALE, "Female")]
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)

    # TODO: Hispanic?

    ASIAN = "ASIAN"
    BLACK = "BLACK"
    NATIVE = "NATIVE"
    PAC_ISLANDER = "HAWAIIAN/PACIFIC_ISLANDER"
    WHITE = "WHITE"
    OTHER = "OTHER"

    RACE_CHOICES = [(ASIAN, "Asian"),
                    (BLACK, "Black/African American"),
                    (NATIVE, "Native American"),
                    (PAC_ISLANDER, "Native Hawaiian/Pacific Islander"),
                    (WHITE, "White"),
                    (OTHER, "Other")]

    height = models.IntegerField(null=True)
    weight = models.IntegerField(null=True)
    # TODO: Choices
    hair_color = models.CharField(max_length=20, null=True)
    # TODO: Choices
    eye_color = models.CharField(max_length=20, null=True)
    drivers_license = models.CharField(max_length=100, null=True)
    # TODO: Choices
    drivers_license_state = models.CharField(max_length=2, null=True)
    employer = models.CharField(max_length=200)
    employer_address = models.ForeignKey(Address, null=True,
                                         on_delete=models.CASCADE,
                                         related_name="incident_employer_address")


def determine_file_upload_path(instance, filename):
    return f"{instance.incident.incident_number}/{filename}"


class IncidentFile(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE)
    file = models.FileField(upload_to=determine_file_upload_path)

