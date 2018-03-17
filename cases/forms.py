import logging
from django import forms
from address.forms import AddressField
from .models import Offense

from .constants import (SHIFT_CHOICES,
                        SEX_CHOICES, RACE_CHOICES,
                        HAIR_COLOR_CHOICES,
                        EYE_COLOR_CHOICES)
logger = logging.getLogger('cases')


class IncidentSearchForm(forms.Form):
    incident_number = forms.CharField(max_length=35, required=False)
    report_datetime_min = forms.DateTimeField(required=False)
    report_datetime_max = forms.DateTimeField(required=False)
    reporting_officer = forms.CharField(required=False)

    earliest_occurrence_datetime = forms.DateTimeField(required=False)
    latest_occurrence_datetime = forms.DateTimeField(required=False)

    location = AddressField(required=False)

    beat = forms.IntegerField(required=False)
    shift = forms.ChoiceField(required=False, choices=SHIFT_CHOICES)
    offenses = forms.ModelMultipleChoiceField(queryset=Offense.objects.all(), required=False)
    min_damage_amount = forms.IntegerField(required=False)
    max_damage_amount = forms.IntegerField(required=False)

    min_stolen_amount = forms.IntegerField(required=False)
    max_stolen_amount = forms.IntegerField(required=False)

    # Party related fields
    victim_juvenile = forms.NullBooleanField()
    victim_date_of_birth_min = forms.DateField(required=False)
    victim_date_of_birth_max = forms.DateField(required=False)
    victim_sex = forms.ChoiceField(choices=SEX_CHOICES,required=False)
    victim_race = forms.ChoiceField(choices=RACE_CHOICES, required=False)
    victim_height_min = forms.IntegerField(required=False)
    victim_height_max = forms.IntegerField(required=False)
    victim_weight_min = forms.IntegerField(required=False)
    victim_weight_max = forms.IntegerField(required=False)
    victim_build = forms.CharField(required=False)
    victim_hair_color = forms.ChoiceField(choices=HAIR_COLOR_CHOICES, required=False)
    victim_eye_color = forms.ChoiceField(choices=EYE_COLOR_CHOICES, required=False)

    suspect_juvenile = forms.NullBooleanField()
    suspect_date_of_birth_min = forms.DateField(required=False)
    suspect_date_of_birth_max = forms.DateField(required=False)
    suspect_sex = forms.ChoiceField(choices=SEX_CHOICES, required=False)
    suspect_race = forms.ChoiceField(choices=RACE_CHOICES, required=False)
    suspect_height_min = forms.IntegerField(required=False)
    suspect_height_max = forms.IntegerField(required=False)
    suspect_weight_min = forms.IntegerField(required=False)
    suspect_weight_max = forms.IntegerField(required=False)
    suspect_build = forms.CharField(required=False)
    suspect_hair_color = forms.ChoiceField(choices=HAIR_COLOR_CHOICES, required=False)
    suspect_eye_color = forms.ChoiceField(choices=EYE_COLOR_CHOICES, required=False)
