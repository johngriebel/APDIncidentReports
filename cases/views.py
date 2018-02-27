import logging
import json
from collections import namedtuple
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .forms import (IncidentForm,
                    IncidentInvolvedPartyForm,
                    IncidentSearchForm,
                    IncidentFileForm,
                    init_incident_detail_context)
from .models import Incident, IncidentFile
from .utils import (parse_and_compile_incident_input_data,
                    handle_files)
from .search import get_search_results
from .printing import IncidentReportPDFGenerator
logger = logging.getLogger('cases')


ContextFile = namedtuple("ContextFile", ["url", "display_name"])


@login_required
def index(request, *args, **kwargs):
    logger.debug(f"User: {request.user}")
    incidents = Incident.objects.all()
    display_fields = ["Incident Number", "Report Date & Time", "Reporting Officer"]
    context = {'incidents': incidents,
               'display_fields': display_fields}
    return render(request, "cases/index.html", context=context)


def _create_or_update_incident(incident, request) -> Incident:
    files = request.FILES.getlist('files')
    (incident_data, victim_data,
     suspect_data, party_data) = parse_and_compile_incident_input_data(request.POST)

    logger.debug(f"Incident data: {incident_data}")

    incident_form = IncidentForm(incident_data)

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

    victim_valid = all([vic.is_valid() for vic in victim_forms])
    sus_valid = all([sus.is_valid() for sus in suspect_forms])
    valid = incident_form.is_valid() and victim_valid and sus_valid

    if valid:
        incident = incident_form.save(party_data=party_data,
                                      instance=incident,
                                      files=files)
        return incident
    else:
        all_errors = []
        all_errors += [f.errors for f in victim_forms]
        all_errors += [f.errors for f in suspect_forms]
        all_errors += incident_form.errors

        logger.debug(all_errors)


@login_required
def create_incident(request, *args, **kwargs):
    incident = None
    if request.method == 'POST':
        incident = _create_or_update_incident(incident, request)
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
    if request.method == "POST":
        incident = _create_or_update_incident(incident, request)
        return redirect(f"/{incident.id}")
    else:
        context = init_incident_detail_context(incident=incident)
    return render(request, "cases/detail.html", context=context)


@login_required
def search(request, *args, **kwargs):
    display_fields = ["Incident Number", "Report Date & Time", "Reporting Officer"]
    if request.method == "POST":
        form = IncidentSearchForm(request.POST)
        results = get_search_results(request.POST)
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

