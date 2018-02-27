import logging
import json
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from address.models import _to_python
from .models import (Officer, Incident,
                     IncidentInvolvedParty,
                     IncidentFile)
from .serializers import (OfficerSerializer, IncidentSerializer,
                          IncidentInvolvedPartySerializer,
                          IncidentFileSerializer)
from .constants import VICTIM, SUSPECT
from rest_framework import viewsets
logger = logging.getLogger('cases')
User = get_user_model()


class OfficerViewSet(viewsets.ModelViewSet):
    queryset = Officer.objects.all()
    serializer_class = OfficerSerializer


class IncidentViewSet(viewsets.ModelViewSet):
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer

    def create(self, request, *args, **kwargs):
        logger.debug(request.data)
        dirty_data = {key: value for key, value in request.data.items()}
        logger.debug(f"Dirty data: {dirty_data}")
        for field in dirty_data:
            if "officer" in field or "supervisor" in field:
                dirty_data[field] = Officer.objects.get(id=dirty_data[field])
        dirty_data['offenses'] = json.loads(dirty_data['offenses'])
        dirty_data['location'] = json.loads(dirty_data['location'])
        serializer = self.get_serializer(data=request.data)
        # logger.debug(f"Type of data['offenses']: {type(json.loads(dirty_data['offenses']))}")
        logger.debug(f"Valid? {serializer.is_valid()}")
        logger.debug(serializer.validated_data)
        logger.debug(f"Errors: {serializer.errors}")
        serializer.create(validated_data=dirty_data)
        return Response(status=status.HTTP_201_CREATED,
                        data=serializer.data)


class VictimViewSet(viewsets.ModelViewSet):
    queryset = IncidentInvolvedParty.objects.filter(party_type=VICTIM)
    serializer_class = IncidentInvolvedPartySerializer


class SuspectViewSet(viewsets.ModelViewSet):
    queryset = IncidentInvolvedParty.objects.filter(party_type=SUSPECT)
    serializer_class = IncidentInvolvedPartySerializer


class IncidentFileViewSet(viewsets.ModelViewSet):
    queryset = IncidentFile.objects.all()
    serializer_class = IncidentFileSerializer
