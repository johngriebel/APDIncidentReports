import os

from datetime import datetime
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

from cases.constants import (STATE_CHOICES, SHIFT_CHOICES,
                             PARTY_TYPE_CHOICES, SEX_CHOICES,
                             RACE_CHOICES, HAIR_COLOR_CHOICES,
                             EYE_COLOR_CHOICES)
User = get_user_model()


class APDIncidentBaseModel(models.Model):
    created_timestamp = models.DateTimeField(auto_now_add=True)
    updated_timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# TODO: State, city, and address probably don't belong in the cases app,
# But don't really deserve an entire app, do  they?
class State(APDIncidentBaseModel):
    """
    'State' in this context represents the typical continental American idea of a 'state',
    as applied to any top level geographical distinction of the given country.
    In other words, Puerto Rico, Washington DC, the US Virgin Islands, etc. are all considered
    states.
    """
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=5, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "abbreviation"


class City(APDIncidentBaseModel):
    name = models.CharField(max_length=150)
    state = models.ForeignKey(State, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f"{self.name}, {self.state.abbreviation}"

    class Meta:
        db_table = "city"


class Address(APDIncidentBaseModel):
    street_number = models.CharField(max_length=25, null=True, blank=True)
    route = models.CharField(max_length=255, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.DO_NOTHING)
    postal_code = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f"{self.street_number} {self.route} {self.city} {self.postal_code}"

    class Meta:
        db_table = "address"


class Officer(APDIncidentBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    officer_number = models.IntegerField(unique=True)
    supervisor = models.ForeignKey("Officer", null=True, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return f"{self.user.last_name} - {self.officer_number}"

    class Meta:
        db_table = "officer"


class Incident(APDIncidentBaseModel):
    # Should incident number be auto-generated?
    incident_number = models.CharField(max_length=35, unique=True)
    report_datetime = models.DateTimeField(default=datetime.now)
    reporting_officer = models.ForeignKey(Officer,
                                          on_delete=models.CASCADE,
                                          related_name="reported_incidents")
    reviewed_by_officer = models.ForeignKey(Officer,
                                            on_delete=models.CASCADE,
                                            related_name="reviewed_incidents")
    reviewed_datetime = models.DateTimeField(null=True, blank=True)
    investigating_officer = models.ForeignKey(Officer,
                                              on_delete=models.CASCADE,
                                              related_name="investigated_incidents")
    officer_making_report = models.ForeignKey(Officer,
                                              on_delete=models.CASCADE,
                                              related_name="made_report_incidents")
    supervisor = models.ForeignKey(Officer,
                                   on_delete=models.CASCADE,
                                   related_name="supervised_reports")
    approved_datetime = models.DateTimeField(null=True, blank=True)
    earliest_occurrence_datetime = models.DateTimeField()
    latest_occurrence_datetime = models.DateTimeField()
    location = models.ForeignKey(Address, on_delete=models.DO_NOTHING)
    beat = models.IntegerField()
    shift = models.CharField(max_length=1, choices=SHIFT_CHOICES)
    damaged_amount = models.PositiveIntegerField(null=True)
    stolen_amount = models.PositiveIntegerField(null=True)

    offenses = models.ManyToManyField("Offense")
    narrative = models.TextField(null=True)

    # TODO Fields
    # associated_offense_number
    # disposition

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("cases.views.incident_detail", args=[str(self.id)])

    @property
    def upload_directory(self) -> str:
        return os.path.join(settings.MEDIA_ROOT, self.incident_number)

    class Meta:
        db_table = "incident"


class Offense(APDIncidentBaseModel):
    ucr_name_classification = models.CharField(max_length=100, default="")
    ucr_subclass_description = models.CharField(max_length=255, default="")
    gcic_code = models.CharField(max_length=8, null=True)
    ucr_code = models.CharField(max_length=8, null=True)
    ucr_rank = models.IntegerField(null=True)
    code_group = models.CharField(max_length=4, null=True)
    ucr_alpha = models.CharField(max_length=10)
    log_code = models.CharField(max_length=10, null=True)

    def __str__(self):
        return f"{self.ucr_name_classification}:{self.ucr_subclass_description} - {self.ucr_code}"

    class Meta:
        db_table = "offense"


class IncidentInvolvedParty(APDIncidentBaseModel):
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE)
    officer_signed = models.ForeignKey(Officer, null=True, on_delete=models.CASCADE)
    party_type = models.CharField(max_length=7, choices=PARTY_TYPE_CHOICES)
    juvenile = models.BooleanField(default=False)
    home_address = models.ForeignKey(Address, blank=True, null=True,
                                     related_name="party_home_address",
                                     on_delete=models.SET_NULL)
    # THis is a todo field. I haven't arrived at a good solution for storing these safely yet.
    social_security_number = None
    date_of_birth = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
    race = models.CharField(max_length=50, choices=RACE_CHOICES)
    height = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)
    hair_color = models.CharField(max_length=20, null=True, choices=HAIR_COLOR_CHOICES, blank=True)
    eye_color = models.CharField(max_length=20, null=True, choices=EYE_COLOR_CHOICES, blank=True)
    drivers_license = models.CharField(max_length=100, null=True, blank=True)
    drivers_license_state = models.CharField(max_length=2, null=True,
                                             choices=STATE_CHOICES, blank=True)
    employer = models.CharField(max_length=200, null=True, blank=True)
    employer_address = models.ForeignKey(Address, blank=True, null=True,
                                         related_name="incident_employer_address",
                                         on_delete=models.SET_NULL)
    build = models.CharField(max_length=25, null=True, blank=True)
    tattoos = models.TextField(null=True, blank=True)
    scars = models.TextField(null=True, blank=True)
    hairstyle = models.CharField(max_length=30, null=True, blank=True)
    display_sequence = models.IntegerField(null=True)

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"


def determine_file_upload_path(instance, filename):
    return f"{instance.incident.incident_number}/{filename}"


class IncidentFile(APDIncidentBaseModel):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE)
    file = models.FileField(upload_to=determine_file_upload_path)

    @property
    def display_name(self) -> str:
        return "/".join(self.file.name.split("/")[1:])

    @property
    def smart_size(self) -> str:
        raw_size = self.file.size
        kilobytes = raw_size / 1024

        if kilobytes < 1:
            return f"{raw_size} B"

        megabytes = kilobytes / 1024
        if megabytes < 1:
            return f"{kilobytes} KB"

        gigabytes = megabytes / 1024
        return f"{gigabytes} GB"
