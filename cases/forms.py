from copy import deepcopy
from django.forms import modelformset_factory
from django import forms
from django.forms import ModelForm
from .models import (Address, IncidentInvolvedParty,
                     Officer, Offense, Incident)
from .utils import cleanse_incident_party_data_and_create, get_party_groups
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

    def save(self, party_data=None, instance=None):
        incident = instance
        try:
            data = deepcopy(self.cleaned_data)
            print(("data", data))

            offense_ids = data.pop("offenses")
            files = data.pop("files")

            address_data = {}
            for key in self.cleaned_data:
                if key.startswith("location_"):
                    address_data[key.replace("location_", "")] = data.pop(key)

            address, _ = Address.objects.get_or_create(**address_data,
                                                       defaults=address_data)
            data['location'] = address
            incident, _ = Incident.objects.update_or_create(id=getattr(incident, "id", None),
                                                            defaults=data)
            offenses = Offense.objects.filter(id__in=offense_ids)
            incident.offenses.set(offenses)

            groups = get_party_groups(data=party_data)
            cleanse_incident_party_data_and_create(incident=incident,
                                                   data=party_data,
                                                   groups=groups)

            return incident
        except Exception as e:
            if incident is not None and incident.id is not None:
                incident.delete()
            raise e


class IncidentInvolvedPartyForm(ModelForm):
    class Meta:
        model = IncidentInvolvedParty
        exclude = ['id', 'incident', 'party_type']


def populate_initial_incident_update_form_data(incident: Incident) -> dict:
    incident_data = {field: getattr(incident, field) for field in IncidentForm().fields
                     if (not field.startswith("location_")) and not field.startswith("files")}
    incident_data['stolen_amount'] = str(incident_data['stolen_amount']).replace("$", "")
    incident_data['damaged_amount'] = str(incident_data['damaged_amount']).replace("$", "")
    for k in incident_data:
        if "officer" in k:
            incident_data[k] = incident_data[k].pk

    incident_data['offenses'] = incident.offenses.all()

    for field in ["street", "street_two", "city", "state", "zip_code"]:
        incident_data["location_" + field] = getattr(incident.location, field)

    return {'incident_data': incident_data}
