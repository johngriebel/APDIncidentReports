from copy import deepcopy
from django import forms
from django.forms import ModelForm
from address.forms import AddressField
from .models import (IncidentInvolvedParty,
                     Officer, Offense, Incident)
from .utils import cleanse_incident_party_data_and_create, get_party_groups
from .constants import (STATE_CHOICES, SHIFT_CHOICES,
                        SEX_CHOICES, RACE_CHOICES,
                        HAIR_COLOR_CHOICES,
                        EYE_COLOR_CHOICES)


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

    location = AddressField()

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

            # address, _ = Address.objects.get_or_create(**address_data,
            #                                            defaults=address_data)
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
                pass
            raise e


class IncidentInvolvedPartyForm(ModelForm):
    class Meta:
        model = IncidentInvolvedParty
        exclude = ['id', 'incident', 'party_type']


class IncidentSearchForm(forms.Form):
    incident_number = forms.CharField(max_length=35, required=False)
    report_datetime_min = forms.DateTimeField(required=False)
    report_datetime_max = forms.DateTimeField(required=False)
    reporting_officer = forms.CharField(required=False)

    earliest_occurrence_datetime = forms.DateTimeField(required=False)
    latest_occurrence_datetime = forms.DateTimeField(required=False)

    locations = AddressField()

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
