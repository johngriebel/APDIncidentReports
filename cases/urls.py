from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('create/', views.create_incident, name="create-incident"),
    path('<int:incident_id>/', views.incident_detail, name="detail"),
    path('search/', views.search, name="search"),
]
