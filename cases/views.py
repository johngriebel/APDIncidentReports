import logging
import json
from collections import namedtuple
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .forms import (IncidentForm,
                    IncidentInvolvedPartyForm,
                    populate_initial_incident_update_form_data,
                    IncidentSearchForm,
                    IncidentFileForm)
from .models import Incident, IncidentFile
from .utils import (parse_and_compile_incident_input_data,
                    handle_files)
from .search import get_search_results
from .printing import IncidentReportPDFGenerator
logger = logging.getLogger('cases')


ContextFile = namedtuple("ContextFile", ["url", "display_name"])


@login_required
def index(request, *args, **kwargs):
    incidents = Incident.objects.all()
    display_fields = ["Incident Number", "Report Date & Time", "Reporting Officer"]
    context = {'incidents': incidents,
               'display_fields': display_fields}
    return render(request, "cases/index.html", context=context)


@login_required
def create_incident(request, *args, **kwargs):
    if request.method == 'POST':
        (incident_data, victim_data,
         suspect_data, party_data) = parse_and_compile_incident_input_data(request.POST)
        incident_form = IncidentForm(incident_data)
        victim_form = IncidentInvolvedPartyForm(victim_data[0])
        suspect_form = IncidentInvolvedPartyForm(suspect_data[0])

        isvalid = (incident_form.is_valid()
                   and victim_form.is_valid()
                   and suspect_form.is_valid())

        if isvalid:
            incident = incident_form.save(party_data=party_data)
            return redirect(f"/{incident.id}")
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
    logger.debug(request.method)
    if request.method == "POST":
        files = request.FILES.getlist('files')
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
            incident = incident_form.save(party_data=party_data,
                                          instance=incident,
                                          files=files)
            return redirect(f"/{incident.id}")
        else:
            print(incident_form.errors)
    else:
        forms = populate_initial_incident_update_form_data(incident)
        incident_form = IncidentForm(data=forms['incident_data'])
        files = forms['existing_files']

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
                                                         'suspect_forms': suspect_forms,
                                                         'existing_files': files})


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


@login_required
def manage_files(request, *args, **kwargs):
    incident = Incident.objects.get(id=kwargs.get("incident_id"))
    files = IncidentFile.objects.filter(incident=incident)

    context_files = [ContextFile(url=inc_file.file.url,
                                 display_name=inc_file.display_name)
                     for inc_file in files]
    logger.debug(f"Context Files:\n {context_files}")
    form = IncidentFileForm()
    context = {'incident': incident,
               'files': files,
               'form': form}
    return render(request, "cases/manage_files.html", context=context)


@login_required
def delete_files(request, *args, **kwargs):
    incident_file_id_list = json.loads(request.body, encoding="utf-8")
    logger.debug(f"IncidentFiles to delete: {incident_file_id_list}")
    try:
        incident_files = IncidentFile.objects.filter(id__in=incident_file_id_list)
        for f in incident_files:
            f.file.delete()
        result = incident_files.delete()
        logger.debug(f"Successfully deleted incident files: {result}")
        success = True
        message = result
        status = 200
    except Exception as e:
        logger.exception(e)
        success = False
        message = str(e)
        status = 500
    data = {'success': success,
            'message': message}
    return JsonResponse(status=status,
                        data=data)


@login_required
def upload_file(request, *args, **kwargs):
    incident = Incident.objects.get(id=kwargs.get("incident_id"))
    existing_files = IncidentFile.objects.filter(incident=incident)
    if request.method == "POST":
        form = IncidentFileForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('files')
            handle_files(incident=incident,
                         files=files)
            return redirect("manage-files", incident_id=incident.id)
    else:
        form = IncidentFileForm()
    context = {'incident': incident,
               'files': existing_files,
               'form': form}
    return render(request, "cases/manage_files.html", context=context)

