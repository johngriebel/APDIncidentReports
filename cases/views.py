from django.shortcuts import render, redirect, get_object_or_404
from .forms import IncidentForm
from .models import Incident


# Create your views here.
def index(request, *args, **kwargs):
    context = {}
    return render(request, "cases/index.html", context=context)


def create_incident(request, *args, **kwargs):
    if request.method == 'POST':
        form = IncidentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(form)
    else:
        form = IncidentForm()

    context = {'form': form}
    return render(request, "cases/create_incident.html", context=context)


def incident_detail(request, incident_id):
    incident = get_object_or_404(Incident, pk=incident_id)
    return render(request, "cases/detail.html", context={'incident': incident})
