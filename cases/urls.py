from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views, rest_views


router = routers.SimpleRouter()
router.register("officers", rest_views.OfficerViewSet)
router.register("incidents", rest_views.IncidentViewSet)
router.register("offenses", rest_views.OffenseViewSet)

incidents_router = routers.NestedSimpleRouter(router, "incidents",
                                              lookup="incidents")
incidents_router.register("victims", rest_views.VictimViewSet,
                          base_name="victim")
incidents_router.register("suspects", rest_views.SuspectViewSet,
                          base_name="suspect")
incidents_router.register("files", rest_views.IncidentFileViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/', include(incidents_router.urls)),
    path('search/', rest_views.search, name="search"),
    path('api/incidents/print/<int:incident_id>/', rest_views.print_report, name="print-report"),
]
