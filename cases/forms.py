from copy import deepcopy
from itertools import groupby
from django import forms
from django.forms import ModelForm
from .models import (Address, IncidentInvolvedParty,
                     Officer, Offense, Incident)
from .utils import convert_slash_date_to_iso
from .constants import STATE_CHOICES, SHIFT_CHOICES, VICTIM


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

    def save(self, victims_data=None, suspects_data=None):
        incident = None
        try:
            data = deepcopy(self.cleaned_data)
            print(data)
            offense_ids = data.pop("offenses")
            files = data.pop("files")

            address_data = {}
            for key in self.cleaned_data:
                if key.startswith("location_"):
                    address_data[key.replace("location_", "")] = data.pop(key)

            address = Address.objects.create(**address_data)
            data['location'] = address
            incident = Incident.objects.create(**data)
            offenses = Offense.objects.filter(id__in=offense_ids)
            incident.offenses.set(offenses)

            officers_cache = {}

            victim_groups = []
            for k, g in groupby(victims_data, lambda obj: obj.split("-")[:2]):
                if not ('INITIAL_FORMS' in k or 'MAX_NUM_FORMS' in k
                        or'MIN_NUM_FORMS' in k or 'TOTAL_FORMS' in k):
                    victim_groups.append(list(g))
            print(victim_groups)
            victims_to_create = []
            for group in victim_groups:
                if len(group) > 1:
                    indiv_victim_data = {key[10:]: victims_data[key] for key in group}
                    print(f"Indiv victim data: {indiv_victim_data}")
                    officer_id = indiv_victim_data['officer_signed']

                    converted_date = convert_slash_date_to_iso(indiv_victim_data['date_of_birth'])

                    indiv_victim_data['date_of_birth'] = converted_date

                    if officer_id in officers_cache:
                        indiv_victim_data['officer_signed'] = officers_cache[officer_id]
                    else:
                        officer = Officer.objects.get(id=officer_id)
                        indiv_victim_data['officer_signed'] = officers_cache[officer_id] = officer

                    home_address_id = indiv_victim_data['home_address']
                    if indiv_victim_data['home_address'] == "":
                        indiv_victim_data['home_address'] = None
                    else:
                        indiv_victim_data['home_address'] = Address.objects.get(id=home_address_id)

                    employer_address_id = indiv_victim_data['employer_address']
                    if employer_address_id == "":
                        indiv_victim_data['employer_address'] = None
                    else:
                        indiv_victim_data['employer_address'] = Address.objects.get(id=home_address_id)

                    if indiv_victim_data['height'] == "":
                        indiv_victim_data['height'] = None
                    if indiv_victim_data['weight'] == "":
                        indiv_victim_data['weight'] = None

                    indiv_victim_data.update({'incident': incident, 'party_type': VICTIM})
                    victims_to_create.append(IncidentInvolvedParty(**indiv_victim_data))
            count = IncidentInvolvedParty.objects.bulk_create(victims_to_create)
            print(f"Number of victims created: {count}")

            suspect_groups = []
            for k, g in groupby(suspects_data, lambda obj: obj.split("-")[:2]):
                if not ('INITIAL_FORMS' in k or 'MAX_NUM_FORMS' in k
                        or 'MIN_NUM_FORMS' in k or 'TOTAL_FORMS' in k):
                    suspect_groups.append(list(g))
            print(suspect_groups)
            suspects_to_create = []
            for group in suspect_groups:
                if len(group) > 1:
                    indiv_suspect_data = {key[11:]: suspects_data[key] for key in group}
                    officer_id = indiv_suspect_data['officer_signed']

                    converted_date = convert_slash_date_to_iso(indiv_suspect_data['date_of_birth'])
                    indiv_suspect_data['date_of_birth'] = converted_date

                    if officer_id in officers_cache:
                        indiv_suspect_data['officer_signed'] = officers_cache[officer_id]
                    else:
                        officer = Officer.objects.get(id=officer_id)
                        indiv_suspect_data['officer_signed'] = officers_cache[officer_id] = officer

                    home_address_id = indiv_suspect_data['home_address']
                    if home_address_id == "":
                        indiv_suspect_data['home_address'] = None
                    else:
                        indiv_suspect_data['home_address'] = Address.objects.get(id=home_address_id)

                    employer_address_id = indiv_suspect_data['employer_address']
                    if employer_address_id == "":
                        indiv_suspect_data['employer_address'] = None
                    else:
                        indiv_suspect_data['employer_address'] = Address.objects.get(id=home_address_id)

                    if indiv_suspect_data['height'] == "":
                        indiv_suspect_data['height'] = None
                    if indiv_suspect_data['weight'] == "":
                        indiv_suspect_data['weight'] = None


                    indiv_suspect_data.update({'incident': incident, 'party_type': VICTIM})
                    suspects_to_create.append(IncidentInvolvedParty(**indiv_suspect_data))
            count = IncidentInvolvedParty.objects.bulk_create(suspects_to_create)
            print(f"Number of suspects created: {count}")

            return incident
        except Exception as e:
            if incident is not None and incident.id is not None:
                incident.delete()
            raise e


class IncidentInvolvedPartyForm(ModelForm):
    class Meta:
        model = IncidentInvolvedParty
        exclude = ['id', 'incident', 'party_type']
