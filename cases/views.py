import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelformset_factory
from django.http import HttpResponse
from .forms import (IncidentForm,
                    IncidentInvolvedPartyForm,
                    populate_initial_incident_update_form_data,
                    IncidentSearchForm)
from .models import Incident, IncidentInvolvedParty
from .utils import parse_and_compile_incident_input_data
from .search import get_search_results
from .printing import IncidentReportPDFGenerator
logger = logging.getLogger('cases')


@login_required
def index(request, *args, **kwargs):
    incidents = Incident.objects.all()
    display_fields = ["Incident Number", "Report Date & Time", "Reporting Officer"]
    context = {'incidents': incidents,
               'display_fields': display_fields}
    return render(request, "cases/index.html", context=context)


@login_required
def create_incident(request, *args, **kwargs):
    # print(f"request.POST: {request.POST}")
    VictimFormset = modelformset_factory(IncidentInvolvedParty,
                                         form=IncidentInvolvedPartyForm,
                                         exclude=('id', 'incident',
                                                  'party_type', 'diplay_sequence'))
    SuspectFormset = modelformset_factory(IncidentInvolvedParty,
                                          form=IncidentInvolvedPartyForm,
                                          exclude=['id', 'incident',
                                                   'party_type', 'display_sequence'])
    if request.method == 'POST':
        print(f"request.POST: {request.POST.getlist('report_datetime')}")
        (incident_data, victim_data,
         suspect_data, party_data) = parse_and_compile_incident_input_data(request.POST)
        incident_form = IncidentForm(incident_data)

        if incident_form.is_valid():
            incident = incident_form.save(party_data=party_data)
            return redirect(f"/{incident.id}")
        else:
            print(incident_form.errors)
    else:
        incident_form = IncidentForm()
        victim_form = IncidentInvolvedPartyForm(prefix="victims-0")
        suspect_form = IncidentInvolvedPartyForm(prefix="suspects-0")

    context = {'incident_form': incident_form,
               'victim_form': victim_form,
               'suspect_form': suspect_form}
    return render(request, "cases/create_incident.html", context=context)


@login_required
def incident_detail(request, incident_id):
    incident = get_object_or_404(Incident, pk=incident_id)
    if request.method == "POST":
        (incident_data, victim_data,
         suspect_data, party_data) = parse_and_compile_incident_input_data(request.POST)
        incident_form = IncidentForm(incident_data)

        incident_valid = incident_form.is_valid()
        victim_forms = []
        victim_idx = 0
        for victim in victim_data:
            prefix = f"victims-{victim_idx}"
            victim_forms.append(IncidentInvolvedPartyForm(victim,
                                                          prefix=prefix))
            victim_idx += 1

        suspect_forms = []
        suspect_idx = 0
        for suspect in suspect_data:
            prefix = f"suspects-{suspect_idx}"
            suspect_forms.append(IncidentInvolvedPartyForm(suspect,
                                                           prefix=prefix))
            suspect_idx += 1

        if incident_valid:
            incident = incident_form.save(party_data=party_data, instance=incident)
            return redirect(f"/{incident.id}")
        else:
            print(incident_form.errors)
    else:
        forms = populate_initial_incident_update_form_data(incident)
        logger.debug(f"Incident Data to be rendered:\n{forms['incident_data']}")
        incident_form = IncidentForm(data=forms['incident_data'])

        victim_forms = []
        victim_idx = 0
        for victim in forms['victim_data']:
            prefix = f"victims-{victim_idx}"
            victim_forms.append(IncidentInvolvedPartyForm(victim,
                                                          prefix=prefix))
            victim_idx += 1

        suspect_forms = []
        suspect_idx = 0
        for suspect in forms['suspect_data']:
            prefix = f"suspects-{suspect_idx}"
            suspect_forms.append(IncidentInvolvedPartyForm(suspect,
                                                           prefix=prefix))
            suspect_idx += 1

    return render(request, "cases/detail.html", context={'incident': incident,
                                                         'incident_form': incident_form,
                                                         'victim_forms': victim_forms,
                                                         'suspect_forms': suspect_forms})


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
