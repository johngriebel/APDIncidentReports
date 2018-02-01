from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import IncidentForm


# Create your views here.
def index(request, *args, **kwargs):
    context = {}
    return render(request, "cases/index.html", context=context)


def create_incident(request, *args, **kwargs):
    if request.method == 'POST':
        form = IncidentForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/thanks/')
    else:
        form = IncidentForm()

    context = {'form': form}
    return render(request, "cases/create_incident.html", context=context)
