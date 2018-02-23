from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('create/', views.create_incident, name="create-incident"),
    path('<int:incident_id>/', views.incident_detail, name="detail"),
    path('search/', views.search, name="search"),
    path('print/<int:incident_id>/', views.print_report, name="print-report"),
    path('manage-files/<int:incident_id>/', views.manage_files, name="manage-files"),
    path('delete-files/<int:incident_id>/', views.delete_files, name="delete-files")
]
