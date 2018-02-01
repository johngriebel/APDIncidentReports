from django.db import models
from django.contrib.auth import get_user_model
from djmoney.models.fields import MoneyField
from .constants import (STATE_CHOICES, SHIFT_CHOICES,
                        PARTY_TYPE_CHOICES, SEX_CHOICES,
                        RACE_CHOICES, HAIR_COLOR_CHOICES,
                        EYE_COLOR_CHOICES)
User = get_user_model()


class Address(models.Model):
    street = models.CharField(max_length=255)
    street_two = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, default="Atlanta")
    state = models.CharField(max_length=2, choices=STATE_CHOICES)
    zip_code = models.CharField(max_length=5)

    class Meta:
        db_table = "address"


class Officer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    officer_number = models.IntegerField(unique=True)
    supervisor = models.ForeignKey("Officer", null=True, on_delete=models.CASCADE)

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
    shift = models.CharField(max_length=1, choices=SHIFT_CHOICES)
    damaged_amount = MoneyField(max_digits=12, decimal_places=2,
                                default_currency="USD", default=0.0)
    stolen_amount = MoneyField(max_digits=12, decimal_places=2,
                               default_currency="USD", default=0.0)

    offenses = models.ManyToManyField("Offense")
    narrative = models.TextField(null=True)

    # TODO Fields
    # associated_offense_number
    # disposition

    class Meta:
        db_table = "incident"


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
    party_type = models.CharField(max_length=7, choices=PARTY_TYPE_CHOICES)
    juvenile = models.BooleanField(default=False)
    home_address = models.ForeignKey(Address, null=True,
                                     on_delete=models.CASCADE,
                                     related_name="incident_party_address")
    # THis is a todo field. I haven't arrived at a good solution for storing these safely yet.
    social_security_number = None
    date_of_birth = models.DateField(null=True)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
    race = models.CharField(max_length=50, choices=RACE_CHOICES)
    height = models.IntegerField(null=True)
    weight = models.IntegerField(null=True)
    hair_color = models.CharField(max_length=20, null=True, choices=HAIR_COLOR_CHOICES)
    eye_color = models.CharField(max_length=20, null=True, choices=EYE_COLOR_CHOICES)
    drivers_license = models.CharField(max_length=100, null=True)
    drivers_license_state = models.CharField(max_length=2, null=True, choices=STATE_CHOICES)
    employer = models.CharField(max_length=200)
    employer_address = models.ForeignKey(Address, null=True,
                                         on_delete=models.CASCADE,
                                         related_name="incident_employer_address")
    build = models.CharField(max_length=25, null=True, blank=True)
    tattoos = models.TextField(null=True, blank=True)
    scars = models.TextField(null=True, blank=True)
    hairstyle = models.CharField(max_length=30, null=True, blank=True)


def determine_file_upload_path(instance, filename):
    return f"{instance.incident.incident_number}/{filename}"


class IncidentFile(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE)
    file = models.FileField(upload_to=determine_file_upload_path)

