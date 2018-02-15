from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelformset_factory
from django.http import HttpResponse
from .forms import (IncidentForm,
                    IncidentInvolvedPartyForm,
                    populate_initial_incident_update_form_data,
                    IncidentSearchForm)
from .models import Incident, IncidentInvolvedParty
from .constants import VICTIM, SUSPECT
from .utils import parse_and_compile_incident_input_data
from .search import get_search_results
from .printing import IncidentReportPDFGenerator


@login_required
def index(request, *args, **kwargs):
    incidents = Incident.objects.all()
    display_fields = ["Incident Number", "Report Date & Time", "Reporting Officer"]
    context = {'incidents': incidents,
               'display_fields': display_fields}
    return render(request, "cases/index.html", context=context)


@login_required
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


@login_required
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
        incident_valid = incident_form.is_valid()
        victim_valid = victim_formset.is_valid()
        suspect_valid = suspect_formset.is_valid()
        if incident_valid and victim_valid and suspect_valid:
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


@login_required
def search(request, *args, **kwargs):
    display_fields = ["Incident Number", "Report Date & Time", "Reporting Officer"]
    if request.method == "POST":
        form = IncidentSearchForm(request.POST)
        results = get_search_results(request.POST)
        print(f"request.POST: {request.POST}")
        was_post = True
    else:
        form = IncidentSearchForm()
        results = []
        was_post = False

    context = {'form': form,
               'results': results,
               'display_fields': display_fields,
               'was_post': was_post}
    return render(request, "cases/search.html", context=context)


@login_required
def print_report(request, *args, **kwargs):
    print((args, kwargs))
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="somefilename.pdf"'

    pdf_generator = IncidentReportPDFGenerator(response, kwargs.get('incident_id'))
    pdf_generator.generate()
    return response
