from copy import deepcopy
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelformset_factory
from .forms import IncidentForm, IncidentInvolvedPartyForm, populate_initial_incident_update_form_data
from .models import Incident, IncidentInvolvedParty
from .constants import VICTIM, SUSPECT
from .utils import parse_and_compile_incident_input_data


# Create your views here.
def index(request, *args, **kwargs):
    context = {}
    return render(request, "cases/index.html", context=context)


def create_address(request, *args, **kwargs):
    pass


def create_incident(request, *args, **kwargs):
    VictimFormset = modelformset_factory(IncidentInvolvedParty,
                                         form=IncidentInvolvedPartyForm,
                                         exclude=('id', 'incident', 'party_type'))
    SuspectFormset = modelformset_factory(IncidentInvolvedParty,
                                          form=IncidentInvolvedPartyForm,
                                          exclude=['id', 'incident', 'party_type'])
    if request.method == 'POST':

        (incident_data, victim_data,
         suspect_data, party_data) = parse_and_compile_incident_input_data(request.POST)
        incident_form = IncidentForm(incident_data)

        victim_formset = VictimFormset(victim_data, prefix="victims",
                                       queryset=IncidentInvolvedParty.objects.none())
        suspect_formset = SuspectFormset(suspect_data, prefix="suspects",
                                         queryset=IncidentInvolvedParty.objects.none())

        if incident_form.is_valid() and victim_formset.is_valid and suspect_formset.is_valid():
            incident = incident_form.save(party_data=party_data)
            return redirect(f"/cases/{incident.id}")
        else:
            print(incident_form.errors)
    else:
        incident_form = IncidentForm()
        victim_formset = VictimFormset(prefix="victims",
                                       queryset=IncidentInvolvedParty.objects.none())
        suspect_formset = SuspectFormset(prefix="suspects",
                                         queryset=IncidentInvolvedParty.objects.none())

    context = {'form': incident_form,
               'victim_formset': victim_formset,
               'suspect_formset': suspect_formset}
    return render(request, "cases/create_incident.html", context=context)


def incident_detail(request, incident_id):
    incident = get_object_or_404(Incident, pk=incident_id)
    VictimFormset = modelformset_factory(IncidentInvolvedParty,
                                         form=IncidentInvolvedPartyForm,
                                         exclude=('id', 'incident', 'party_type'))
    SuspectFormset = modelformset_factory(IncidentInvolvedParty,
                                          form=IncidentInvolvedPartyForm,
                                          exclude=['id', 'incident', 'party_type'])
    victims = IncidentInvolvedParty.objects.filter(incident=incident,
                                                   party_type=VICTIM)
    suspects = IncidentInvolvedParty.objects.filter(incident=incident,
                                                    party_type=SUSPECT)
    if request.method == "POST":
        (incident_data, victim_data,
         suspect_data, party_data) = parse_and_compile_incident_input_data(request.POST)
        incident_form = IncidentForm(incident_data)

        victim_formset = VictimFormset(victim_data, prefix="victims",
                                       queryset=victims)
        suspect_formset = SuspectFormset(suspect_data, prefix="suspects",
                                         queryset=suspects)
        if incident_form.is_valid() and victim_formset.is_valid and suspect_formset.is_valid():
            incident = incident_form.save(party_data=party_data, instance=incident)
            return redirect(f"/cases/{incident.id}")
        else:
            print(incident_form.errors)
    else:

        forms = populate_initial_incident_update_form_data(incident)
        incident_form = IncidentForm(data=forms['incident_data'])

        victim_formset = VictimFormset(prefix="victims",
                                       queryset=victims)
        suspect_formset = SuspectFormset(prefix="suspects",
                                         queryset=suspects)

    return render(request, "cases/detail.html", context={'incident': incident,
                                                         'incident_form': incident_form,
                                                         'victim_formset': victim_formset,
                                                         'suspect_formset': suspect_formset})
