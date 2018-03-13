import logging
import json
from collections import namedtuple
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .forms import (IncidentSearchForm,
                    IncidentFileForm)
from .models import Incident, IncidentFile
from .utils import handle_files
from .search import get_search_results
from .printing import IncidentReportPDFGenerator
logger = logging.getLogger('cases')


ContextFile = namedtuple("ContextFile", ["url", "display_name"])


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

