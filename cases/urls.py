from django.urls import path, include
from rest_framework_nested import routers
from . import views


router = routers.SimpleRouter()
router.register("officers", views.OfficerViewSet)
router.register("incidents", views.IncidentViewSet)
router.register("offenses", views.OffenseViewSet)

incidents_router = routers.NestedSimpleRouter(router, "incidents",
                                              lookup="incidents")
incidents_router.register("victims", views.VictimViewSet,
                          base_name="victim")
incidents_router.register("suspects", views.SuspectViewSet,
                          base_name="suspect")
incidents_router.register("files", views.IncidentFileViewSet,
                          base_name="file")

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/', include(incidents_router.urls)),
    path('api/incidents/print/<int:incident_id>/', views.print_report, name="print-report"),
]
