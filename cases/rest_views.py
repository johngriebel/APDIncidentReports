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
        dirty_data = {key: value for key, value in request.data.items()}
        for field in dirty_data:
            if "officer" in field or "supervisor" in field:
                dirty_data[field] = Officer.objects.get(id=dirty_data[field])
        dirty_data['offenses'] = json.loads(dirty_data['offenses'])
        dirty_data['location'] = json.loads(dirty_data['location'])

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        serializer.create(validated_data=dirty_data)
        return Response(status=status.HTTP_201_CREATED,
                        data=serializer.data)


class VictimViewSet(viewsets.ModelViewSet):
    queryset = IncidentInvolvedParty.objects.filter(party_type=VICTIM)
    serializer_class = IncidentInvolvedPartySerializer

    def get_queryset(self):
        qs = IncidentInvolvedParty.objects.filter(incident__id=self.kwargs.get('incidents_pk'),
                                                  party_type=VICTIM)
        return qs

    def create(self, request, *args, **kwargs):
        logger.debug((args, kwargs))
        dirty_data = {key: value for key, value in request.data.items()}
        dirty_data['incident'] = kwargs.get('incidents_pk')
        dirty_data['party_type'] = VICTIM

        for addr in ["home_address", "employer_address"]:
            address_attrs = dirty_data.get(addr)
            if address_attrs is not None:
                dirty_data[addr] = json.loads(dirty_data[addr])

        serializer = self.get_serializer(data=dirty_data)
        valid = serializer.is_valid()

        if not valid:
            logger.debug(serializer.errors)
            resp_status = status.HTTP_400_BAD_REQUEST
            resp_data = serializer.errors
        else:
            serializer.create(validated_data=dirty_data)
            resp_status = status.HTTP_201_CREATED
            resp_data = serializer.data

        return Response(status=resp_status,
                        data=resp_data)


class SuspectViewSet(viewsets.ModelViewSet):
    queryset = IncidentInvolvedParty.objects.filter(party_type=SUSPECT)
    serializer_class = IncidentInvolvedPartySerializer


class IncidentFileViewSet(viewsets.ModelViewSet):
    queryset = IncidentFile.objects.all()
    serializer_class = IncidentFileSerializer
