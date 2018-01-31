from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def index(request, *args, **kwargs):
    context = {}
    return render(request, "cases/index.html", context=context)
