import logging

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import api_view
from rest_framework import viewsets

from cases.models import (Officer, Incident,
                          IncidentInvolvedParty,
                          IncidentFile, Offense)

from cases.serializers import (OfficerSerializer, IncidentSerializer,
                               IncidentInvolvedPartySerializer,
                               IncidentFileSerializer,
                               OffenseSerializer)

from cases.search import get_search_results

from cases.utils import (create_incident_involved_party,
                         convert_date_string_to_object)

from cases.constants import VICTIM, SUSPECT
from cases.printing import IncidentReportPDFGenerator

logger = logging.getLogger('cases')
User = get_user_model()


class OfficerViewSet(viewsets.ModelViewSet):
    queryset = Officer.objects.all()
    serializer_class = OfficerSerializer


class OffenseViewSet(viewsets.ModelViewSet):
    queryset = Offense.objects.all()
    serializer_class = OffenseSerializer


class IncidentViewSet(viewsets.ModelViewSet):
    queryset = Incident.objects.all().order_by("-report_datetime")
    serializer_class = IncidentSerializer

    def create(self, request, *args, **kwargs):
        logger.debug(f"Request.data: {request.data}")
        dirty_data = {key: value for key, value in request.data.items()}
        logger.debug(f"Dirty data: {dirty_data}")
        for field in dirty_data:
            if "officer" in field or "supervisor" in field:
                dirty_data[field] = dirty_data[field]['officer_number']
            if "datetime" in field:
                dirty_data[field] = convert_date_string_to_object(f"{dirty_data[field]['date']} "
                                                                  f"{dirty_data[field]['time']}")
        # dirty_data['offenses'] = [offense['id'] for offense in dirty_data['offenses']]
        if "id" in dirty_data:
            dirty_data.pop("id")
        logger.debug(f"After cleaning: {dirty_data['location']}")
        serializer = self.get_serializer(data=dirty_data)
        serializer.is_valid()
        incident = serializer.create(validated_data=dirty_data)
        return Response(status=status.HTTP_201_CREATED,
                        data=self.get_serializer_class()(instance=incident).data)

    def partial_update(self, request, *args, **kwargs):
        incident = Incident.objects.get(id=kwargs['pk'])
        logger.debug(f"Request.data: {request.data}")
        dirty_data = {key: value for key, value in request.data.items()}
        for field in dirty_data:
            if "officer" in field or "supervisor" in field:
                dirty_data[field] = dirty_data[field]['officer_number']
            if "datetime" in field:
                logger.debug(f"dirty_data[{field}]: {dirty_data[field]}")
                dirty_data[field] = convert_date_string_to_object(f"{dirty_data[field]['date']} "
                                                                  f"{dirty_data[field]['time']}")

        if "damaged_amount" in dirty_data and dirty_data['damaged_amount'] is None:
            dirty_data['damaged_amount'] = 0

        if "stolen_amount" in dirty_data and dirty_data['stolen_amount'] is None:
            dirty_data['stolen_amount'] = 0

        # dirty_data['offenses'] = [offense['id'] for offense in dirty_data['offenses']]
        if "offenses" in dirty_data and isinstance(dirty_data['offenses'], dict):
            offenses = dirty_data.pop("offenses")
            dirty_data['offenses'] = [offenses['id']]

        serializer = self.get_serializer(incident, data=dirty_data, partial=True)
        if serializer.is_valid():
            serializer.update(instance=incident, validated_data=dirty_data)
            resp_status = status.HTTP_200_OK
            resp_data = serializer.data
        else:
            logger.debug(f"Data: {dirty_data}")
            resp_status = status.HTTP_400_BAD_REQUEST
            resp_data = serializer.errors
            logger.debug(f"Errors: {resp_data}")

        return Response(status=resp_status,
                        data=resp_data)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


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

    def update(self, request, *args, **kwargs):
        if request.method == "PUT":
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            return super(VictimViewSet, self).update(request,
                                                     *args, **kwargs)


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

    def update(self, request, *args, **kwargs):
        if request.method == "PUT":
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            return super(SuspectViewSet, self).update(request,
                                                      *args, **kwargs)


class IncidentFileViewSet(viewsets.ModelViewSet):
    queryset = IncidentFile.objects.all()
    serializer_class = IncidentFileSerializer
    parser_classes = (MultiPartParser,)

    def create(self, request, *args, **kwargs):
        incident = Incident.objects.get(pk=kwargs.get('incidents_pk'))
        created_files = []
        for upload in request.FILES.getlist('files'):
            incident_file = IncidentFile(incident=incident,
                                         file=upload)
            incident_file.save()
            logger.info(f"Wrote file upload to {incident_file.file.path}")
            created_files.append(incident_file)
        data = self.get_serializer(created_files, many=True).data
        return Response(status=status.HTTP_201_CREATED,
                        data=data)


@api_view(["POST"])
def search(request, *args, **kwargs):
    results = get_search_results(params=request.data)
    serializer = IncidentSerializer(results, many=True)

    return Response(status=status.HTTP_201_CREATED,
                    data=serializer.data)


@api_view(['GET'])
def print_report(request, *args, **kwargs):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="somefilename.pdf"'

    pdf_generator = IncidentReportPDFGenerator(response, kwargs.get('incident_id'))
    pdf_generator.generate()
    return response


def jwt_response_payload_handler(token, user=None, request=None):
    logger.debug(f"Token: {token}")
    logger.debug(f"User: {user}")
    officer = Officer.objects.get(user=user)
    serialized = OfficerSerializer(officer)
    return {'token': token,
            'officer': serialized.data}
