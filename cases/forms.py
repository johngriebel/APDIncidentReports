from copy import deepcopy
from itertools import groupby
from django import forms
from django.forms import ModelForm
from .models import (Address, IncidentInvolvedParty,
                     Officer, Offense, Incident)
from .utils import cleanse_incident_party_data, get_party_groups
from .constants import STATE_CHOICES, SHIFT_CHOICES


class AddressForm(ModelForm):
    class Meta:
        model = Address
        exclude = ['id']


class IncidentForm(forms.Form):
    incident_number = forms.CharField(max_length=35)
    report_datetime = forms.DateTimeField()
    reporting_officer = forms.ModelChoiceField(queryset=Officer.objects.all())
    reviewed_by_officer = forms.ModelChoiceField(queryset=Officer.objects.all())
    investigating_officer = forms.ModelChoiceField(queryset=Officer.objects.all())
    officer_making_report = forms.ModelChoiceField(queryset=Officer.objects.all())
    supervisor = forms.ModelChoiceField(queryset=Officer.objects.all())
    earliest_occurrence_datetime = forms.DateTimeField()
    latest_occurrence_datetime = forms.DateTimeField()

    location_street = forms.CharField()
    location_street_two = forms.CharField(required=False)
    location_city = forms.CharField()
    location_state = forms.ChoiceField(choices=STATE_CHOICES)
    location_zip_code = forms.CharField(max_length=5)

    beat = forms.IntegerField()
    shift = forms.ChoiceField(choices=SHIFT_CHOICES)
    damaged_amount = forms.DecimalField(max_digits=12, decimal_places=2, required=False)
    stolen_amount = forms.DecimalField(max_digits=12, decimal_places=2, required=False)

    offenses = forms.ModelMultipleChoiceField(queryset=Offense.objects.all(), required=False)

    narrative = forms.CharField(widget=forms.Textarea)
    files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}),
                            required=False)

    def save(self, party_data=None):
        incident = None
        try:
            data = deepcopy(self.cleaned_data)
            print(("data", data))

            offense_ids = data.pop("offenses")
            files = data.pop("files")

            address_data = {}
            for key in self.cleaned_data:
                if key.startswith("location_"):
                    address_data[key.replace("location_", "")] = data.pop(key)

            address = Address.objects.get_or_create(**address_data,
                                                    defaults=address_data)
            data['location'] = address
            incident = Incident.objects.create(**data)
            offenses = Offense.objects.filter(id__in=offense_ids)
            incident.offenses.set(offenses)

            groups = get_party_groups(data=party_data)
            parties_to_create = cleanse_incident_party_data(incident=incident,
                                                            data=party_data,
                                                            groups=groups)
            IncidentInvolvedParty.objects.bulk_create(parties_to_create)

            return incident
        except Exception as e:
            if incident is not None and incident.id is not None:
                incident.delete()
            raise e


class IncidentInvolvedPartyForm(ModelForm):
    class Meta:
        model = IncidentInvolvedParty
        exclude = ['id', 'incident', 'party_type']
