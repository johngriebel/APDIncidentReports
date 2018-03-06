import logging
import json
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from .models import (Officer, Incident,
                     IncidentInvolvedParty,
                     IncidentFile)
from .serializers import (OfficerSerializer, IncidentSerializer,
                          IncidentInvolvedPartySerializer,
                          IncidentFileSerializer)
from .utils import create_incident_involved_party
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
                dirty_data[field] = dirty_data[field]['id']
        offense_json_list = json.loads(dirty_data['offenses'])
        dirty_data['offenses'] = [offense['id'] for offense in offense_json_list]
        dirty_data['location'] = json.loads(dirty_data['location'])

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        serializer.create(validated_data=dirty_data)
        return Response(status=status.HTTP_201_CREATED,
                        data=serializer.data)

    def partial_update(self, request, *args, **kwargs):
        incident = Incident.objects.get(id=kwargs['pk'])

        dirty_data = {key: value for key, value in request.data.items()}
        for field in dirty_data:
            if "officer" in field or "supervisor" in field:
                dirty_data[field] = dirty_data[field]['id']

        if dirty_data['damaged_amount'] is None:
            dirty_data['damaged_amount'] = 0

        if dirty_data['stolen_amount'] is None:
            dirty_data['stolen_amount'] = 0

        dirty_data['offenses'] = [offense['id'] for offense in dirty_data['offenses']]

        logger.debug(f"Dirty Data after cleaning: {dirty_data}")

        serializer = self.get_serializer(incident, data=dirty_data, partial=True)
        serializer.is_valid()
        if serializer.errors:
            resp_status = status.HTTP_400_BAD_REQUEST
            resp_data = serializer.errors
        else:
            serializer.save()
            resp_status = status.HTTP_200_OK
            resp_data = serializer.data

        return Response(status=resp_status,
                        data=resp_data)

class VictimViewSet(viewsets.ModelViewSet):
    queryset = IncidentInvolvedParty.objects.filter(party_type=VICTIM)
    serializer_class = IncidentInvolvedPartySerializer

    def get_queryset(self):
        qs = IncidentInvolvedParty.objects.filter(incident__id=self.kwargs.get('incidents_pk'),
                                                  party_type=VICTIM)
        return qs

    def create(self, request, *args, **kwargs):
        kwargs['party_type'] = VICTIM
        return create_incident_involved_party(request=request,
                                              serializer_class=self.get_serializer_class(),
                                              kwargs=kwargs)


class SuspectViewSet(viewsets.ModelViewSet):
    queryset = IncidentInvolvedParty.objects.filter(party_type=SUSPECT)
    serializer_class = IncidentInvolvedPartySerializer

    def get_queryset(self):
        qs = IncidentInvolvedParty.objects.filter(incident__id=self.kwargs.get('incidents_pk'),
                                                  party_type=SUSPECT)
        return qs

    def create(self, request, *args, **kwargs):
        kwargs['party_type'] = SUSPECT
        return create_incident_involved_party(request=request,
                                              serializer_class=self.get_serializer_class(),
                                              kwargs=kwargs)


class IncidentFileViewSet(viewsets.ModelViewSet):
    queryset = IncidentFile.objects.all()
    serializer_class = IncidentFileSerializer
