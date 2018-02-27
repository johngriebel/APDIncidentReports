from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views, rest_views


router = routers.SimpleRouter()
router.register("officers", rest_views.OfficerViewSet)
router.register("incidents", rest_views.IncidentViewSet)

incidents_router = routers.NestedSimpleRouter(router, "incidents", lookup="incidents")
incidents_router.register("victims", rest_views.VictimViewSet)
incidents_router.register("suspects", rest_views.SuspectViewSet)
incidents_router.register("files", rest_views.IncidentFileViewSet)

urlpatterns = [
    path('', views.index, name="index"),
    path('', include(router.urls)),
    path('', include(incidents_router.urls)),
    path('create/', views.create_incident, name="create-incident"),
    path('<int:incident_id>/', views.incident_detail, name="detail"),
    path('search/', views.search, name="search"),
    path('print/<int:incident_id>/', views.print_report, name="print-report"),
    path('manage-files/<int:incident_id>/', views.manage_files, name="manage-files"),
    path('delete-files/<int:incident_id>/', views.delete_files, name="delete-files"),
    path('upload-files/<int:incident_id>/', views.upload_file, name="upload-files")
]
